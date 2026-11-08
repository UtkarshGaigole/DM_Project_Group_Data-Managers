"""Compare Tableau Prep and Python Tier 2 outputs.

Columns are matched by name, and rows are matched using composite keys.
SQLite provides disk-backed storage for large datasets.

Numeric comparisons retain full-precision source values. Absolute and relative
tolerances are reported separately; neither source CSV is modified.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLEAU_DIR = ROOT / "data" / "processed" / "tableau"
PYTHON_DIR = ROOT / "data" / "processed"
REPORT_PATH = ROOT / "docs" / "evidence" / "equivalence_report.md"
DATABASE_PATH = ROOT / "data" / "interim" / "comparison.sqlite"

RELATIVE_TOLERANCE = Decimal("1e-6")

# Tableau Prep writes numbers to its CSV output with at most 9 decimal places.
# Rounding to 9 decimals changes a value by at most half a unit in the 9th
# decimal, i.e. 5e-10. The tolerance follows from that export precision (which
# the report measures as "max Tableau decimals"), not from the observed result.
# This is a comparison threshold only; Python output is never rounded.
TABLEAU_EXPORT_DECIMALS = 9
EXPORT_ROUNDING_TOLERANCE = Decimal("5e-10")
ABSOLUTE_TOLERANCES = {
    "x_value": EXPORT_ROUNDING_TOLERANCE,
    "y_value": EXPORT_ROUNDING_TOLERANCE,
}

BATCH_SIZE = 5_000

DATASETS = {
    "Tier 2 curves": {
        "tableau": TABLEAU_DIR / "tier2_curves.csv",
        "python": PYTHON_DIR / "tier2_curves.csv",
        "keys": ["figure_id", "sample_id"],
        "numeric_columns": set(),
    },
    "Tier 2 points": {
        "tableau": TABLEAU_DIR / "tier2_points.csv",
        "python": PYTHON_DIR / "tier2_points.csv",
        "keys": ["figure_id", "sample_id", "point_index"],
        "numeric_columns": {"x_value", "y_value"},
    },
}


def normalize_newlines(value: str) -> str:
    """Normalize line endings without changing other text."""
    return value.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")


def normalize_value(value: str | None):
    """Normalize nulls, timestamps, booleans, numbers and line endings."""
    if value is None or value == "":
        return None

    if value in {"True", "False"}:
        return value.lower()

    timestamp_formats = (
        "%d-%m-%Y %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
    )

    for fmt in timestamp_formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    try:
        number = Decimal(value)
        if number.is_finite():
            return number
    except InvalidOperation:
        pass

    return normalize_newlines(value)


def parse_decimal(value: str | None) -> Decimal | None:
    """Return a finite Decimal, or None if the value is not numeric."""
    if value is None:
        return None

    try:
        number = Decimal(value)
        return number if number.is_finite() else None
    except (InvalidOperation, TypeError):
        return None


def relative_difference(tableau_value: Decimal, python_value: Decimal) -> Decimal:
    """Calculate symmetric relative difference."""
    denominator = max(abs(tableau_value), abs(python_value))
    if denominator == 0:
        return Decimal("0")
    return abs(tableau_value - python_value) / denominator


def make_key(row: dict[str, str], key_columns: list[str]) -> str:
    """Create a normalized composite key."""
    values = [normalize_value(row[column]) for column in key_columns]
    if any(value is None for value in values):
        raise ValueError(f"Null value in comparison key: {values}")
    return json.dumps([str(value) for value in values], separators=(",", ":"))


def inspect_csv(path: Path):
    """Return columns, row count and null counts for a CSV."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")

    row_count = 0
    null_counts = Counter()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        if not columns:
            raise ValueError(f"No CSV header found: {path}")

        for row in reader:
            row_count += 1
            for column in columns:
                if row[column] is None or row[column] == "":
                    null_counts[column] += 1

    return columns, row_count, dict(null_counts)


