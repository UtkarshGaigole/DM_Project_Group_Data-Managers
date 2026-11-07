
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
CURVES_INPUT = RAW_DIR / "starrydata_curves.csv"

SAMPLES_OUTPUT = OUTPUT_DIR / "starrydata_samples_cleaned.csv"
PAPERS_OUTPUT = OUTPUT_DIR / "starrydata_papers_cleaned.csv"
CURVES_OUTPUT = OUTPUT_DIR / "starrydata_curves_cleaned.csv"

EXPECTED_SAMPLES_ROWS = 106331
EXPECTED_PAPERS_ROWS = 56495
EXPECTED_CURVES_ROWS = 237313

EXPECTED_PRECISION_COUNTS = {
    "YMD": 25192,
    "YM": 24570,
    "Y": 6526,
    "Unknown": 207
}

EXPECTED_TIMESTAMP_RANGES = {
    "papers.created_at": (
        "2018-01-25 04:56:56",
        "2026-09-18 01:43:28"
    ),
    "samples.created_at": (
        "2017-09-01 09:19:39",
        "2026-09-30 08:25:24"
    ),
    "samples.updated_at": (
        "2017-09-01 09:19:39",
        "2026-09-30 08:34:52"
    ),
    "curves.created_at": (
        "2017-09-01 09:19:39",
        "2026-09-30 08:33:51"
    ),
    "curves.updated_at": (
        "2017-09-01 09:19:39",
        "2026-09-30 08:33:55"
    )
}


def clean_timestamp_column(df, column, dataset):
    """
    Reproduce Tableau's timestamp conversion.

    Tableau:
    1. Extract characters 5-24.
    2. Parse using MMM dd yyyy HH:mm:ss.
    3. Subtract 9 hours to convert JST to UTC.
    4. Create a new _utc column.
    5. Remove the original timestamp column.
    """

    if column not in df.columns:
        raise KeyError(
            f"Required timestamp column '{column}' is missing."
        )

    output_column = f"{column}_utc"
    range_key = f"{dataset}.{column}"

    print(f"\nCleaning timestamp: {range_key}")

    extracted = df[column].astype("string").str.slice(4, 24)

    parsed = pd.to_datetime(
        extracted,
        format="%b %d %Y %H:%M:%S",
        errors="coerce"
    )

    utc_values = parsed - pd.Timedelta(hours=9)

    null_count = utc_values.isna().sum()

    if null_count > 0:
        raise ValueError(
            f"{range_key}: {null_count} timestamps could not be parsed."
        )

    actual_min = utc_values.min().strftime("%Y-%m-%d %H:%M:%S")
    actual_max = utc_values.max().strftime("%Y-%m-%d %H:%M:%S")

    expected_min, expected_max = EXPECTED_TIMESTAMP_RANGES[range_key]

    if actual_min != expected_min:
        raise ValueError(
            f"{range_key}: minimum timestamp mismatch. "
            f"Expected {expected_min}, got {actual_min}."
        )

    if actual_max != expected_max:
        raise ValueError(
            f"{range_key}: maximum timestamp mismatch. "
            f"Expected {expected_max}, got {actual_max}."
        )

    df[output_column] = utc_values.dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    df = df.drop(columns=[column])

    print(
        f"PASS: {output_column} | "
        f"Nulls: {null_count} | "
        f"Min: {actual_min} | "
        f"Max: {actual_max}"
    )

    return df


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
    """Load Samples, clean timestamps and flatten sample_info."""

    print("\nLoading Samples dataset...")

    df = pd.read_csv(
        SAMPLES_INPUT,
        low_memory=False,
        skip_blank_lines=True,
        dtype={
            "SID": "string",
            "sample_id": "string"
        }
    )

    print(f"Original Samples shape: {df.shape}")

    if len(df) != EXPECTED_SAMPLES_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_SAMPLES_ROWS:,} Samples rows, "
            f"got {len(df):,}."
        )

    if "sample_info" not in df.columns:
        raise KeyError("Required column 'sample_info' is missing.")

    df = clean_timestamp_column(
        df, "created_at", "samples"
    )

    df = clean_timestamp_column(
        df, "updated_at", "samples"
    )

    print("\nParsing and flattening sample_info...")

    flattened_data = df["sample_info"].apply(parse_sample_info)

    flattened_df = pd.DataFrame(
        flattened_data.tolist(),
        index=df.index
    )

    if "sample_info" in flattened_df.columns:
        df = df.rename(
            columns={"sample_info": "sample_info_raw"}
        )

    duplicate_columns = set(df.columns).intersection(
        flattened_df.columns
    )

    if duplicate_columns:
        raise ValueError(
            "Flattened JSON produced columns that already exist: "
            f"{sorted(duplicate_columns)}"
        )

    cleaned_df = pd.concat(
        [df, flattened_df],
        axis=1
    )

    print(f"Cleaned Samples shape: {cleaned_df.shape}")
    print(f"New flattened columns: {len(flattened_df.columns)}")

    if len(cleaned_df) != EXPECTED_SAMPLES_ROWS:
        raise ValueError(
            "Samples row count changed during cleaning."
        )

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

    df["issued_cleaned"] = df["issued"].apply(
        extract_issued_date
    )

    parts = df["issued_cleaned"].str.split(
        ",",
        n=2,
        expand=True
    )

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

    df = df.drop(
        columns=["issued_cleaned", "issued"]
    )

    return df


def clean_papers_data():
    """Load Papers and reproduce Tableau cleaning."""

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
            f"got {len(papers):,}."
        )

    papers = clean_timestamp_column(
        papers, "created_at", "papers"
    )

    cleaned_papers = clean_publication_precision(papers)

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
                f"expected {expected:,}, got {actual:,}."
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

    print(f"PASS: Papers row count = {len(cleaned_papers):,}")
    print(f"Saved Papers output: {PAPERS_OUTPUT}")

    return cleaned_papers


def clean_curves_data():
    """Load Curves and reproduce Tableau timestamp cleaning."""

    print("\nLoading Curves dataset...")

    curves = pd.read_csv(
        CURVES_INPUT,
        low_memory=False,
        skip_blank_lines=True,
        dtype={
            "SID": "string",
            "sample_id": "string",
            "figure_id": "string"
        }
    )

    print(f"Original Curves shape: {curves.shape}")

    if len(curves) != EXPECTED_CURVES_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_CURVES_ROWS:,} Curves rows, "
            f"got {len(curves):,}."
        )

    curves = clean_timestamp_column(
        curves, "created_at", "curves"
    )

    curves = clean_timestamp_column(
        curves, "updated_at", "curves"
    )

    curves.to_csv(
        CURVES_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(f"PASS: Curves row count = {len(curves):,}")
    print(f"Saved Curves output: {CURVES_OUTPUT}")

    return curves


def main():

    print("STARRYDATA CLEANING PIPELINE")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned_samples = clean_samples_data()
    cleaned_papers = clean_papers_data()
    cleaned_curves = clean_curves_data()

    print("\n========== CLEANING COMPLETE ==========")

    print(
        f"Samples: {len(cleaned_samples):,} rows, "
        f"{len(cleaned_samples.columns)} columns"
    )

    print(
        f"Papers: {len(cleaned_papers):,} rows, "
        f"{len(cleaned_papers.columns)} columns"
    )

    print(
        f"Curves: {len(cleaned_curves):,} rows, "
        f"{len(cleaned_curves.columns)} columns"
    )

    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
