
import json
import re
import warnings
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

SAMPLES_INPUT = RAW_DIR / "starrydata_samples.csv"
PAPERS_INPUT = RAW_DIR / "starrydata_papers.csv"

SAMPLES_OUTPUT = OUTPUT_DIR / "starrydata_samples_cleaned.csv"
PAPERS_OUTPUT = OUTPUT_DIR / "starrydata_papers_cleaned.csv"

EXPECTED_SAMPLES_ROWS = 106331
EXPECTED_PAPERS_ROWS = 56495

EXPECTED_PRECISION_COUNTS = {
    
    "YMD": 25192,
    "YM": 24570,
    "Y": 6526,
    "Unknown": 207

}


def clean_column_name(name):
    """
    Convert JSON property names into clean column names.

    Example:
    ' Measurement temperature ' -> 'Measurement_temperature'
    """

    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return name


def flatten_json(data, parent_key=""):
    """
    Recursively flatten a nested JSON dictionary.

    Example:
    {
        "MaterialFamily": {
            "category": "Bi2Te3",
            "comment": ""
        }
    }

    Becomes:
    {
        "MaterialFamily_category": "Bi2Te3",
        "MaterialFamily_comment": ""
    }
    """

    flattened = {}

    if not isinstance(data, dict):
        return flattened

    for key, value in data.items():

        new_key = (
            f"{parent_key}_{key}"
            if parent_key
            else key
        )

        if isinstance(value, dict):

            nested_data = flatten_json(value, new_key)
            flattened.update(nested_data)

        else:

            column_name = clean_column_name(new_key)
            flattened[column_name] = value

    return flattened


def parse_sample_info(json_string):
    """
    Parse sample_info JSON and return flattened data.

    Handles:
    - Empty values
    - Empty JSON objects
    - Invalid JSON
    - Nested dictionaries
    """

    if pd.isna(json_string) or not str(json_string).strip():
        return {}

    try:

        parsed_json = json.loads(json_string)

        return flatten_json(parsed_json)

    except (json.JSONDecodeError, TypeError) as error:

        warnings.warn(f"Invalid JSON encountered: {error}")

        return {}


