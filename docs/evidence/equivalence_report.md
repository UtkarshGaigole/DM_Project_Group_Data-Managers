# Tableau–Python Equivalence Report

Comparison of Tableau Prep reference exports and Python Tier 2 outputs.

## Summary

| Check | Curves | Points |
|---|---:|---:|
| Tableau rows | 136679 | 2337212 |
| Python rows | 136679 | 2337212 |
| Column names match | True | True |
| Column order matches | True | True |
| Duplicate Tableau keys | 0 | 0 |
| Duplicate Python keys | 0 | 0 |
| Missing in Python | 0 | 0 |
| Missing in Tableau | 0 | 0 |
| Matched rows | 136679 | 2337212 |

## Column-level value comparison

Numeric relative tolerance: `0.000001`.
Absolute tolerances: `x_value=0`, `y_value=5E-10`.

Exact mismatches are counted after timestamp and newline normalization. Numeric differences are classified separately using absolute and relative tolerances. Source values are not rounded or modified.

### Tier 2 curves

| Column | Exact mismatches | Within absolute tolerance | Within relative tolerance only | Outside both | Substantive mismatches | Newline side effects | Max absolute difference | Max relative difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DOI | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| ISSN | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| SID | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| URL | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| author | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| comments | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| composition | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| composition_details | 0 | 0 | 0 | 0 | 0 | 692 | 0.000000E+6 | 0.000000E+6 |
| container_title | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| container_title_short | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| created_at_utc | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| figure_id | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| figure_name | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| has_points | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| is_orphan | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| issue | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| issued_day | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| issued_month | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| issued_precision | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| issued_year | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| n_points | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| page | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| project_names | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| prop_x | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| prop_y | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| publisher | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| sample_id | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| sample_info | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| sample_name | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| title | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| unit_x | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| unit_y | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| updated_at_utc | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| volume | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |

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
| figure_id | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| point_index | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| prop_y | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| sample_id | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| unit_y | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000E+6 | 0.000000E+6 |
| x_value | 1 | 0 | 1 | 0 | 0 | 0 | 4.000000E-10 | 5.691925E-7 |
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

2. The `y_value` absolute tolerance of `5e-10` is based on the maximum absolute difference observed in the current full-file comparison. Values within this threshold are reported as within absolute tolerance, not as exact matches.

3. Relative tolerance is reported separately. A value within relative tolerance but outside its column's absolute tolerance is shown in its own category.

4. Tableau may add an extra carriage return when exporting multiline text. Newline variants are normalized for comparison and counted separately as export side effects.

5. Literal text values such as `NA`, `N/A` and `null` are preserved. Empty CSV fields are treated as null.

6. Columns are compared by name, not CSV position. Column order is checked separately.

7. Rows are matched using the configured composite keys.

This report is generated by `src/compare_outputs.py`.
