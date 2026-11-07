
import json
from pathlib import Path

import pandas as pd

from load_data import (
    get_papers_data,
    get_samples_data,
    get_curves_data
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"

CURVE_POINTS_INPUT = INTERIM_DIR / "curve_points.csv"
TIER2_CURVES_INPUT = INTERIM_DIR / "starrydata_curves_tier2.csv"
TIER2_POINTS_INPUT = INTERIM_DIR / "starrydata_tier2_curve_points.csv"

EXPECTED_PAPERS_ROWS = 56_495
EXPECTED_SAMPLES_ROWS = 106_331
EXPECTED_CURVES_ROWS = 237_313

EXPECTED_RAW_CURVE_POINTS = 4_839_779
EXPECTED_EMPTY_CURVES = 3_952

EXPECTED_TIER2_CURVES = 136_679
EXPECTED_TIER2_POINTS = 2_337_212
EXPECTED_TIER2_CURVES_WITHOUT_POINTS = 2_140

EXPECTED_ORPHAN_SIDS = {"8534", "8535", "9026"}


def validate_schema(df, expected_columns, file_name):
    """Check whether all mandatory columns exist."""

    missing_columns = [
        column for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Schema validation failed for {file_name}. "
            f"Missing columns: {missing_columns}"
        )

    print(f"PASS: Schema validation - {file_name}")
    return df


def validate_row_count(df, expected_rows, dataset_name):
    """Validate the expected number of records."""

    actual_rows = len(df)

    if actual_rows != expected_rows:
        raise ValueError(
            f"{dataset_name}: expected {expected_rows:,} rows, "
            f"got {actual_rows:,}."
        )

    print(f"PASS: {dataset_name} row count = {actual_rows:,}")


def validate_not_null(df, columns, dataset_name):
    """Check mandatory fields for missing values."""

    for column in columns:
        null_count = df[column].isna().sum()

        if null_count:
            raise ValueError(
                f"{dataset_name}.{column} contains "
                f"{null_count:,} missing values."
            )

    print(f"PASS: Required fields are populated - {dataset_name}")


def validate_unique_key(df, columns, dataset_name):
    """Check whether a primary or composite key is unique."""

    duplicate_count = df.duplicated(subset=columns).sum()

    if duplicate_count:
        raise ValueError(
            f"{dataset_name}: found {duplicate_count:,} "
            f"duplicate records for key {columns}."
        )

    print(f"PASS: Unique key - {dataset_name}: {columns}")


def validate_identifier_types(df):
    """Keep identifier columns in pandas string format."""

    for column in ["SID", "sample_id", "figure_id"]:
        if column in df.columns:
            df[column] = df[column].astype("string")

    return df


def validate_curve_references(curves, samples, papers):
    """Check curve references and identify orphan SIDs."""

    sample_ids = set(samples["sample_id"].dropna())
    curve_sample_ids = set(curves["sample_id"].dropna())

    unmatched_sample_ids = curve_sample_ids - sample_ids

    if unmatched_sample_ids:
        print(
            "WARNING: Curve sample IDs without matching Samples: "
            f"{len(unmatched_sample_ids):,}"
        )
    else:
        print("PASS: All curve sample IDs reference Samples.")

    paper_sids = set(papers["SID"].dropna())
    curve_sids = set(curves["SID"].dropna())

    orphan_sids = curve_sids - paper_sids

    if orphan_sids != EXPECTED_ORPHAN_SIDS:
        raise ValueError(
            f"Orphan SID mismatch. "
            f"Expected {sorted(EXPECTED_ORPHAN_SIDS)}, "
            f"got {sorted(orphan_sids)}."
        )

    orphan_rows = curves["SID"].isin(orphan_sids).sum()

    print(f"PASS: Orphan SIDs identified = {sorted(orphan_sids)}")
    print(f"Orphan curve records retained = {orphan_rows:,}")


def parse_curve_array(value, column_name, row_index):
    """Parse and validate an x or y JSON array."""

    if pd.isna(value):
        raise ValueError(
            f"Missing {column_name} array at curve row {row_index}."
        )

    try:
        parsed = json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(
            f"Invalid {column_name} JSON at curve row {row_index}: {error}"
        ) from error

    if not isinstance(parsed, list):
        raise ValueError(
            f"{column_name} must contain a JSON array "
            f"at curve row {row_index}."
        )

    return parsed


def validate_curve_arrays(curves):
    """Validate x/y arrays and independently calculate point counts."""

    total_points = 0
    empty_curves = 0

    for row_index, row in curves[["x", "y"]].iterrows():
        x_values = parse_curve_array(row["x"], "x", row_index)
        y_values = parse_curve_array(row["y"], "y", row_index)

        if len(x_values) != len(y_values):
            raise ValueError(
                f"x/y length mismatch at curve row {row_index}: "
                f"x={len(x_values)}, y={len(y_values)}."
            )

        if not x_values and not y_values:
            empty_curves += 1

        total_points += len(x_values)

    if total_points != EXPECTED_RAW_CURVE_POINTS:
        raise ValueError(
            f"Expected {EXPECTED_RAW_CURVE_POINTS:,} raw points, "
            f"got {total_points:,}."
        )

    if empty_curves != EXPECTED_EMPTY_CURVES:
        raise ValueError(
            f"Expected {EXPECTED_EMPTY_CURVES:,} empty curves, "
            f"got {empty_curves:,}."
        )

    print("PASS: All x/y arrays have matching lengths.")
    print(f"PASS: Total raw measurement points = {total_points:,}")
    print(f"PASS: Empty curves = {empty_curves:,}")


def validate_curve_points(curves):
    """Validate generated raw curve-point data."""

    if not CURVE_POINTS_INPUT.exists():
        raise FileNotFoundError(
            f"Curve-points file not found: {CURVE_POINTS_INPUT}"
        )

    print("\nValidating generated curve points...")

    point_columns = [
        "figure_id",
        "sample_id",
        "point_index"
    ]

    raw_curve_keys = curves[
        ["figure_id", "sample_id"]
    ].copy()

    for column in point_columns:
        if column in raw_curve_keys.columns:
            raw_curve_keys[column] = pd.to_numeric(
                raw_curve_keys[column],
                errors="raise"
            ).astype("int64")

    raw_curve_keys = raw_curve_keys.drop_duplicates()

    points = pd.read_csv(
        CURVE_POINTS_INPUT,
        usecols=point_columns,
        dtype={
            "figure_id": "int64",
            "sample_id": "int64",
            "point_index": "int64"
        }
    )

    validate_row_count(
        points,
        EXPECTED_RAW_CURVE_POINTS,
        "Generated curve points"
    )

    validate_not_null(
        points,
        point_columns,
        "Generated curve points"
    )

    validate_unique_key(
        points,
        point_columns,
        "Generated curve points"
    )

    point_curve_keys = points[
        ["figure_id", "sample_id"]
    ].drop_duplicates()

    unknown_curves = point_curve_keys.merge(
        raw_curve_keys,
        on=["figure_id", "sample_id"],
        how="left",
        indicator=True
    )

    unknown_count = (
        unknown_curves["_merge"] == "left_only"
    ).sum()

    if unknown_count:
        raise ValueError(
            f"{unknown_count:,} point-level curve keys "
            "do not exist in the raw Curves dataset."
        )

    print("PASS: All curve-point keys reference raw curves.")

    index_summary = points.groupby(
        ["figure_id", "sample_id"]
    )["point_index"].agg(["min", "max", "count"])

    invalid_sequences = (
        (index_summary["min"] != 1)
        | (index_summary["max"] != index_summary["count"])
    ).sum()

    if invalid_sequences:
        raise ValueError(
            f"Found {invalid_sequences:,} curves with "
            "invalid point-index sequences."
        )

    print("PASS: Point indexes start at 1 and are continuous.")


def validate_tier2_outputs(curves):
    """Validate Tier 2 curve and measurement-point outputs."""

    if not TIER2_CURVES_INPUT.exists():
        raise FileNotFoundError(
            f"Tier 2 curves file not found: {TIER2_CURVES_INPUT}"
        )

    if not TIER2_POINTS_INPUT.exists():
        raise FileNotFoundError(
            f"Tier 2 points file not found: {TIER2_POINTS_INPUT}"
        )

    tier2_curves = pd.read_csv(
        TIER2_CURVES_INPUT,
        dtype={
            "figure_id": "int64",
            "sample_id": "int64"
        },
        usecols=["figure_id", "sample_id"]
    )

    tier2_points = pd.read_csv(
        TIER2_POINTS_INPUT,
        dtype={
            "figure_id": "int64",
            "sample_id": "int64",
            "point_index": "int64"
        }
    )

    validate_row_count(
        tier2_curves,
        EXPECTED_TIER2_CURVES,
        "Tier 2 curves"
    )

    validate_row_count(
        tier2_points,
        EXPECTED_TIER2_POINTS,
        "Tier 2 measurement points"
    )

    validate_unique_key(
        tier2_curves,
        ["figure_id", "sample_id"],
        "Tier 2 curves"
    )

    validate_unique_key(
        tier2_points,
        ["figure_id", "sample_id", "point_index"],
        "Tier 2 measurement points"
    )

    tier2_curve_keys = tier2_curves.drop_duplicates()

    tier2_point_keys = tier2_points[
        ["figure_id", "sample_id"]
    ].drop_duplicates()

    missing_keys = tier2_curve_keys.merge(
        tier2_point_keys,
        on=["figure_id", "sample_id"],
        how="left",
        indicator=True
    )

    curves_without_points = (
        missing_keys["_merge"] == "left_only"
    ).sum()

    if curves_without_points != EXPECTED_TIER2_CURVES_WITHOUT_POINTS:
        raise ValueError(
            f"Expected {EXPECTED_TIER2_CURVES_WITHOUT_POINTS:,} "
            f"Tier 2 curves without points, "
            f"got {curves_without_points:,}."
        )

    print(
        "PASS: Tier 2 curves without measurement points = "
        f"{curves_without_points:,}"
    )


def main():
    """Run ingestion and data-quality validation."""

    print("\n========== STARRYDATA DATA VALIDATION ==========\n")

    papers = get_papers_data()
    samples = get_samples_data()
    curves = get_curves_data()

    validate_schema(
        papers,
        ["SID"],
        "starrydata_papers.csv"
    )

    validate_schema(
        samples,
        ["SID", "sample_id"],
        "starrydata_samples.csv"
    )

    validate_schema(
        curves,
        ["SID", "sample_id", "figure_id", "x", "y"],
        "starrydata_curves.csv"
    )

    papers = validate_identifier_types(papers)
    samples = validate_identifier_types(samples)
    curves = validate_identifier_types(curves)

    validate_row_count(papers, EXPECTED_PAPERS_ROWS, "Papers")
    validate_row_count(samples, EXPECTED_SAMPLES_ROWS, "Samples")
    validate_row_count(curves, EXPECTED_CURVES_ROWS, "Curves")

    validate_not_null(papers, ["SID"], "Papers")
    validate_not_null(samples, ["sample_id"], "Samples")
    validate_not_null(
        curves,
        ["SID", "sample_id", "figure_id", "x", "y"],
        "Curves"
    )

    validate_unique_key(papers, ["SID"], "Papers")
    validate_unique_key(samples, ["sample_id"], "Samples")
    validate_unique_key(
        curves,
        ["figure_id", "sample_id"],
        "Curves"
    )

    validate_curve_references(curves, samples, papers)
    validate_curve_arrays(curves)
    validate_curve_points(curves)
    validate_tier2_outputs(curves)

    print("\n========== ALL VALIDATIONS PASSED ==========")

    return papers, samples, curves


if __name__ == "__main__":
    main()
