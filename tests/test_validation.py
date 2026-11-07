
import pandas as pd
import pytest

from src.validate import (
    validate_schema,
    validate_row_count,
    validate_not_null,
    validate_unique_key,
    validate_identifier_types,
)


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "SID": ["1001", "1002", "1003"],
        "sample_id": ["101", "102", "103"],
        "value": [1.5, 2.5, 3.5],
    })


def test_schema_validation_passes(sample_dataframe):
    result = validate_schema(
        sample_dataframe,
        ["SID", "sample_id"],
        "test_samples.csv"
    )

    assert list(result.columns) == list(sample_dataframe.columns)


def test_schema_validation_fails_for_missing_column(sample_dataframe):
    with pytest.raises(ValueError, match="Missing columns"):
        validate_schema(
            sample_dataframe,
            ["SID", "missing_column"],
            "test_samples.csv"
        )


def test_row_count_passes(sample_dataframe):
    validate_row_count(
        sample_dataframe,
        3,
        "Test samples"
    )


def test_row_count_fails(sample_dataframe):
    with pytest.raises(ValueError, match="expected 4 rows"):
        validate_row_count(
            sample_dataframe,
            4,
            "Test samples"
        )


def test_not_null_passes(sample_dataframe):
    validate_not_null(
        sample_dataframe,
        ["SID", "sample_id"],
        "Test samples"
    )


def test_not_null_fails(sample_dataframe):
    sample_dataframe.loc[0, "SID"] = pd.NA

    with pytest.raises(ValueError, match="missing values"):
        validate_not_null(
            sample_dataframe,
            ["SID"],
            "Test samples"
        )


def test_unique_key_passes(sample_dataframe):
    validate_unique_key(
        sample_dataframe,
        ["SID"],
        "Test samples"
    )


def test_unique_key_fails(sample_dataframe):
    sample_dataframe.loc[2, "SID"] = "1001"

    with pytest.raises(ValueError, match="duplicate records"):
        validate_unique_key(
            sample_dataframe,
            ["SID"],
            "Test samples"
        )


def test_identifier_types_are_strings(sample_dataframe):
    sample_dataframe["SID"] = pd.to_numeric(
        sample_dataframe["SID"]
    )

    result = validate_identifier_types(sample_dataframe)

    assert result["SID"].dtype == pd.StringDtype()
    assert result["sample_id"].dtype == pd.StringDtype()