def clean_samples_data():
    """Load the complete Samples dataset and flatten sample_info."""

    print("\nLoading Samples dataset...")

    df = pd.read_csv(
        SAMPLES_INPUT,
        low_memory=False,
        skip_blank_lines=True,
        dtype={"SID": "string", "sample_id": "string"}
    )

    print(f"Original Samples shape: {df.shape}")

    if len(df) != EXPECTED_SAMPLES_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_SAMPLES_ROWS:,} Samples rows, "
            f"got {len(df):,}"
        )

    if "sample_info" not in df.columns:
        raise KeyError("Required column 'sample_info' is missing.")

    print("Parsing and flattening sample_info...")

    flattened_data = df["sample_info"].apply(parse_sample_info)

    flattened_df = pd.DataFrame(
        flattened_data.tolist(),
        index=df.index
    )

    # Preserve the original JSON column separately.
    if "sample_info" in flattened_df.columns:
        df = df.rename(
            columns={"sample_info": "sample_info_raw"}
        )
    
    # Check for any remaining column-name collisions.
    duplicate_columns = set(df.columns).intersection(flattened_df.columns)
    
    if duplicate_columns:
        raise ValueError(
            "Flattened JSON produced columns that already exist: "
            f"{sorted(duplicate_columns)}"
        )
    
    # Combine original data with flattened JSON properties.
    cleaned_df = pd.concat(
        [df, flattened_df],
        axis=1
    )

    print(f"Cleaned Samples shape: {cleaned_df.shape}")
    print(f"New flattened columns: {len(flattened_df.columns)}")

    cleaned_df.to_csv(
        SAMPLES_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(f"PASS: Samples row count = {len(cleaned_df):,}")
    print(f"Saved Samples output: {SAMPLES_OUTPUT}")

    return cleaned_df


def extract_issued_date(value):
    """
    Reproduce Tableau's REGEXP_EXTRACT calculation:

    REGEXP_EXTRACT([issued], '\\[\\[(.*?)\\]\\]')
    """

    if pd.isna(value):
        return None

    match = re.search(r"\[\[(.*?)\]\]", str(value))

    if match:
        return match.group(1)

    return None


def clean_publication_precision(papers):
    """
    Reproduce Tableau's Extract Publication Precision step.

    Creates:
    - issued_year
    - issued_month
    - issued_day
    - issued_precision

    Removes:
    - issued_cleaned
    - issued
    """

    df = papers.copy()

    if "issued" not in df.columns:
        raise KeyError("Required column 'issued' is missing.")

    print("Extracting publication dates...")

    # Extract the content inside [[...]] using Tableau's exact regex.
    df["issued_cleaned"] = df["issued"].apply(extract_issued_date)

    # Split the extracted date into year, month and day.
    parts = df["issued_cleaned"].str.split(",", n=2, expand=True)

    for index, column in enumerate(
        ["issued_year", "issued_month", "issued_day"]
    ):

        if index < parts.shape[1]:

            values = parts[index].str.strip()

            df[column] = pd.to_numeric(
                values,
                errors="coerce"
            ).astype("Int64")

        else:

            df[column] = pd.Series(
                pd.NA,
                index=df.index,
                dtype="Int64"
            )

    # Reproduce Tableau's issued_precision calculation.
    df["issued_precision"] = "Unknown"

    df.loc[
        df["issued_year"].notna(),
        "issued_precision"
    ] = "Y"

    df.loc[
        df["issued_month"].notna(),
        "issued_precision"
    ] = "YM"

    df.loc[
        df["issued_day"].notna(),
        "issued_precision"
    ] = "YMD"

    # Remove the temporary and original fields as Tableau does.
    df = df.drop(
        columns=["issued_cleaned", "issued"]
    )

    return df


def clean_papers_data():
    """Load Papers and reproduce Tableau publication precision cleaning."""

    print("\nLoading Papers dataset...")

    papers = pd.read_csv(
        PAPERS_INPUT,
        low_memory=False,
        skip_blank_lines=True,
        dtype={"SID": "string"}
    )

    print(f"Original Papers shape: {papers.shape}")

    if len(papers) != EXPECTED_PAPERS_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_PAPERS_ROWS:,} Papers rows, "
            f"got {len(papers):,}"
        )

    cleaned_papers = clean_publication_precision(papers)
    
    
    
    
    
    
    
    
    unknown_mask = cleaned_papers["issued_precision"].eq("Unknown")
    
    unknown_details = papers.loc[
        unknown_mask,
        ["SID", "issued"]
    ]
    
    print(unknown_details.to_string(index=False))
    print(f"\nTotal Unknown records: {len(unknown_details)}")
    
    
    
    
    missing_year_mask = cleaned_papers["issued_year"].isna()
    
    missing_year_details = papers.loc[
        missing_year_mask,
        ["SID", "issued"]
    ]
    
    print(missing_year_details.to_string(index=False))
    print(f"\nTotal records with missing year: {len(missing_year_details)}")
    




    # Validate the number of records in each precision category.
    actual_counts = (
        cleaned_papers["issued_precision"]
        .value_counts()
        .to_dict()
    )

    print("\nPublication precision validation:")

    for precision, expected in EXPECTED_PRECISION_COUNTS.items():

        actual = actual_counts.get(precision, 0)

        if actual != expected:
            raise ValueError(
                f"Precision mismatch for {precision}: "
                f"expected {expected:,}, got {actual:,}"
            )

        print(f"PASS: {precision} = {actual:,}")

    if len(cleaned_papers) != EXPECTED_PAPERS_ROWS:
        raise ValueError(
            "Papers row count changed during publication cleaning."
        )

    cleaned_papers.to_csv(
        PAPERS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(f"\nPASS: Papers row count = {len(cleaned_papers):,}")
    print(f"Saved Papers output: {PAPERS_OUTPUT}")

    return cleaned_papers


def main():

    print("STARRYDATA CLEANING PIPELINE")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Clean the complete Samples dataset.
    cleaned_samples = clean_samples_data()

    # Clean publication precision in the complete Papers dataset.
    cleaned_papers = clean_papers_data()

    print("\n========== CLEANING COMPLETE ==========")

    print(
        f"Samples: {len(cleaned_samples):,} rows, "
        f"{len(cleaned_samples.columns)} columns"
    )

    print(
        f"Papers: {len(cleaned_papers):,} rows, "
        f"{len(cleaned_papers.columns)} columns"
    )

    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
