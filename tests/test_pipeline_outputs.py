import hashlib

import pandas as pd
import pytest

from src.clean_data import (
    CURVE_POINTS_INPUT,
    CURVES_INPUT,
    PAPERS_INPUT,
    SAMPLES_INPUT,
    TIER2_CURVE_COLUMNS,
    TIER2_POINT_COLUMNS,
    clean_publication_precision,
    clean_timestamp_column,
    main,
    read_csv,
)

RAW_FILES_AVAILABLE = all(
    path.is_file()
    for path in (
        PAPERS_INPUT,
        SAMPLES_INPUT,
        CURVES_INPUT,
        CURVE_POINTS_INPUT,
    )
)


@pytest.fixture(scope="session")
def pipeline_outputs():
    """Run the full pipeline once for the integration tests."""
    if not RAW_FILES_AVAILABLE:
        pytest.skip("Raw Starrydata files or generated curve points are unavailable")

    main()

    curves = pd.read_csv(
        "data/processed/tier2_curves.csv",
        dtype={"SID": "string", "sample_id": "string", "figure_id": "string"},
    )
    points = pd.read_csv(
        "data/processed/tier2_points.csv",
        dtype={"sample_id": "string", "figure_id": "string"},
    )

    return curves, points


def test_timestamp_conversion():
    frame = pd.DataFrame({"created_at": ["Sun Jan 06 2019 01:04:51 GMT+0900"]})

    result = clean_timestamp_column(frame, "created_at")

    assert result.loc[0, "created_at_utc"] == "2019-01-05 16:04:51"
    assert "created_at" not in result.columns


def test_timestamp_conversion_rejects_invalid_values():
    frame = pd.DataFrame({"created_at": ["invalid timestamp"]})

    with pytest.raises(ValueError, match="could not be parsed"):
        clean_timestamp_column(frame, "created_at")


def test_publication_precision():
    papers = pd.DataFrame(
        {
            "issued": [
                "[[2020]]",
                "[[2021, 5]]",
                "[[2022, 6, 15]]",
                None,
                '[[2023, "", ""]]',
            ]
        }
    )

    result = clean_publication_precision(papers)

    assert result["issued_precision"].tolist() == [
        "Y",
        "YM",
        "YMD",
        "Unknown",
        "Y",
    ]

    assert result.loc[0, "issued_year"] == 2020
    assert result.loc[1, "issued_month"] == 5
    assert result.loc[2, "issued_day"] == 15
    assert pd.isna(result.loc[3, "issued_year"])
    assert pd.isna(result.loc[4, "issued_month"])


def test_publication_precision_rejects_invalid_component():
    papers = pd.DataFrame({"issued": ["[[2020, invalid]]"]})

    with pytest.raises(ValueError, match="non-numeric"):
        clean_publication_precision(papers)


@pytest.mark.skipif(
    not RAW_FILES_AVAILABLE,
    reason="Raw Starrydata files or generated curve points are unavailable",
)
def test_publication_precision_real_dataset():
    papers = read_csv(PAPERS_INPUT, string_columns=("SID", "DOI"))
    result = clean_publication_precision(papers)

    assert result["issued_precision"].value_counts().to_dict() == {
        "YMD": 25192,
        "YM": 24570,
        "Y": 6526,
        "Unknown": 207,
    }


def test_tier2_output_schemas(pipeline_outputs):
    curves, points = pipeline_outputs

    assert list(curves.columns) == TIER2_CURVE_COLUMNS
    assert list(points.columns) == TIER2_POINT_COLUMNS


def test_tier2_output_row_counts(pipeline_outputs):
    curves, points = pipeline_outputs

    assert len(curves) == 136679
    assert len(points) == 2337212


def test_tier2_curves_with_and_without_points(pipeline_outputs):
    curves, _ = pipeline_outputs

    assert int(curves["has_points"].sum()) == 134539
    assert int((~curves["has_points"]).sum()) == 2140
    assert int(curves["n_points"].isna().sum()) == 2140
    assert int(curves["n_points"].eq(0).sum()) == 0


def test_tier2_orphan_curves_are_retained(pipeline_outputs):
    curves, _ = pipeline_outputs

    assert int(curves["is_orphan"].sum()) == 28
    assert curves.loc[curves["is_orphan"], "SID"].notna().all()


def test_tier2_curve_keys_are_unique(pipeline_outputs):
    curves, _ = pipeline_outputs

    assert not curves.duplicated(["figure_id", "sample_id"]).any()


def test_tier2_point_keys_are_unique():
    if not RAW_FILES_AVAILABLE:
        pytest.skip("Raw Starrydata files or generated curve points are unavailable")

    main()
    points = pd.read_csv("data/processed/tier2_points.csv")

    assert not points.duplicated(["figure_id", "sample_id", "point_index"]).any()


def test_tier2_points_have_no_missing_values(pipeline_outputs):
    _, points = pipeline_outputs

    assert points.isna().sum().sum() == 0


def test_tier2_point_indexes_start_at_one(pipeline_outputs):
    _, points = pipeline_outputs

    minimum_indexes = points.groupby(["figure_id", "sample_id"])["point_index"].min()

    assert minimum_indexes.eq(1).all()


def test_sample_info_is_preserved_as_raw_text(pipeline_outputs):
    curves, _ = pipeline_outputs

    non_null_values = curves["sample_info"].dropna()

    assert non_null_values.map(lambda value: isinstance(value, str)).all()


def _sha256(path):
    """Calculate a file's SHA-256 hash."""
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


@pytest.mark.skipif(
    not RAW_FILES_AVAILABLE,
    reason="Raw Starrydata files or generated curve points are unavailable",
)
def test_pipeline_outputs_are_reproducible(pipeline_outputs):
    from src.clean_data import TIER2_CURVES_OUTPUT, TIER2_POINTS_OUTPUT

    first_hashes = (
        _sha256(TIER2_CURVES_OUTPUT),
        _sha256(TIER2_POINTS_OUTPUT),
    )

    main()

    second_hashes = (
        _sha256(TIER2_CURVES_OUTPUT),
        _sha256(TIER2_POINTS_OUTPUT),
    )

    assert first_hashes == second_hashes
