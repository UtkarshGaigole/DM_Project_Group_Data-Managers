# Data Quality Issue Register

**Dataset:** `20261001_starrydata2`, Figshare snapshot `10.6084/m9.figshare.34036677.v1` (database snapshot 2026-10-01 02:00:01 JST)  
**Prepared by:** Group 6 "Data-Managers", SRH University of Applied Sciences Heidelberg  
**Version:** v2.2, 2026-11-07 (Python Tier 2 code merged 07 Nov, PR #20; formal Tableau–Python comparison pending; precision labels match the outputs; #20 moved to unresolved)  
**Row counts of the raw tables:** papers 56,495 · samples 106,331 · curves 237,313

## How to read this register

**Use case.** Training a model on the six thermoelectric properties (Seebeck coefficient, electrical conductivity, electrical resistivity, thermal conductivity, power factor, ZT) with temperature on the x-axis. This is the **in-scope** data: 136,679 curves.

**Severity measures the impact on that use case, not the share of missing values.** Two ratings are given per issue:

- **Severity** is rated **before treatment**: what the issue would do to the use case if the raw data were used as delivered.
- **Residual risk** is rated **after the applied treatment**: what is still left for a user of our outputs.

So an issue can be High in severity and Low in residual risk (for example #1, neutralised by the scope filter). Both use the same scale:

| Rating | Meaning |
|---|---|
| **High** | Would silently corrupt the values or the structure a model learns from. |
| **Medium** | Would bias, weaken or leak information in training or evaluation, or removes usable data. |
| **Low** | Affects only optional or descriptive information, or data outside the six properties. Documented for completeness. |

**Eight fields per issue:** problem · table / column · records affected · impact · proposed treatment · applied treatment · rows before / after · validation.

All counts were reproduced from the raw files (`dictionary_appendix_counts.py`, the profiling notebook) and the Tableau Prep flow. Where a check also cites the Python Tier 2 pipeline, that code was merged on 07 Nov (PR #20); the formal Tableau–Python comparison is pending. Every issue appears once (20 issues).

## Summary

| # | Issue | Table / column | Records affected | Severity (before) | Applied treatment | Residual risk (after) |
|---|---|---|---|---|---|---|
| 1 | Mixed x-axis: temperature and inverse temperature | curves.prop_x | 5,231 curves with core property names | **High** | Scope filter x = Temperature | Low: only K-based temperature curves remain; 5,231 curves knowingly excluded |
| 2 | Curve points stored as arrays in one cell | curves.x, curves.y | 237,313 curves | **High** | Unpacked to one row per point | Low: unpacked once and tested |
| 3 | Property name variants and unit errors | curves.prop_y, unit_y | 760 curves (same quantity, x = Temperature); 31 names / 11,295 curves incl. related quantities | **High** | Excluded and reported | Medium: no wrong values enter scope, but 760 usable curves are lost and unit errors stay uncorrected |
| 4 | Curves with empty point arrays | curves.x, curves.y | 3,952 (2,140 in scope) | Medium | Flagged `has_points = FALSE` | Low: flagged, no point rows |
| 5 | Same DOI on different paper records | papers.DOI | 85 rows share 40 DOIs (45 surplus) | Medium | Reported, not changed | Medium: leakage risk remains unless splits group by DOI |
| 6 | Orphans: SID not found in papers | samples, curves | 9 samples + 31 curves (28 in scope) | Medium | Flagged `is_orphan`, not dropped | Low: flagged and visible (in scope 28 of 136,679, 0.02%; overall 31 of 237,313, 0.01%) |
| 7 | Publication date has variable precision | papers.issued | 31,303 not full dates | Medium | Split into parts plus precision | Low: precision kept explicit (see #20) |
| 8 | 170 property names and 69 units | curves | whole table | Medium | Reason for the narrowed scope | Low in scope; unresolved outside the six properties |
| 9 | `sample_info` often empty | samples.sample_info | 33,875 samples without content | Medium | Kept; completeness stated correctly | Medium: missing descriptors cannot be recovered |
| 10 | Flattening bug in our own pipeline | samples.sample_info | 22,298 values in 15,786 records | Medium | Fix pending and tested safe (43 conflicts to review); Tier 2 keeps raw | Low for Tier 2 (not flattened); Medium for any flattened output until the fix is merged |
| 11 | Timestamps stored as JavaScript text | created_at / updated_at | 5 columns, all rows | Low | Parsed to UTC | Low |
| 12 | `log(Electrical conductivity)` labelled with a linear unit | curves.unit_y | 1,689 | Low | Out of scope; reported | Low |
| 13 | `sample_info` keys with spelling and space variants | samples.sample_info | 138 keys | Low | Merging mapping proposed | Low |
| 14 | `composition_details` mostly missing | samples | 87,433 (82.23%) | Low | Kept as null | Low |
| 15 | Curve comments missing | curves.comments | 103,868 (43.77%) | Low | Kept as null | Low |
| 16 | Every CSV ends with a blank line | all 3 files | 1 per file | Low | Removed in Tableau | Low |
| 17 | Line breaks inside quoted text | samples.composition_details | 6,586 records | Low | Handled by the text qualifier | Low |
| 18 | README says "XXX License" | README.md | n/a | Low | Documentation defect | Low |
| 19 | README file names and columns do not match the data | README.md | n/a | Low | Documentation defect | Low |
| 20 | One paper has publication month 0 | papers.issued | 1 paper (SID 31709) | Low | Unresolved: kept as recorded, reported as a limitation | Low |

---

## High severity

### 1. Mixed x-axis: temperature and inverse temperature

- **Problem:** the same property is plotted against different x-axes. Some curves have temperature on the x-axis, others inverse temperature (`Inverse temperature`, `1000/T`) or a non-temperature quantity such as carrier concentration.
- **Table / column:** `curves.prop_x`
- **Records affected:** 141,910 thermoelectric curves carry one of the six exact property names; 5,231 of them do not have `Temperature` on the x-axis (`Inverse temperature` 3,693, `Carrier concentration` 701, `1000/T` 193, `T` 191, and 63 other names on 453 curves). Example, electrical conductivity: 18,839 curves against temperature, 2,233 against inverse temperature.
- **Impact:** a model fed (x, y) points would mix temperature and 1/T values as if they were the same quantity. This corrupts every model that uses the x-axis.
- **Proposed treatment:** keep only curves whose x-axis is exactly `Temperature` (unit K). Convert inverse-temperature curves only after a separate check.
- **Applied treatment:** scope filter `prop_x = Temperature`. All 150,426 thermoelectric curves with a temperature x-axis use the unit K, so no conversion is needed.
- **Rows before / after:** 141,910 → 136,679 curves (5,231 excluded).
- **Validation:** the filter output is 136,679 curves in Tableau and in Python (Python pipeline, PR #20); `unit_x` is K for every kept curve.

### 2. Curve points stored as arrays in one cell

- **Problem:** each curve stores all its points as two JSON arrays (`x` and `y`) in single cells, so one row is a whole curve. The table is not in first normal form.
- **Table / column:** `curves.x`, `curves.y`
- **Records affected:** all 237,313 curves.
- **Impact:** models, joins and aggregations need one row per point. Arrays in a cell cannot be used directly and are slow and error-prone to split in each tool separately.
- **Proposed treatment:** unpack once, in one tested Python function, into a tidy point table keyed by the curve key (`figure_id`, `sample_id`) and the point position. Tableau reads that output.
- **Applied treatment:** `curve_points.csv` with the columns `figure_id`, `sample_id`, `point_index`, `x_value`, `y_value`.
- **Rows before / after:** 237,313 curves → 233,361 curves with points → 4,839,779 point rows. In scope: 134,539 curves → 2,337,212 points.
- **Validation:** rows equal the sum of the array lengths; the key (`figure_id`, `sample_id`, `point_index`) is unique; every curve key exists in the raw `curves`; automated checks run in the Python test suite (16 tests pass; Python pipeline, PR #20).

### 3. Property name variants and unit errors

- **Problem:** the same quantity appears under several names or notations, and some units are wrong. Seebeck coefficient is also named `thermopower` (489 curves) and `S` (70), and its unit is written both as `V*K^(-1)` and `V/K`. A further 47 `Thermopower` curves carry the unit `kg*m**2/A/s**3`, which is the volt, not V/K, so that label is a unit error. Other errors: `Resistivity` in ohm·m⁻¹ (14 curves, should be ohm·m), `conductivity` without a unit (2 curves), and `Figure of merit Zt` in K⁻¹ (4 curves; that unit belongs to Z, not ZT). Also `total thermal conductivity` (134 curves) is a name variant.
- **Two counts, two definitions.** The register and the data dictionary give different numbers for "variants" because they measure different things:
  - **About 760 curves** (exactly 760): the **same quantity** under another name or notation, or with a wrong unit, restricted to **thermoelectric curves with temperature on the x-axis**. These are the real data-quality problems.
  - **31 names / 11,295 curves** (data dictionary, Appendix B): the same group **plus related but different quantities**, counted over **all x-axes**. The related quantities are log and ln transforms, the lattice, electronic and other components of the thermal conductivity, products such as conductivity times temperature, and the figure of merit Z (which is not ZT). Those are out of scope by definition, **not errors**. Over all x-axes the same-quantity group is 12 names / 861 curves and the related group is 19 names / 10,434 curves.
- **Table / column:** `curves.prop_y`, `curves.unit_y`
- **Records affected:** 760 thermoelectric curves with temperature on the x-axis (same-quantity definition above; 606 of them Seebeck synonyms). The wider list of 31 names / 11,295 curves is not an error count.
- **Impact:** curves under a variant name are silently left out of the target property, which loses data. A wrong unit would put values of a different magnitude or quantity into the same column, which corrupts a model.
- **Proposed treatment:** merge the unambiguous Seebeck synonyms after unit conversion and fix or flag the wrong units. This needs per-variant judgement.
- **Applied treatment:** not merged. The six property names are matched exactly; the variants are excluded and reported as a finding and a limitation. The full list, split into same-quantity and related-quantity names (31 names, 11,295 curves over all x-axes), is in the data dictionary.
- **Rows before / after:** 136,679 in-scope curves; no rows changed. The 760 same-quantity curves are knowingly left out.
- **Validation:** each of the six exact names uses exactly one unit string in scope (for example `V*K^(-1)` for Seebeck, 36,939 curves); the variant counts were re-counted from the raw file and match.

## Medium severity

### 4. Curves with empty point arrays

- **Problem:** a curve record exists but its `x` and `y` arrays are empty (`[]`), so it has no data points.
- **Table / column:** `curves.x`, `curves.y`
- **Records affected:** 3,952 curves; 2,140 of them in scope.
- **Impact:** a training row without any points either breaks the pipeline or is silently dropped, which changes the sample counts per property.
- **Proposed treatment:** keep the curve record, flag it, and exclude it from any point-level modelling step.
- **Applied treatment:** flagged `has_points = FALSE`; `n_points` is null (not 0) because no point rows match in the join; no rows are produced in the point table.
- **Rows before / after:** curves 237,313 → 237,313 (3,952 flagged); in scope 136,679 → 136,679 (2,140 flagged, 134,539 with points).
- **Validation:** flag counts are 2,140 FALSE / 134,539 TRUE in scope; the point table has no row for any flagged curve.

### 5. Same DOI on different paper records

- **Problem:** several paper records share the same DOI, so the same paper may be registered more than once.
- **Table / column:** `papers.DOI`
- **Records affected:** 85 rows share 40 DOIs (45 surplus rows).
- **Impact:** duplicate paper records can put the same measurements into both the training and the test set, which inflates model scores (data leakage). It also breaks DOI as a join key.
- **Proposed treatment:** investigate whether these are true duplicates; group by DOI when splitting data; join on `SID`, never on `DOI`.
- **Applied treatment:** reported, not changed.
- **Rows before / after:** papers 56,495 → 56,495.
- **Validation:** duplicate count reproduced from the raw file; all joins in the pipeline use `SID`.

### 6. Orphans: SID not found in papers

- **Problem:** samples and curves reference paper IDs that do not exist in the `papers` table.
- **Table / column:** `samples.SID`, `curves.SID`
- **Records affected:** 9 samples and 31 curves, all pointing to 3 SIDs (8534, 8535, 9026). 28 of the 31 curves are in scope.
- **Impact:** without a paper record these curves cannot be traced to a source or grouped by paper for a leakage-safe split. The affected share is small: 28 of 136,679 in-scope curves (0.02%); 31 of 237,313 curves overall (0.01%).
- **Proposed treatment:** keep and flag them, so the problem stays visible and can be reported upstream. Dropping is irreversible.
- **Applied treatment:** left joins keep every row; an `is_orphan` flag marks the affected curves. Nothing is dropped.
- **Rows before / after:** samples 106,331 → 106,331 (9 flagged); curves 237,313 → 237,313 (31 flagged); in scope 136,679 → 136,679 (28 flagged).
- **Validation:** the flag is computed from the join, not hard-coded; 28 in scope is confirmed in Tableau and in a re-count from the raw files.

### 7. Publication date has variable precision

- **Problem:** the publication date is stored as JSON `{"date_parts":[[year, month, day]]}`, but many records have only year and month, or only a year, or no date.
- **Table / column:** `papers.issued`
- **Records affected:** 31,303 of 56,495 papers are not full dates: year-month 24,570, year only 6,526, no date 207 (20 empty `{}` plus 187 with an empty-string year `[[""]]`). One record (SID 31709) has the invalid month 0.
- **Impact:** forcing every date into `YYYY-MM-DD` would invent a month and day for more than half of the papers. That distorts any time-based split or time trend a model evaluation relies on.
- **Proposed treatment:** keep the precision: split into year, month and day and add a precision label.
- **Applied treatment:** `issued_year`, `issued_month`, `issued_day` and `issued_precision` (`YMD`, `YM`, `Y`, `Unknown`); missing parts stay null.
- **Rows before / after:** papers 56,495 → 56,495; precision counts 25,192 `YMD` / 24,570 `YM` / 6,526 `Y` / 207 `Unknown`.
- **Validation:** the same four counts in Tableau and in Python (Python pipeline, PR #20); no day or month is imputed. The invalid month in SID 31709 is an unresolved issue (see issue 20).

### 8. 170 property names and 69 units

- **Problem:** property names and units are free text. The table holds 170 distinct `prop_y` names, 146 distinct `prop_x` names and 69 distinct `unit_y` strings, with synonyms, spelling variants and four properties that carry more than one unit.
- **Table / column:** `curves.prop_y`, `prop_x`, `unit_x`, `unit_y`
- **Records affected:** the whole table.
- **Impact:** a model cannot treat values as comparable without first agreeing on property and unit. Cleaning all 170 names correctly is not possible within the project time.
- **Proposed treatment:** narrow the scope to a domain where values can be checked physically.
- **Applied treatment:** deep cleaning is limited to thermoelectric curves, the six core properties and temperature on the x-axis (136,679 of 237,313 curves, 57.6%). Thermoelectric is the largest domain (159,593 curves, 67%); inside it each core property uses exactly one unit.
- **Rows before / after:** 237,313 → 159,593 thermoelectric → 136,679 in scope.
- **Validation:** one unit string per core property in scope (checked on the raw file); distinct counts reproduced by the counting script.

### 9. `sample_info` often empty

- **Problem:** the nested sample descriptors (material family, fabrication process and so on) are empty for many samples.
- **Table / column:** `samples.sample_info`
- **Records affected:** content in 72,456 samples (68.14%); empty `{}` in 31,561 (29.68%); missing in 2,314 (2.18%). So 33,875 samples have no descriptor information.
- **Impact:** descriptors are useful model features, but about a third of the samples have none, so those features cannot be used for all samples. Even where the key is present the value is often blank.
- **Proposed treatment:** keep all samples; treat `{}` as "no information", not as complete; report completeness as 68.14%, not 97.82%.
- **Applied treatment:** kept; the completeness figure is stated correctly in the documentation.
- **Rows before / after:** samples 106,331 → 106,331.
- **Validation:** the three counts match the profiling notebook; no malformed JSON was found.

### 10. Flattening bug in our own pipeline

- **Problem:** when `sample_info` was flattened into columns, keys that differ only by spelling or spaces (for example `Measurement temperature` and ` Measurement temperature`) were written into the same column and one value silently overwrote the other. Example: `room` was replaced by an empty value.
- **Table / column:** `samples.sample_info`
- **Records affected:** 22,298 values in 15,786 records (review of the current pipeline code).
- **Expected effect of the fix (tested with our counting script):** with the variant mapping and the rule "keep the non-empty value", 15,063 (record, column) pairs have variants that differ. **15,020 of them are a value against an empty one, so nothing is lost.** Only **43 are genuine conflicts** with two different non-empty values (26 of them from one paper, SID 61072). The 43 are listed in `sample_info_merge_conflicts.csv` for review.
- **Impact:** recorded values are lost without a warning. Any model that uses the flattened descriptors would train on incomplete features. The Tier 2 output does not use the flattened columns, so the six-property model is not affected today.
- **Proposed treatment:** map the variants to one column, keep the non-empty value, and log every case where two different non-empty values exist. The test above shows this rule is safe: it keeps every recorded value except in the 43 conflicts, which are logged and can be reviewed by hand.
- **Applied treatment:** fix pending. Until then the Tier 2 output keeps `sample_info` as raw JSON and does not flatten it.
- **Rows before / after:** samples 106,331 → 106,331; overwritten values 22,298 today, target 0 after the fix.
- **Validation:** the mapping and rule were run on the full table: 15,063 differing pairs = 15,020 value-against-empty + 43 conflicts (listed in the conflict file). After the pipeline fix, the same conflict log and zero silent overwrites are required as evidence.

## Low severity

### 11. Timestamps stored as JavaScript text

- **Problem:** `created_at` and `updated_at` are strings such as `Thu Jan 25 2018 13:56:56 GMT+0900 (Japan Standard Time)`, which standard parsers do not read.
- **Table / column:** `created_at`, `updated_at` in papers, samples and curves (5 columns).
- **Records affected:** all rows in all five columns.
- **Impact:** the property values do not depend on these fields, so a model on the six properties is not affected. They matter for time-based splits and for lineage.
- **Proposed treatment:** parse to one time base (UTC).
- **Applied treatment:** parsed to UTC (`created_at_utc`, `updated_at_utc`); all source values carry the +0900 offset.
- **Rows before / after:** rows unchanged; 5 text columns gain 5 UTC columns.
- **Validation:** 0 parse failures and 0 nulls; the minimum and maximum are identical in Tableau and in Python (Python pipeline, PR #20) (2017-09-01 09:19:39 to 2026-09-30 08:34:52 UTC, all before the snapshot time); no record was updated before it was created.

### 12. `log(Electrical conductivity)` labelled with a linear unit

- **Problem:** curves named `log(Electrical conductivity)` carry the unit `S*m^(-1)`, which is the unit of the linear quantity. Conductivity elsewhere is written `ohm^(-1)*m^(-1)`, the same unit in a different notation.
- **Table / column:** `curves.prop_y`, `curves.unit_y`
- **Records affected:** 1,689 curves.
- **Impact:** outside the six exact property names, so no effect on the in-scope model. Mixed in by mistake, these values would be read as siemens per metre.
- **Proposed treatment:** keep out of scope; report to the data maintainers.
- **Applied treatment:** excluded by the exact-name filter and reported.
- **Rows before / after:** no rows changed.
- **Validation:** the in-scope conductivity curves all use `ohm^(-1)*m^(-1)` (18,839 curves).

### 13. `sample_info` keys with spelling and space variants

- **Problem:** descriptor keys contain typos, case differences and stray spaces (`coercivity`, ` coercivity`, `oercivity`; `Material family`, `Materials family`).
- **Table / column:** `samples.sample_info`
- **Records affected:** 138 raw keys; 128 after trimming spaces; 108 after merging the known variants.
- **Impact:** one attribute is split over several columns, so a feature looks sparser than it is. Not used by the six-property model.
- **Proposed treatment:** trim and map the variants to one column each, with the merge rule from the pipeline fix (keep the non-empty value, log conflicts).
- **Applied treatment:** mapping proposed and documented in the data dictionary; not yet decided by the team.
- **Rows before / after:** samples unchanged; 138 → 128 → 108 columns.
- **Validation:** key counts reproduced by the counting script.

### 14. `composition_details` mostly missing

- **Problem:** the additional composition text is empty for most samples.
- **Table / column:** `samples.composition_details`
- **Records affected:** 87,433 missing (82.23%).
- **Impact:** optional descriptive text; the composition itself is in `composition`. No effect on the six-property model.
- **Proposed treatment:** keep as null.
- **Applied treatment:** kept as null; no sample is dropped because of it.
- **Rows before / after:** 106,331 → 106,331.
- **Validation:** the missing count matches the profiling notebook.

### 15. Curve comments missing

- **Problem:** the comments and measurement conditions are empty for many curves. A further 87,594 rows hold the placeholder `"{}"`, an empty JSON object.
- **Table / column:** `curves.comments`
- **Records affected:** 103,868 missing (43.77%); including the placeholder, 191,462 curves (80.68%) have no real comment text.
- **Impact:** optional text. It can hold measurement conditions, but a model on the six properties does not need it.
- **Proposed treatment:** keep as null; treat the placeholder as "no comment".
- **Applied treatment:** kept as null; no curve is dropped because of it.
- **Rows before / after:** 237,313 → 237,313.
- **Validation:** the missing and placeholder counts were re-counted from the raw file.

### 16. Every CSV ends with a blank line

- **Problem:** all three files end with an extra empty line. pandas ignores it, but Tableau Prep reads it as one all-empty row.
- **Table / column:** all three files (papers, samples, curves).
- **Records affected:** one phantom row per file.
- **Impact:** one empty row would add a false record to counts and joins. It carries no values, so no effect on model inputs.
- **Proposed treatment:** remove the empty row in Tableau; log the difference between the two tools.
- **Applied treatment:** removed in Tableau; Python needs no step.
- **Rows before / after:** Tableau 56,496 / 106,332 / 237,314 → 56,495 / 106,331 / 237,313 (papers / samples / curves).
- **Validation:** counts equal the pandas counts after the filter.

### 17. Line breaks inside quoted text

- **Problem:** some `composition_details` texts contain line breaks inside quotation marks, so one record spans several physical lines.
- **Table / column:** `samples.composition_details`
- **Records affected:** 6,586 records, all in `composition_details` and all Windows line breaks (CRLF) (145,606 physical lines in the file for 106,331 records); none in papers or curves.
- **Impact:** a reader that ignores the quotation marks would split records and shift columns. With the text qualifier set, nothing is lost.
- **Proposed treatment:** set the text qualifier correctly in every reader.
- **Applied treatment:** handled by the text qualifier in Tableau and pandas.
- **Rows before / after:** 106,331 → 106,331.
- **Validation:** both tools return 106,331 samples with 9 columns.

### 18. README says "XXX License"

- **Problem:** the dataset README names a placeholder ("This dataset is provided under the XXX License") that contradicts the Figshare record.
- **Table / column:** `README.md`
- **Records affected:** not applicable.
- **Impact:** none on model inputs. It weakens the clarity of the usage rights at file level.
- **Proposed treatment:** treat the Figshare record as authoritative and ask the maintainers to correct the README.
- **Applied treatment:** documented as a defect. The licence used is CC BY 4.0, from the Figshare record and the written confirmation of the maintainers.
- **Rows before / after:** not applicable.
- **Validation:** Figshare record and the maintainers' email are on file; the README text is quoted in the FAIR assessment.

### 19. README file names and columns do not match the data

- **Problem:** the README uses `Curves.csv` / `all_curves.csv` while the files are `starrydata_curves.csv`. It also omits columns that exist (`composition_details`, `figure_name`, and `DOI` in curves) and lists properties that do not occur (for example "Z-Seebeck coefficient").
- **Table / column:** `README.md`
- **Records affected:** not applicable.
- **Impact:** none on model inputs; users need the data dictionary to read the files correctly.
- **Proposed treatment:** use the data dictionary as the reference and report the differences to the maintainers.
- **Applied treatment:** documented as a defect; the data dictionary supersedes the README.
- **Rows before / after:** not applicable.
- **Validation:** README columns compared one by one with the file headers.

### 20. One paper has publication month 0

- **Problem:** the paper with SID 31709 has the publication date `{"date_parts":[[2018,0]]}`. Month 0 does not exist. The record is kept as recorded and, because it has two date parts, it is classified as `YM` even though the month is invalid.
- **Table / column:** `papers.issued`
- **Records affected:** 1 paper (SID 31709). All other months are 1 to 12 and no day is invalid.
- **Impact:** negligible for the model. A single paper would carry a month that cannot be read as a date, and it counts as `YM` precision when only the year can be trusted.
- **Proposed treatment:** flag the record, and set the month to null so the paper is classified as year-only.
- **Applied treatment:** none; **unresolved issue.** The value is kept as recorded in both pipelines and the paper stays in the `YM` count (24,570). Reported as a limitation and to the maintainers.
- **Rows before / after:** papers 56,495 → 56,495. If the proposed fix were applied: `YM` 24,570 → 24,569 and `Y` 6,526 → 6,527.
- **Validation:** found by checking every month and day in the date parts against the calendar (1 invalid month, 0 invalid days).
- **Checked, not an error:** 44 papers have a publication year before 1950 (earliest 1885). They were checked and are genuine historical papers, so they are kept.

---

## Checks that passed

| Check | Table / column | Result | How validated |
|---|---|---|---|
| Curve array validity | curves.x, curves.y | All 237,313 arrays parse as JSON numbers: 0 failures, 0 length mismatches between `x` and `y`. Median 15 points per curve, maximum 804. | Parsed every row in Python; the point count equals the sum of array lengths (4,839,779). |
| Curve key uniqueness | curves (`figure_id`, `sample_id`) | 0 duplicates, 0 null `figure_id`, 0 fully duplicate rows. | Counted on the raw file; also holds with `SID` added. |
| Paper key | papers.SID | Unique, no nulls. | Profiling notebook. |
| Sample keys | samples.sample_id | Unique, no nulls; every curve's sample exists. | Profiling notebook and join check. |
| JSON syntax of `sample_info` | samples.sample_info | No malformed JSON. | Profiling notebook. |
| Early publication years | papers.issued | 44 papers before 1950, earliest 1885; checked and genuine, not an error. | Years read from every date and the oldest records reviewed. |