
import csv
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Paths and expected values
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "starrydata_curves.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_FILE = OUTPUT_DIR / "curve_points.csv"
TEMP_FILE = OUTPUT_DIR / "curve_points.tmp.csv"
LOG_FILE = OUTPUT_DIR / "curve_points_validation.log"

EXPECTED_ROWS = 4_839_779
EXPECTED_EMPTY_CURVES = 3_952


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def parse_array(value):
    """Parse a JSON array while preserving decimal precision."""

    return json.loads(
        value,
        parse_float=Decimal,
        parse_int=Decimal
    )


def log_result(log, description, passed, details=""):
    """Print and save a PASS/FAIL result."""

    status = "PASS" if passed else "FAIL"
    message = f"{status}: {description}"

    if details:
        message += f" | {details}"

    print(message)
    log.write(message + "\n")

    if not passed:
        raise ValueError(message)


# --------------------------------------------------
# Main curve-point generation
# --------------------------------------------------

def create_curve_points():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "w", encoding="utf-8") as log:

        print("\n========== CURVE POINT GENERATION ==========\n")

        log.write("CURVE POINT GENERATION VALIDATION\n\n")

        # Load raw curves
        curves = pd.read_csv(
            RAW_FILE,
            low_memory=False,
            skip_blank_lines=True,
            dtype={
                "figure_id": "string",
                "sample_id": "string",
                "x": "string",
                "y": "string"
            }
        )

        required_columns = [
            "figure_id",
            "sample_id",
            "x",
            "y"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in curves.columns
        ]

        log_result(
            log,
            "Mandatory columns exist",
            not missing_columns,
            str(missing_columns) if missing_columns else ""
        )

        log_result(
            log,
            "Raw curve row count",
            len(curves) == 237_313,
            f"Actual: {len(curves):,}"
        )

        # Check raw curve-pair uniqueness
        duplicate_pairs = curves.duplicated(
            subset=["figure_id", "sample_id"]
        ).sum()

        log_result(
            log,
            "Raw (figure_id, sample_id) pairs are unique",
            duplicate_pairs == 0,
            f"Duplicates: {duplicate_pairs}"
        )

        # Parse and validate arrays before writing
        parsed_curves = []
        total_points = 0
        empty_curves = 0
        mismatch_count = 0

        for row in curves.itertuples(index=False):

            x_values = parse_array(row.x)
            y_values = parse_array(row.y)

            if not isinstance(x_values, list):
                raise ValueError(
                    f"x is not an array for figure {row.figure_id}"
                )

            if not isinstance(y_values, list):
                raise ValueError(
                    f"y is not an array for figure {row.figure_id}"
                )

            if len(x_values) != len(y_values):
                mismatch_count += 1

            if len(x_values) == 0 and len(y_values) == 0:
                empty_curves += 1

            total_points += len(x_values)

            parsed_curves.append(
                (
                    row.figure_id,
                    row.sample_id,
                    x_values,
                    y_values
                )
            )

        log_result(
            log,
            "x and y array lengths match",
            mismatch_count == 0,
            f"Mismatched curves: {mismatch_count}"
        )

        log_result(
            log,
            "Empty array curve count",
            empty_curves == EXPECTED_EMPTY_CURVES,
            f"Actual: {empty_curves:,}"
        )

        log_result(
            log,
            "Total points equal sum of array lengths",
            total_points == EXPECTED_ROWS,
            f"Actual: {total_points:,}"
        )

        # Generate flattened CSV
        rows_written = 0

        with open(
            TEMP_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "figure_id",
                "sample_id",
                "point_index",
                "x_value",
                "y_value"
            ])

            for figure_id, sample_id, x_values, y_values in parsed_curves:

                for index, (x_value, y_value) in enumerate(
                    zip(x_values, y_values),
                    start=1
                ):

                    writer.writerow([
                        figure_id,
                        sample_id,
                        index,
                        x_value,
                        y_value
                    ])

                    rows_written += 1

        log_result(
            log,
            "Generated row count",
            rows_written == EXPECTED_ROWS,
            f"Actual: {rows_written:,}"
        )

        # Every output pair originates from a raw curve.
        raw_pairs = set(
            zip(curves["figure_id"], curves["sample_id"])
        )

        generated_pairs = {
            (figure_id, sample_id)
            for figure_id, sample_id, x_values, y_values
            in parsed_curves
            if len(x_values) > 0
        }

        log_result(
            log,
            "Every generated curve pair exists in raw curves",
            generated_pairs.issubset(raw_pairs)
        )

        # Each raw pair is unique, and point_index is generated
        # exactly once per point, starting at 1.
        log_result(
            log,
            "Output composite key is unique",
            duplicate_pairs == 0 and mismatch_count == 0,
            "(figure_id, sample_id, point_index)"
        )

        # Publish only after all checks pass
        TEMP_FILE.replace(OUTPUT_FILE)

        print("\n========== GENERATION COMPLETE ==========")
        print(f"Output: {OUTPUT_FILE}")
        print(f"Rows: {rows_written:,}")
        print(f"Empty curves logged: {empty_curves:,}")
        print(f"Validation log: {LOG_FILE}")

        log.write("\nGeneration completed successfully.\n")


if __name__ == "__main__":
    create_curve_points()
