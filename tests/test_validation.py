
import pandas as pd
import pytest
import json


from src.validate import (
    validate_schema,
    validate_row_count,
    validate_not_null,
    validate_unique_key,
    validate_identifier_types,
    parse_curve_array,
    validate_curve_arrays,
    validate_curve_references,
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


def test_curve_arrays_pass():
    curves = pd.DataFrame({
        "x": [
            json.dumps([1, 2, 3]),
            json.dumps([4, 5])
        ],
        "y": [
            json.dumps([10, 20, 30]),
            json.dumps([40, 50])
        ]
    })

    total_points, empty_curves = validate_curve_arrays(
        curves,
        expected_points=5,
        expected_empty_curves=0
    )

    assert total_points == 5
    assert empty_curves == 0


def test_curve_arrays_detect_length_mismatch():
    curves = pd.DataFrame({
        "x": [json.dumps([1, 2, 3])],
        "y": [json.dumps([10, 20])]
    })

    with pytest.raises(ValueError, match="length mismatch"):
        validate_curve_arrays(
            curves,
            expected_points=3,
            expected_empty_curves=0
        )


def test_curve_arrays_detect_empty_arrays():
    curves = pd.DataFrame({
        "x": [json.dumps([]), json.dumps([1, 2])],
        "y": [json.dumps([]), json.dumps([10, 20])]
    })

    total_points, empty_curves = validate_curve_arrays(
        curves,
        expected_points=2,
        expected_empty_curves=1
    )

    assert total_points == 2
    assert empty_curves == 1


def test_invalid_curve_array_json():
    with pytest.raises(ValueError, match="Invalid x JSON"):
        parse_curve_array("{invalid}", "x", 0)


def test_curve_array_must_be_a_list():
    with pytest.raises(ValueError, match="must contain a JSON array"):
        parse_curve_array(json.dumps({"value": 10}), "x", 0)


def test_orphan_sid_detection():
    curves = pd.DataFrame({
        "SID": ["1001", "8534", "8535"],
        "sample_id": ["101", "102", "103"]
    })

    samples = pd.DataFrame({
        "sample_id": ["101", "102", "103"]
    })

    papers = pd.DataFrame({
        "SID": ["1001"]
    })

    orphan_sids, orphan_rows = validate_curve_references(
        curves,
        samples,
        papers,
        expected_orphan_sids={"8534", "8535"}
    )

    assert orphan_sids == {"8534", "8535"}
    assert orphan_rows == 2

def test_curve_reference_validation_fails_for_missing_sample():
    curves = pd.DataFrame({
        "SID": ["1001"],
        "sample_id": ["999"]
    })

    samples = pd.DataFrame({
        "sample_id": ["101"]
    })

    papers = pd.DataFrame({
        "SID": ["1001"]
    })

    with pytest.raises(ValueError, match="without matching Samples"):
        validate_curve_references(
            curves,
            samples,
            papers,
            expected_orphan_sids=set()
        )
