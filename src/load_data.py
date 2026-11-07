
import pandas as pd
from pathlib import Path


# 1. PROJECT PATHS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


# 2. EXPECTED ROW COUNTS

EXPECTED_ROW_COUNTS = {
    "starrydata_papers.csv": 56_495,
    "starrydata_samples.csv": 106_331,
    "starrydata_curves.csv": 237_313
}


# 3. GENERIC CSV LOADER

def load_starrydata_file(
    file_path: Path,
    expected_columns: list
) -> pd.DataFrame:
    """
    Loads a Starrydata CSV, validates its schema,
    and checks its expected row count.
    """

    # Check file existence
    if not file_path.exists():
        raise FileNotFoundError(
            f"Cannot find data file: {file_path}. "
            "Please check the data/raw/ directory."
        )

    try:
        df = pd.read_csv(
            file_path,
            dtype={
                "SID": "string",
                "sample_id": "string",
                "figure_id": "string"
            },
            low_memory=False,
            skip_blank_lines=True
        )

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            f"CSV file is empty: {file_path}"
        ) from error

    except pd.errors.ParserError as error:
        raise ValueError(
            f"Unable to parse {file_path.name}: {error}"
        ) from error

    # Validate mandatory columns
    missing_cols = [
        col for col in expected_columns
        if col not in df.columns
    ]

    if missing_cols:
        raise ValueError(
            f"Schema mismatch in {file_path.name}. "
            f"Missing columns: {missing_cols}"
        )

    # Validate expected row count
    expected_rows = EXPECTED_ROW_COUNTS[file_path.name]
    actual_rows = len(df)

    if actual_rows != expected_rows:
        raise ValueError(
            f"Row count mismatch in {file_path.name}. "
            f"Expected: {expected_rows:,}, "
            f"Actual: {actual_rows:,}"
        )

    # Remove unwanted whitespace from identifiers
    for column in ["SID", "sample_id", "figure_id"]:
        if column in df.columns:
            df[column] = df[column].str.strip()

    print(
        f"PASS: {file_path.name} loaded "
        f"({actual_rows:,} rows, {len(df.columns)} columns)"
    )

    return df



# 4. PAPERS DATASET


def get_papers_data() -> pd.DataFrame:
    """Loads and validates the Papers dataset."""

    path = RAW_DIR / "starrydata_papers.csv"

    mandatory_cols = [
        "SID",
        "DOI",
        "issued"
    ]

    return load_starrydata_file(path, mandatory_cols)



# 5. SAMPLES DATASET

def get_samples_data() -> pd.DataFrame:
    """Loads and validates the Samples dataset."""

    path = RAW_DIR / "starrydata_samples.csv"

    mandatory_cols = [
        "SID",
        "sample_id"
    ]

    return load_starrydata_file(path, mandatory_cols)


# 6. CURVES DATASET

def get_curves_data() -> pd.DataFrame:
    """Loads and validates the Curves dataset."""

    path = RAW_DIR / "starrydata_curves.csv"

    mandatory_cols = [
        "figure_id",
        "sample_id",
        "x",
        "y"
    ]

    return load_starrydata_file(path, mandatory_cols)


# 7. MAIN EXECUTION


def main():

    print("\n" + "=" * 55)
    print("STARRYDATA DATA INGESTION PIPELINE")
    print("=" * 55)

    # Fail-fast: any loading or validation error stops execution.
    papers_df = get_papers_data()
    samples_df = get_samples_data()
    curves_df = get_curves_data()

    datasets = {
        "Papers": papers_df,
        "Samples": samples_df,
        "Curves": curves_df
    }

    print("\nALL DATASETS LOADED SUCCESSFULLY")

    print("\nDATASET SUMMARY")
    print("-" * 55)

    for name, df in datasets.items():
        print(
            f"{name:10} | "
            f"Rows: {len(df):>8,} | "
            f"Columns: {len(df.columns):>3}"
        )

    print("\nIDENTIFIER DATA TYPES")
    print("-" * 55)

    for name, df in datasets.items():
        for column in ["SID", "sample_id", "figure_id"]:
            if column in df.columns:
                print(
                    f"{name}.{column}: "
                    f"{df[column].dtype}"
                )

    print("\n" + "=" * 55)
    print("DELIVERABLE COMPLETE - ALL CHECKS PASSED")
    print("=" * 55)

    return papers_df, samples_df, curves_df



# 8. RUN SCRIPT

if __name__ == "__main__":
    papers, samples, curves = main()