def prepare_database(connection: sqlite3.Connection) -> None:
    """Create fresh disk-backed comparison tables."""
    connection.execute("DROP TABLE IF EXISTS reference_rows")
    connection.execute("DROP TABLE IF EXISTS python_rows")

    connection.execute("""
        CREATE TABLE reference_rows (
            record_key TEXT PRIMARY KEY,
            row_data TEXT NOT NULL
        )
        """)
    connection.execute("""
        CREATE TABLE python_rows (
            record_key TEXT PRIMARY KEY,
            row_data TEXT NOT NULL
        )
        """)
    connection.commit()


def load_csv(
    connection: sqlite3.Connection,
    path: Path,
    table_name: str,
    key_columns: list[str],
    comparison_columns: list[str],
):
    """Load CSV records into SQLite and count duplicate keys."""
    if table_name not in {"reference_rows", "python_rows"}:
        raise ValueError("Invalid SQLite table name")

    inserted = 0
    duplicates = 0
    batch = []
    sql = f"INSERT OR IGNORE INTO {table_name} " "(record_key, row_data) VALUES (?, ?)"

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = make_key(row, key_columns)
            selected_values = {column: row[column] for column in comparison_columns}
            payload = json.dumps(
                selected_values,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            batch.append((key, payload))

            if len(batch) >= BATCH_SIZE:
                before = connection.total_changes
                connection.executemany(sql, batch)
                added = connection.total_changes - before
                inserted += added
                duplicates += len(batch) - added
                connection.commit()
                batch.clear()

        if batch:
            before = connection.total_changes
            connection.executemany(sql, batch)
            added = connection.total_changes - before
            inserted += added
            duplicates += len(batch) - added
            connection.commit()

    return inserted, duplicates


def compare_rows(
    connection: sqlite3.Connection,
    columns: list[str],
    numeric_columns: set[str],
):
    """Compare matching records and calculate full-file statistics."""
    results = {
        column: {
            "exact_mismatches": 0,
            "within_absolute_tolerance": 0,
            "within_relative_tolerance_only": 0,
            "outside_both_tolerances": 0,
            "substantive_mismatches": 0,
            "newline_export_differences": 0,
            "max_relative_difference": Decimal("0"),
            "max_absolute_difference": Decimal("0"),
            "max_tableau_decimals": 0,
            "tableau_scientific_values": 0,
            "scientific_mismatches": 0,
            "max_scientific_absolute_difference": Decimal("0"),
        }
        for column in columns
    }

    query = """
        SELECT r.row_data, p.row_data
        FROM reference_rows AS r
        INNER JOIN python_rows AS p
            ON r.record_key = p.record_key
    """
    cursor = connection.execute(query)
    inspected = 0

    while True:
        batch = cursor.fetchmany(BATCH_SIZE)
        if not batch:
            break

        for tableau_json, python_json in batch:
            tableau_row = json.loads(tableau_json)
            python_row = json.loads(python_json)
            inspected += 1

            for column in columns:
                tableau_raw = tableau_row[column]
                python_raw = python_row[column]
                tableau_value = normalize_value(tableau_raw)
                python_value = normalize_value(python_raw)
                stats = results[column]

                is_scientific = False
                if column in numeric_columns and isinstance(tableau_raw, str):
                    if "e" in tableau_raw.lower():
                        # Scientific notation (e.g. 1.5E-12) is not rounded to a
                        # fixed number of decimals, so it is counted separately.
                        is_scientific = True
                        stats["tableau_scientific_values"] += 1
                    else:
                        number = parse_decimal(tableau_raw)
                        if number is not None:
                            decimals = max(0, -number.as_tuple().exponent)
                            if decimals > stats["max_tableau_decimals"]:
                                stats["max_tableau_decimals"] = decimals

                if tableau_value == python_value:
                    if (
                        tableau_raw != python_raw
                        and isinstance(tableau_raw, str)
                        and isinstance(python_raw, str)
                        and "\r\r\n" in tableau_raw
                        and normalize_newlines(tableau_raw)
                        == normalize_newlines(python_raw)
                    ):
                        stats["newline_export_differences"] += 1
                    continue

                stats["exact_mismatches"] += 1
                if is_scientific:
                    stats["scientific_mismatches"] += 1

                if column not in numeric_columns:
                    stats["substantive_mismatches"] += 1
                    continue

                tableau_number = parse_decimal(tableau_raw)
                python_number = parse_decimal(python_raw)

                if tableau_number is None or python_number is None:
                    stats["outside_both_tolerances"] += 1
                    stats["substantive_mismatches"] += 1
                    continue

                absolute = abs(tableau_number - python_number)
                relative = relative_difference(tableau_number, python_number)

                stats["max_absolute_difference"] = max(
                    stats["max_absolute_difference"], absolute
                )
                stats["max_relative_difference"] = max(
                    stats["max_relative_difference"], relative
                )
                if is_scientific:
                    stats["max_scientific_absolute_difference"] = max(
                        stats["max_scientific_absolute_difference"], absolute
                    )

                absolute_tolerance = ABSOLUTE_TOLERANCES.get(column, Decimal("0"))
                within_absolute = absolute <= absolute_tolerance
                within_relative = relative <= RELATIVE_TOLERANCE

                if within_absolute:
                    stats["within_absolute_tolerance"] += 1
                elif within_relative:
                    stats["within_relative_tolerance_only"] += 1
                else:
                    stats["outside_both_tolerances"] += 1
                    stats["substantive_mismatches"] += 1

    return results, inspected


def compare_dataset(name: str, config: dict):
    """Compare schema, rows, keys, nulls and values."""
    tableau_path = config["tableau"]
    python_path = config["python"]
    keys = config["keys"]

    tableau_columns, tableau_count, tableau_nulls = inspect_csv(tableau_path)
    python_columns, python_count, python_nulls = inspect_csv(python_path)
    tableau_set = set(tableau_columns)
    python_set = set(python_columns)
    common_columns = sorted(tableau_set & python_set)

    missing_python_columns = sorted(tableau_set - python_set)
    missing_tableau_columns = sorted(python_set - tableau_set)

    for key in keys:
        if key not in common_columns:
            raise ValueError(f"Missing comparison key: {key}")

    connection = sqlite3.connect(DATABASE_PATH)
    try:
        prepare_database(connection)

        tableau_inserted, tableau_duplicates = load_csv(
            connection, tableau_path, "reference_rows", keys, common_columns
        )
        python_inserted, python_duplicates = load_csv(
            connection, python_path, "python_rows", keys, common_columns
        )

        missing_in_python = connection.execute("""
            SELECT COUNT(*)
            FROM reference_rows AS r
            LEFT JOIN python_rows AS p ON r.record_key = p.record_key
            WHERE p.record_key IS NULL
            """).fetchone()[0]

        missing_in_tableau = connection.execute("""
            SELECT COUNT(*)
            FROM python_rows AS p
            LEFT JOIN reference_rows AS r ON p.record_key = r.record_key
            WHERE r.record_key IS NULL
            """).fetchone()[0]

        column_results, matched_rows = compare_rows(
            connection, common_columns, config["numeric_columns"]
        )
    finally:
        connection.close()

    return {
        "name": name,
        "tableau_columns": tableau_columns,
        "python_columns": python_columns,
        "schema_names_match": tableau_set == python_set,
        "column_order_matches": tableau_columns == python_columns,
        "missing_python_columns": missing_python_columns,
        "missing_tableau_columns": missing_tableau_columns,
        "tableau_rows": tableau_count,
        "python_rows": python_count,
        "tableau_nulls": tableau_nulls,
        "python_nulls": python_nulls,
        "duplicate_tableau_keys": tableau_duplicates,
        "duplicate_python_keys": python_duplicates,
        "indexed_tableau_rows": tableau_inserted,
        "indexed_python_rows": python_inserted,
        "missing_in_python": missing_in_python,
        "missing_in_tableau": missing_in_tableau,
        "matched_rows": matched_rows,
        "column_results": column_results,
    }


def format_cell(value) -> str:
    """Thousands separators for counts; booleans and text unchanged."""
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    return str(value)


def format_difference(value: Decimal) -> str:
    """Scientific notation for differences, plain 0 when there is none."""
    return "0" if value == 0 else f"{value:.6E}"


def write_report(results: list[dict]) -> None:
    """Write a detailed Markdown equivalence report."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tableau–Python Equivalence Report",
        "",
        "Comparison of Tableau Prep reference exports and Python Tier 2 outputs.",
        "",
        "## Summary",
        "",
        "| Check | Curves | Points |",
        "|---|---:|---:|",
    ]

    curves, points = results
    summary_rows = [
        ("Tableau rows", "tableau_rows"),
        ("Python rows", "python_rows"),
        ("Column names match", "schema_names_match"),
        ("Column order matches", "column_order_matches"),
        ("Duplicate Tableau keys", "duplicate_tableau_keys"),
        ("Duplicate Python keys", "duplicate_python_keys"),
        ("Missing in Python", "missing_in_python"),
        ("Missing in Tableau", "missing_in_tableau"),
        ("Matched rows", "matched_rows"),
    ]
    for label, key in summary_rows:
        lines.append(f"| {label} | {format_cell(curves[key])} | {format_cell(points[key])} |")

    absolute_description = ", ".join(
        f"`{column}={value}`" for column, value in ABSOLUTE_TOLERANCES.items()
    )
    lines.extend(
        [
            "",
            "## Column-level value comparison",
            "",
            f"Numeric relative tolerance: `{RELATIVE_TOLERANCE}`.",
            f"Absolute tolerances: {absolute_description}.",
            "",
            "Exact mismatches are counted after timestamp and newline "
            "normalization. Numeric differences are classified separately "
            "using absolute and relative tolerances. Source values are not "
            "rounded or modified.",
            "",
        ]
    )

    for result in results:
        lines.extend(
            [
                f"### {result['name']}",
                "",
                "| Column | Exact mismatches | Within absolute tolerance | "
                "Within relative tolerance only | Outside both | "
                "Substantive mismatches | Newline side effects | "
                "Max absolute difference | Max relative difference |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )

        for column, stats in result["column_results"].items():
            lines.append(
                f"| {column} | "
                f"{stats['exact_mismatches']:,} | "
                f"{stats['within_absolute_tolerance']:,} | "
                f"{stats['within_relative_tolerance_only']:,} | "
                f"{stats['outside_both_tolerances']:,} | "
                f"{stats['substantive_mismatches']:,} | "
                f"{stats['newline_export_differences']:,} | "
                f"{format_difference(stats['max_absolute_difference'])} | "
                f"{format_difference(stats['max_relative_difference'])} |"
            )

        lines.extend(
            [
                "",
                "### Null-count comparison",
                "",
                "| Column | Tableau nulls | Python nulls | Match |",
                "|---|---:|---:|---|",
            ]
        )

        all_columns = sorted(
            set(result["tableau_columns"]) | set(result["python_columns"])
        )
        for column in all_columns:
            tableau_nulls = result["tableau_nulls"].get(column, 0)
            python_nulls = result["python_nulls"].get(column, 0)
            lines.append(
                f"| {column} | {tableau_nulls:,} | "
                f"{python_nulls:,} | {tableau_nulls == python_nulls} |"
            )

        lines.extend(
            [
                "",
                "### Schema differences",
                "",
                f"- Columns missing from Python: "
                f"{result['missing_python_columns'] or 'None'}",
                f"- Columns missing from Tableau: "
                f"{result['missing_tableau_columns'] or 'None'}",
                f"- Column names match: **{result['schema_names_match']}**",
                f"- Column order matches: **{result['column_order_matches']}**",
                "",
            ]
        )

    all_numeric_within_absolute = all(
        stats["within_relative_tolerance_only"] == 0
        and stats["outside_both_tolerances"] == 0
        for result in results
        for column, stats in result["column_results"].items()
        if column in DATASETS[result["name"]]["numeric_columns"]
    )
    lines.extend(
        [
            "## Interpretation and known export differences",
            "",
            "1. Python retains full-precision measurement values. The "
            "comparison applies explicit tolerances for assessment and does "
            "not round or modify Python output files.",
            "",
            "2. The absolute tolerance of `5e-10` for `x_value` and `y_value` "
            "follows from Tableau's export precision, not from the observed "
            "result. Tableau writes numbers in plain notation with at most "
            f"{TABLEAU_EXPORT_DECIMALS} decimal places; rounding to "
            f"{TABLEAU_EXPORT_DECIMALS} decimals changes a value by at most "
            "half a unit in the last place (5e-10). Very small or very large "
            "values are written in scientific notation instead, with a limited "
            "number of significant digits. Measured in the Tableau file: "
            + "; ".join(
                f"`{column}`: plain-notation values have at most "
                f"{stats['max_tableau_decimals']} decimals; "
                f"{stats['tableau_scientific_values']:,} values are in "
                f"scientific notation, of which "
                f"{stats['scientific_mismatches']:,} differ from Python "
                f"(largest absolute difference "
                f"{format_difference(stats['max_scientific_absolute_difference'])})"
                for result in results
                for column, stats in result["column_results"].items()
                if column in DATASETS[result["name"]]["numeric_columns"]
            )
            + ". "
            + (
                "Every numeric difference, in either notation, is at most "
                "5e-10 in absolute terms; the largest relative differences "
                "(column table above) occur for very small values. Both are "
                "far below the precision with which values can be read from a "
                "published plot, so they have no practical effect. Python "
                "keeps the source precision; the Tableau CSV export is the "
                "lossy side. "
                if all_numeric_within_absolute
                else "**Not every numeric difference is within 5e-10 (see the "
                "column table above), so this tolerance does not cover all "
                "differences and must be revisited.** "
            )
            + "Values within the tolerance are reported as within absolute "
            "tolerance, not as exact matches.",
            "",
            "3. Relative tolerance is reported separately. A value within "
            "relative tolerance but outside its column's absolute tolerance "
            "is shown in its own category.",
            "",
            "4. Tableau may add an extra carriage return when exporting "
            "multiline text. Newline variants are normalized for comparison "
            "and counted separately as export side effects.",
            "",
            "5. Literal text values such as `NA`, `N/A` and `null` are "
            "preserved. Empty CSV fields are treated as null.",
            "",
            "6. Columns are compared by name, not CSV position. Column order "
            "is checked separately.",
            "",
            "7. Rows are matched using the configured composite keys.",
            "",
            "This report is generated by `src/compare_outputs.py`.",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Compare both Tier 2 outputs and generate the report."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    results = []

    for name, config in DATASETS.items():
        print(f"\n--- Comparing {name} ---")
        result = compare_dataset(name, config)
        results.append(result)

        print(f"Tableau rows: {result['tableau_rows']:,}")
        print(f"Python rows: {result['python_rows']:,}")
        print(f"Matched rows: {result['matched_rows']:,}")
        print(f"Column names match: {result['schema_names_match']}")
        print(f"Column order matches: {result['column_order_matches']}")
        print(f"Missing in Python: {result['missing_in_python']:,}")
        print(f"Missing in Tableau: {result['missing_in_tableau']:,}")
        print(
            "Duplicate keys: "
            f"Tableau={result['duplicate_tableau_keys']:,}, "
            f"Python={result['duplicate_python_keys']:,}"
        )

        print("\nColumn comparison:")
        for column, stats in result["column_results"].items():
            if stats["exact_mismatches"] > 0:
                print(
                    f"{column}: {stats['exact_mismatches']:,} exact "
                    f"differences, {stats['within_absolute_tolerance']:,} "
                    f"within absolute tolerance, "
                    f"{stats['within_relative_tolerance_only']:,} within "
                    f"relative tolerance only, "
                    f"{stats['outside_both_tolerances']:,} outside both"
                )

    write_report(results)
    print(f"\nReport saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()