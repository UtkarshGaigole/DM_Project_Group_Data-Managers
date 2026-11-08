# Tableau–Python Equivalence Report

Comparison of Tableau Prep reference exports and Python Tier 2 outputs.

## Summary

| Check | Curves | Points |
|---|---:|---:|
| Tableau rows | 136,679 | 2,337,212 |
| Python rows | 136,679 | 2,337,212 |
| Column names match | True | True |
| Column order matches | True | True |
| Duplicate Tableau keys | 0 | 0 |
| Duplicate Python keys | 0 | 0 |
| Missing in Python | 0 | 0 |
| Missing in Tableau | 0 | 0 |
| Matched rows | 136,679 | 2,337,212 |

## Column-level value comparison

Numeric relative tolerance: `0.000001`.
Absolute tolerances: `x_value=5E-10`, `y_value=5E-10`.

Exact mismatches are counted after timestamp and newline normalization. Numeric differences are classified separately using absolute and relative tolerances. Source values are not rounded or modified.

### Tier 2 curves

| Column | Exact mismatches | Within absolute tolerance | Within relative tolerance only | Outside both | Substantive mismatches | Newline side effects | Max absolute difference | Max relative difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DOI | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ISSN | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SID | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| URL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| author | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| comments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| composition | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| composition_details | 0 | 0 | 0 | 0 | 0 | 692 | 0 | 0 |
| container_title | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| container_title_short | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| created_at_utc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| figure_id | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| figure_name | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| has_points | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| is_orphan | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| issue | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| issued_day | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| issued_month | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| issued_precision | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| issued_year | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| n_points | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| page | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| project_names | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| prop_x | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| prop_y | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| publisher | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sample_id | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sample_info | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sample_name | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| title | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| unit_x | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| unit_y | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| updated_at_utc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| volume | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Null-count comparison

| Column | Tableau nulls | Python nulls | Match |
|---|---:|---:|---|
| DOI | 0 | 0 | True |
| ISSN | 3,068 | 3,068 | True |
| SID | 0 | 0 | True |
| URL | 28 | 28 | True |
| author | 63 | 63 | True |
| comments | 88,814 | 88,814 | True |
| composition | 250 | 250 | True |
| composition_details | 129,401 | 129,401 | True |
| container_title | 28 | 28 | True |
| container_title_short | 3,398 | 3,398 | True |
| created_at_utc | 0 | 0 | True |
| figure_id | 0 | 0 | True |
| figure_name | 0 | 0 | True |
| has_points | 0 | 0 | True |
| is_orphan | 0 | 0 | True |
| issue | 15,034 | 15,034 | True |
| issued_day | 72,198 | 72,198 | True |
| issued_month | 18,489 | 18,489 | True |
| issued_precision | 28 | 28 | True |
| issued_year | 803 | 803 | True |
| n_points | 2,140 | 2,140 | True |
| page | 5,272 | 5,272 | True |
| project_names | 0 | 0 | True |
| prop_x | 0 | 0 | True |
| prop_y | 0 | 0 | True |
| publisher | 28 | 28 | True |
| sample_id | 0 | 0 | True |
| sample_info | 7,639 | 7,639 | True |
| sample_name | 32 | 32 | True |
| title | 28 | 28 | True |
| unit_x | 0 | 0 | True |
| unit_y | 0 | 0 | True |
| updated_at_utc | 0 | 0 | True |
| volume | 3,046 | 3,046 | True |

### Schema differences

- Columns missing from Python: None
- Columns missing from Tableau: None
- Column names match: **True**
- Column order matches: **True**

### Tier 2 points

| Column | Exact mismatches | Within absolute tolerance | Within relative tolerance only | Outside both | Substantive mismatches | Newline side effects | Max absolute difference | Max relative difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| figure_id | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| point_index | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| prop_y | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sample_id | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| unit_y | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| x_value | 1 | 1 | 0 | 0 | 0 | 0 | 4.000000E-10 | 5.691925E-7 |
| y_value | 404,916 | 404,916 | 0 | 0 | 0 | 0 | 5.000000E-10 | 4.999550E-6 |

### Null-count comparison

| Column | Tableau nulls | Python nulls | Match |
|---|---:|---:|---|
| figure_id | 0 | 0 | True |
| point_index | 0 | 0 | True |
| prop_y | 0 | 0 | True |
| sample_id | 0 | 0 | True |
| unit_y | 0 | 0 | True |
| x_value | 0 | 0 | True |
| y_value | 0 | 0 | True |

### Schema differences

- Columns missing from Python: None
- Columns missing from Tableau: None
- Column names match: **True**
- Column order matches: **True**

## Interpretation and known export differences

1. Python retains full-precision measurement values. The comparison applies explicit tolerances for assessment and does not round or modify Python output files.

2. The absolute tolerance of `5e-10` for `x_value` and `y_value` follows from Tableau's export precision, not from the observed result. Tableau writes numbers in plain notation with at most 9 decimal places; rounding to 9 decimals changes a value by at most half a unit in the last place (5e-10). Very small or very large values are written in scientific notation instead, with a limited number of significant digits. Measured in the Tableau file: `x_value`: plain-notation values have at most 9 decimals; 1 values are in scientific notation, of which 0 differ from Python (largest absolute difference 0); `y_value`: plain-notation values have at most 9 decimals; 700,298 values are in scientific notation, of which 49 differ from Python (largest absolute difference 4.000000E-33). Every numeric difference, in either notation, is at most 5e-10 in absolute terms; the largest relative differences (column table above) occur for very small values. Both are far below the precision with which values can be read from a published plot, so they have no practical effect. Python keeps the source precision; the Tableau CSV export is the lossy side. Values within the tolerance are reported as within absolute tolerance, not as exact matches.

3. Relative tolerance is reported separately. A value within relative tolerance but outside its column's absolute tolerance is shown in its own category.

4. Tableau may add an extra carriage return when exporting multiline text. Newline variants are normalized for comparison and counted separately as export side effects.

5. Literal text values such as `NA`, `N/A` and `null` are preserved. Empty CSV fields are treated as null.

6. Columns are compared by name, not CSV position. Column order is checked separately.

7. Rows are matched using the configured composite keys.

This report is generated by `src/compare_outputs.py`.
