"""Clean Starrydata tables and create the agreed Tier 2 outputs.

The pipeline deliberately preserves sample_info as raw JSON text. Flattening is
not part of this deliverable because the canonical variant mapping is pending.
Dataset-specific expected counts belong in tests, not in this pipeline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PAPERS_INPUT = RAW_DIR / "starrydata_papers.csv"
SAMPLES_INPUT = RAW_DIR / "starrydata_samples.csv"
CURVES_INPUT = RAW_DIR / "starrydata_curves.csv"
CURVE_POINTS_INPUT = INTERIM_DIR / "curve_points.csv"

PAPERS_OUTPUT = INTERIM_DIR / "starrydata_papers_cleaned.csv"
SAMPLES_OUTPUT = INTERIM_DIR / "starrydata_samples_cleaned.csv"
CURVES_OUTPUT = INTERIM_DIR / "starrydata_curves_cleaned.csv"
TIER2_CURVES_OUTPUT = PROCESSED_DIR / "tier2_curves.csv"
TIER2_POINTS_OUTPUT = PROCESSED_DIR / "tier2_points.csv"

TIER2_PROPERTIES = {
    "Seebeck coefficient",
    "Electrical conductivity",
    "Electrical resistivity",
    "Thermal conductivity",
    "Power factor",
    "ZT",
}

# The seven-column point contract. Confirm the exact order/names against the
# reference export when it is supplied.
TIER2_POINT_COLUMNS = [
    "figure_id",
    "sample_id",
    "point_index",
    "x_value",
    "y_value",
    "prop_y",
    "unit_y",
]

IDENTIFIER_COLUMNS = {
    "SID",
    "sample_id",
    "figure_id",
    "DOI",
}


def read_csv(path: Path, *, string_columns: Iterable[str] = ()) -> pd.DataFrame:
    """Read a CSV while preserving identifiers and skipping blank lines."""
    if not path.is_file():
        raise FileNotFoundError(f"Required input file not found: {path}")

    dtype = {column: "string" for column in string_columns}
    return pd.read_csv(
        path,
        dtype=dtype or None,
        low_memory=False,
        skip_blank_lines=True,
        keep_default_na=True,
    )


def clean_timestamp_column(
    frame: pd.DataFrame,
    column: str,
    *,
    offset_hours: int = 9,
) -> pd.DataFrame:
    """Convert Starrydata timestamp strings to ISO-like UTC strings.

    The source timestamps contain a weekday prefix and a GMT suffix. The
    timestamp body is parsed and shifted by the source's nine-hour offset.
    """
    if column not in frame.columns:
        raise KeyError(f"Required timestamp column is missing: {column}")

    result = frame.copy()
    extracted = result[column].astype("string").str.slice(4, 24)
    parsed = pd.to_datetime(
        extracted,
        format="%b %d %Y %H:%M:%S",
        errors="coerce",
    )
    invalid = parsed.isna()
    if invalid.any():
        examples = result.loc[invalid, column].head(5).tolist()
        raise ValueError(
            f"{column}: {int(invalid.sum())} timestamp(s) could not be parsed; "
            f"examples: {examples}"
        )

    result[f"{column}_utc"] = (parsed - pd.Timedelta(hours=offset_hours)).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return result.drop(columns=column)


def extract_issued_date(value: object) -> str | None:
    """Return the contents of the first double-bracketed issued value."""
    if pd.isna(value):
        return None
    match = re.search(r"\[\[(.*?)\]\]", str(value))
    if not match:
        return None
    return match.group(1).strip()


def _parse_optional_integer(
    value: str | None, *, field: str, row: object
) -> int | None:
    """Parse one issued date component; empty is missing, other text is invalid."""
    if value is None or value == "":
        return None
    if not value.isdigit():
        raise ValueError(
            f"Unexpected non-numeric {field} in issued at row {row!r}: {value!r}"
        )
    return int(value)


def clean_publication_precision(papers: pd.DataFrame) -> pd.DataFrame:
    """Extract issued_year/month/day and precision without silent coercion."""
    if "issued" not in papers.columns:
        raise KeyError("Required column 'issued' is missing")

    result = papers.copy()
    extracted = result["issued"].map(extract_issued_date)
    parsed_components: list[tuple[int | None, int | None, int | None]] = []

    for row_index, value in extracted.items():
        if value is None or value == "":
            parsed_components.append((None, None, None))
            continue

        parts = [part.strip() for part in value.split(",")]
        # A small subset of source records stores an empty component as "".
        parts = [None if part in {'""', "''"} else part for part in parts]
        if len(parts) > 3:
            raise ValueError(
                f"Too many issued date components at row {row_index!r}: {value!r}"
            )
        parts += [None] * (3 - len(parts))
        parsed_components.append(
            (
                _parse_optional_integer(parts[0], field="year", row=row_index),
                _parse_optional_integer(parts[1], field="month", row=row_index),
                _parse_optional_integer(parts[2], field="day", row=row_index),
            )
        )

    component_frame = pd.DataFrame(
        parsed_components,
        index=result.index,
        columns=["issued_year", "issued_month", "issued_day"],
    )
    for column in component_frame.columns:
        result[column] = pd.array(component_frame[column], dtype="Int64")

    result["issued_precision"] = "Unknown"
    result.loc[result["issued_year"].notna(), "issued_precision"] = "Y"
    result.loc[result["issued_month"].notna(), "issued_precision"] = "YM"
    result.loc[result["issued_day"].notna(), "issued_precision"] = "YMD"
    return result.drop(columns="issued")


def clean_samples_data() -> pd.DataFrame:
    """Clean sample timestamps while preserving sample_info exactly as text."""
    samples = read_csv(
        SAMPLES_INPUT,
        string_columns=("SID", "sample_id"),
    )
    if "sample_info" not in samples.columns:
        raise KeyError("Required column 'sample_info' is missing from Samples")

    samples = clean_timestamp_column(samples, "created_at")
    samples = clean_timestamp_column(samples, "updated_at")
    samples.to_csv(SAMPLES_OUTPUT, index=False, encoding="utf-8")
    print(f"Saved Samples: {len(samples):,} rows -> {SAMPLES_OUTPUT}")
    return samples


def clean_papers_data() -> pd.DataFrame:
    """Clean paper timestamp and publication date precision."""
    papers = read_csv(PAPERS_INPUT, string_columns=("SID", "DOI"))
    papers = clean_timestamp_column(papers, "created_at")
    papers = clean_publication_precision(papers)
    papers.to_csv(PAPERS_OUTPUT, index=False, encoding="utf-8")
    print(f"Saved Papers: {len(papers):,} rows -> {PAPERS_OUTPUT}")
    return papers


def clean_curves_data() -> pd.DataFrame:
    """Clean curve timestamps and preserve identifiers as strings."""
    curves = read_csv(
        CURVES_INPUT,
        string_columns=("SID", "DOI", "sample_id", "figure_id"),
    )
    curves = clean_timestamp_column(curves, "created_at")
    curves = clean_timestamp_column(curves, "updated_at")
    curves.to_csv(CURVES_OUTPUT, index=False, encoding="utf-8")
    print(f"Saved Curves: {len(curves):,} rows -> {CURVES_OUTPUT}")
    return curves


def filter_tier2_curves(curves: pd.DataFrame) -> pd.DataFrame:
    """Select Temperature curves in the ThermoelectricMaterials project."""
    required = {"project_names", "prop_x", "prop_y"}
    missing = required.difference(curves.columns)
    if missing:
        raise KeyError(f"Missing Tier 2 filter columns: {sorted(missing)}")

    project_mask = (
        curves["project_names"]
        .astype("string")
        .str.contains(
            "ThermoelectricMaterials",
            regex=False,
            na=False,
        )
    )
    property_mask = curves["prop_y"].isin(TIER2_PROPERTIES)
    temperature_mask = curves["prop_x"].eq("Temperature")
    return curves.loc[project_mask & property_mask & temperature_mask].copy()


def _add_non_duplicate_columns(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    join_keys: list[str],
) -> pd.DataFrame:
    """Left-join only new columns, keeping one copy of each join key/field."""
    new_columns = [
        column
        for column in right.columns
        if column not in join_keys and column not in left.columns
    ]
    return left.merge(
        right[join_keys + new_columns],
        on=join_keys,
        how="left",
        validate="many_to_one",
    )


def join_tier2_datasets(
    tier2_curves: pd.DataFrame,
    samples: pd.DataFrame,
    papers: pd.DataFrame,
) -> pd.DataFrame:
    """Enrich Tier 2 curves, deriving orphan status from the paper join."""
    required_samples = {"sample_id"}
    required_papers = {"SID"}
    if not required_samples.issubset(samples.columns):
        raise KeyError("Samples must contain sample_id")
    if not required_papers.issubset(papers.columns):
        raise KeyError("Papers must contain SID")
    if "sample_id" not in tier2_curves.columns or "SID" not in tier2_curves.columns:
        raise KeyError("Tier 2 curves must contain sample_id and SID")

    result = _add_non_duplicate_columns(
        tier2_curves,
        samples,
        join_keys=["sample_id"],
    )

    # Keep the curve-side SID and any existing fields; add only paper fields
    # that do not already exist, avoiding duplicate/suffixed join columns.
    result = _add_non_duplicate_columns(result, papers, join_keys=["SID"])

    paper_ids = papers["SID"].dropna().astype("string")
    result["is_orphan"] = ~result["SID"].astype("string").isin(paper_ids)
    return result


def _load_curve_points(path: Path) -> pd.DataFrame:
    """Load generated curve points with string IDs and numeric measurements."""
    points = read_csv(
        path,
        string_columns=("figure_id", "sample_id"),
    )
    required = {"figure_id", "sample_id", "point_index", "x_value", "y_value"}
    missing = required.difference(points.columns)
    if missing:
        raise KeyError(f"Curve-points file is missing columns: {sorted(missing)}")
    points["point_index"] = pd.to_numeric(points["point_index"], errors="raise").astype(
        "int64"
    )
    points["x_value"] = pd.to_numeric(points["x_value"], errors="raise")
    points["y_value"] = pd.to_numeric(points["y_value"], errors="raise")
    return points


def build_tier2_outputs(
    enriched_curves: pd.DataFrame,
    curve_points: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create contract-shaped Tier 2 curve and measurement-point tables."""
    curve_keys = ["figure_id", "sample_id"]
    missing_keys = set(curve_keys).difference(enriched_curves.columns)
    if missing_keys:
        raise KeyError(f"Tier 2 curves are missing join keys: {sorted(missing_keys)}")

    if enriched_curves.duplicated(curve_keys).any():
        raise ValueError("Tier 2 curve identifiers are not unique")

    # Count points per curve, then retain curves with zero points as well.
    point_counts = (
        curve_points.groupby(curve_keys, dropna=False)
        .size()
        .rename("n_points")
        .reset_index()
    )
    tier2_curves = enriched_curves.merge(
        point_counts,
        on=curve_keys,
        how="left",
        validate="one_to_one",
    )
    tier2_curves["n_points"] = tier2_curves["n_points"].fillna(0).astype("int64")
    tier2_curves["has_points"] = tier2_curves["n_points"].gt(0)
    tier2_curves = tier2_curves.drop(columns=["x", "y"], errors="ignore")

    # Add property metadata to points. The curve table supplies one row per key.
    metadata_columns = ["figure_id", "sample_id", "prop_y", "unit_y"]
    missing_metadata = set(metadata_columns).difference(enriched_curves.columns)
    if missing_metadata:
        raise KeyError(
            f"Tier 2 curves are missing point metadata: {sorted(missing_metadata)}"
        )
    metadata = enriched_curves[metadata_columns].drop_duplicates(curve_keys)
    tier2_points = curve_points.merge(
        metadata,
        on=curve_keys,
        how="inner",
        validate="many_to_one",
    )
    tier2_points = tier2_points[TIER2_POINT_COLUMNS]

    return tier2_curves, tier2_points


def main() -> None:
    """Run the cleaning pipeline and write final Tier 2 deliverables."""
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    samples = clean_samples_data()
    papers = clean_papers_data()
    curves = clean_curves_data()

    tier2_curves = filter_tier2_curves(curves)
    enriched_curves = join_tier2_datasets(tier2_curves, samples, papers)
    curve_points = _load_curve_points(CURVE_POINTS_INPUT)
    output_curves, output_points = build_tier2_outputs(enriched_curves, curve_points)

    output_curves.to_csv(TIER2_CURVES_OUTPUT, index=False, encoding="utf-8")
    output_points.to_csv(TIER2_POINTS_OUTPUT, index=False, encoding="utf-8")

    print("\nCleaning pipeline completed.")
    print(f"Tier 2 curves: {len(output_curves):,}")
    print(f"Tier 2 curves with points: {int(output_curves['has_points'].sum()):,}")
    print(
        f"Tier 2 curves without points: {int((~output_curves['has_points']).sum()):,}"
    )
    print(f"Tier 2 measurement points: {len(output_points):,}")
    print(f"Orphan curves retained: {int(output_curves['is_orphan'].sum()):,}")
    print(f"Saved: {TIER2_CURVES_OUTPUT}")
    print(f"Saved: {TIER2_POINTS_OUTPUT}")


if __name__ == "__main__":
    main()
