# Starrydata Data Dictionary

**Dataset snapshot:** `2026-10-01 02:00:01 UTC+0900 (JST)` (`db_snapshot.txt`)  
**Source DOI:** [10.6084/m9.figshare.34036677.v1](https://doi.org/10.6084/m9.figshare.34036677.v1)  
**Source files:** `starrydata_papers.csv`, `starrydata_samples.csv`, `starrydata_curves.csv`  
**Prepared by:** Data-Managers, SRH University of Applied Sciences Heidelberg  
**Version:** v0.3, 2026-11-07 (adds output columns; `n_points` null rule; curve key aligned; normalization marked as proposed)

## Scope and assumptions

Starrydata is a database of numerical property data digitized from plots in published papers. The upstream README describes thermoelectric, battery, and magnetic materials, but the snapshot is broader: paper-level `project_names` contain 14 distinct project labels (ThermoelectricMaterials, MagneticMaterials, DielectricMaterials, BatteryMaterials, LowThermalConductivityMaterials, PiezoelectricMaterials, GeneralDB, Resistor, CondensedMatter, HighThermalConductivityMaterials, Hypermaterial, OrganicThermoelectricMaterials, SolidStateBatteryMaterials, AirBatteryMaterials). Values were digitized from figures with WebPlotDigitizer and StarryDigitizer.

The data product is documented as three related tables (`papers`, `samples`, `curves`) to preserve the source relationships. The `sample_info` JSON in `samples` is retained as `sample_info_raw` for provenance. Flattening it into nullable descriptor columns is **proposed, not applied**: the key mapping is open decision D7, and no current output (including Tier 2) contains flattened descriptor columns. Under the proposal, a flattened descriptor column would contain the JSON `category` value; if no category is present, the source string or `extracted` value would be used. The original JSON preserves comments and any values not represented in flattened columns.


## Table relationships

| Table | Row grain | Key | Relationship |
|---|---|---|---|
| `papers` | One paper record | `SID` | `SID` is referenced by `samples` and `curves`. |
| `samples` | One material sample record | (`SID`, `sample_id`) | `SID` links to `papers`; the composite key relates samples to curves. |
| `curves` | One digitized curve | `curve_key` = (`figure_id`, `sample_id`) | `SID` links to `papers`; (`SID`, `sample_id`) links to `samples`. `figure_id` groups curves from the same figure. |
| `curve_points` (output) | One digitized point of one curve | (`figure_id`, `sample_id`, `point_index`) | (`figure_id`, `sample_id`) links to `curves.curve_key`. |

The profiling notebook found no duplicate or missing `SID` values in `papers`, and no duplicate or missing `sample_id` values in `samples` for this snapshot. Use (`SID`, `sample_id`) for the sample-to-curve relationship; this avoids relying on `sample_id` alone across other snapshots.

**Observed in the raw files (this snapshot):**
 
- (`figure_id`, `sample_id`) is unique across all 237,313 curve rows (0 duplicates, 0 null `figure_id`, 0 fully duplicate rows), so it is the agreed `curve_key` used in the pipeline contract. Adding `SID` changes nothing: each `figure_id` and each `sample_id` belongs to exactly one `SID`. No single column is unique.
- `figure_id` identifies one plot: each (`SID`, `figure_id`) has exactly one (`prop_x`, `prop_y`) pair. Median 3 curves per figure, maximum 52.
- Every curve's (`SID`, `sample_id`) pair exists in `samples` (0 unmatched), and `DOI` agrees between `curves`, `samples` and `papers` wherever they join (0 mismatches).
- `papers.DOI` is **not** unique: 85 rows share 40 DOIs (45 surplus rows). Join on `SID`, never on `DOI`.
- Coverage is uneven: 38,988 of 56,495 papers (69.0%) have no samples and 38,994 have no curves, so the `papers` table is a superset of the papers that have digitized data. 118 samples have no curves.

## `papers` Table

| Column | Logical type | Definition |
|---|---|---|
| `SID` | Integer identifier | Primary key - Starrydata identifier for a paper. |
| `DOI` | String | Digital Object Identifier of the source paper, when supplied. |
| `URL` | URL string | URL associated with the paper DOI. |
| `issued` | JSON object stored as string  | Publication date as `{"date_parts":[[year, month, day]]}`. The inner list has 3 elements for 25,192 rows, 2 (year-month) for 24,570, and 1 for 6,713 (6,526 with a year, 187 with an empty-string year); the object is empty (`{}`) for 20 rows. The processed output splits it into `issued_year`, `issued_month`, `issued_day` and `issued_precision` (see Output columns). |
| `author` | JSON array stored as string| Author records; each contain given name, family name, or affiliation data. |
| `title` | String | Title of the source publication. |
| `container_title` | String | Full journal, book, or other containing-work title. |
| `container_title_short` | String | Abbreviated title of the containing work. |
| `volume` | String | Volume value as recorded for the publication. |
| `issue` | String | Issue value as recorded for the publication. |
| `page` | String | Page range or page value as recorded for the publication. |
| `ISSN` | String | One or more comma-separated International Standard Serial Numbers (for example 0001-4842,1520-4898), if supplied. |
| `publisher` | String | Publisher name. |
| `project_names` | JSON array | Starrydata project labels associated with the paper. |
| `created_at` | Timestamp string | Time the paper record was created in Starrydata; JavaScript date string in JST (+0900). The processed output adds `created_at_utc` (see Output columns). |

## `samples` Table

| Column | Logical type | Definition |
|---|---|---|
| `sample_name` | String | Name or label assigned to the material sample. It usually differs from composition (the two are equal for only 9.5% of rows). Missing for 27 rows. |
| `sample_id` | Integer identifier | Starrydata sample identifier; use with `SID` to identify a sample across related records. |
| `composition` | String | Reported chemical composition or sample description. Missing for 191 rows. |
| `composition_details` | String | Additional composition or sample detail. Missing for 87,433 rows (82.23%). |
| `SID` | Integer identifier | Starrydata identifier of the paper describing the sample; foreign key to `papers.SID`. |
| `DOI` | String | DOI of the publication associated with the sample. |
| `created_at` | Timestamp string | Time the sample record was created; JavaScript date string in JST (+0900), same format as `papers.created_at`. The processed output adds `created_at_utc`. |
| `updated_at` | Timestamp string | Time the sample record was last updated; same format. The processed output adds `updated_at_utc` |
| `sample_info_raw` | JSON object stored as string | Original `sample_info` content (raw column name `sample_info`) retained unchanged for provenance, including category, comment, extracted text, and source-specific details. |


### Structure of `sample_info`

In the raw data every non-missing `sample_info` is a JSON object (72,456 populated, 31,561 empty `{}`, 2,314 missing). Each key is a sample descriptor, and each value is one of:

- an object `{"category": "", "comment": ""}` (592,384 key-value pairs);
- an object `{"category": "", "comment": "", "extracted": ""}` (618,550 pairs), where `extracted` holds text extracted from the paper;
- a plain string (130,186 pairs, most of them empty).

Many descriptor values are empty strings even when the key is present, so a key being present does not mean a value was recorded; Appendix A lists both counts.

### Source-key normalization proposed for flattened names (D7, not applied)

This mapping is a proposal under open decision D7. It is not applied in any current output. Under the proposal, all keys would first be trimmed of leading/trailing whitespace (spaces and tabs) and repeated internal whitespace collapsed. The following obvious variations would then be consolidated into one output column, keeping the non-empty value and logging conflicts (43 genuine conflicts in this snapshot, listed in `sample_info_merge_conflicts.csv`); original spellings stay in `sample_info_raw`:

| Output column | Source-key variants consolidated |
|---|---|
| `Measurement temperature` | Case and whitespace variants, including `Measurement temperatur` and trailing-tab/leading-space variants. |
| `Remanence magnetization` | `remanence magnetion`, `emanence magnetion`, and whitespace/case variants. |
| `Saturation magnetization` | `saturation magnetizatio` and capitalization variants. |
| `Coercivity` | `coercivity`, `oercivity`, and leading-space variant. |
| `MaterialFamily` | `Material family`, `Material Family`, `Materials family`, `MaterialsFamily`, `MaterialFarmily`, and whitespace variants. |
| `ThermalMeasurement` | `Thermal Measurement` and `ThermalMeaasurement`. |
| `ElectricalMeasurement` | `Electrical Measurement`. |
| `DifferentialThermalAnalyzer` | `Differential thermal analyzer`. |
| `DataType` | `Data Type`. |
| `GrainSize` | `Grain size`. |
| `RelativeDensity` | `Relative density`. |
| `OrganicFabricationProcess` | `Organic Fabrication Process`. |
| `OrganicMaterialFamily` | `Organic Material Family`. |
| `N/P ratio\|A/C ratio` | `N/P ratio\| A/C ratio` (space after the pipe). |
| `magnetic field` | ` magnetic field` (leading space). |
| `Maximum power` | `Maximum power ` (trailing space). |

Proposed to stay separate (not merged): laser flash and different thermal analyzer, LaserFlash and DifferentialThermalAnalyzer (similar names but distinct source keys), and Sintering temperature (dielectric project) versus sintering temperature (hypermaterial project), which differ only by case but come from different projects. Proposed output column names reproduce the source spelling after trimming, so they mix CamelCase, spaces and special characters (/, |, parentheses); rename to a consistent style such as snake_case if the columns are loaded into a SQL database.


## `curves` Table

| Column | Logical type | Definition |
|---|---|---|
| `SID` | Integer identifier | Starrydata identifier of the source paper; foreign key to `papers.SID`. |
| `DOI` | String | DOI of the source paper. |
| `composition` | String | Composition associated with the curve. Missing for 362 rows. |
| `sample_id` | Integer identifier | Sample identifier; use with `SID` to link to `samples`. Part of `curve_key`. |
| `figure_id` | Integer identifier | Identifier used to group curves associated with one figure (one `prop_x`/`prop_y`pair per figure). Part of `curve_key`. |
| `figure_name` | String | Figure or panel label as recorded in the source paper. Never missing. |
| `prop_x` | String | Name of the property represented on the x-axis. Free-text vocabulary: 146 distinct values (see Appendix B) |
| `prop_y` | String | Name of the property represented on the y-axis. Free-text vocabulary: 170 distinct values, including synonyms and spelling variants (see Appendix B). |
| `unit_x` | String | Unit for x-axis values: normalized, mostly SI-based unit strings (38 distinct values; - means dimensionless). |
| `unit_y` | String | Unit for y-axis values, same notation (69 distinct values). |
| `x` | JSON array of numbers stored as string | Ordered digitized x-axis values for one curve. |
| `y` | JSON array of numbers stored as string | Ordered digitized y-axis values corresponding position-by-position to `x`. |
| `created_at` | Timestamp string | Time the curve record was created; JavaScript date string in JST (+0900). The processed output adds created_at_utc |
| `updated_at` | Timestamp string | Time the curve record was last updated; same format. The processed output adds updated_at_utc |
| `project_names` | JSON array | Starrydata project labels associated with the curve. Never empty. |
| `comments` | String | Source comments or measurement conditions recorded for the curve. Stored as a JSON-encoded string; some contain nested JSON key-value text (for example temperature or field conditions). See the placeholder note in the profiling results. |

### Flags added in the Tableau and Python Tier 2 outputs
 
Orphan records are **flagged, not dropped**: left joins keep every curve. The flags below appear in the Tier 2 outputs (`tier2_curves.csv`, `tier2_points.csv`). The other added output columns are specified in the section *Output columns added by the pipeline* below.
 
| Field | Type | Definition | Unit | Constraints | Missing value means | Source column | Transformation (cleaning-log step) |
|---|---|---|---|---|---|---|---|
| `is_orphan` | Boolean | `TRUE` when the curve's `SID` does not exist in `papers` (the curve cannot be linked to its paper). | n/a | **28** `TRUE` among the 136,679 Tier 2 curves (31 across all 237,313 curves). Must be computed from the join, not hard-coded. | Not expected. | `curves.SID` joined to `papers.SID` | Left join plus a null test on the paper side.  |
| `n_points` | Integer (nullable) | Number of points in the curve's `x`/`y` arrays. | Count | ≥ 1 when present. **Null, not 0**, for the 2,140 Tier 2 curves with empty arrays, because no `curve_points` rows match in the join. Both pipelines must write null so that the Tableau/Python null-count comparison agrees. | The curve has empty `x`/`y` arrays (no points). | `curves.x` | Count of matching `curve_points` rows on `curve_key`; the left join leaves null where nothing matches.  |
| `has_points` | Boolean | `TRUE` when the curve has at least one point. | n/a | **2,140** `FALSE` among Tier 2 curves (these are empty arrays; 134,539 are `TRUE`). | Not expected. | `curve_points` joined on `curve_key` | `TRUE` when `n_points` is not null, else `FALSE`.  |
 
The 28 Tier 2 orphan curves were re-counted from the raw files and match the tracker.
 
All other `curves` columns keep the definitions given in the `curves` table above.

## Output columns added by the pipeline

These columns are created by the Tableau Prep flow and the Python pipeline; the source columns are kept alongside them. The complete Tier 2 column list (34 columns) is defined in the Python Tier 2 output specification (Aditya Pawar); this section specifies every column there that does not exist in the raw files.

### Timestamp columns (`papers`, `samples`, `curves`)

| Field | Type | Definition | Unit | Constraints | Missing value means | Source column | Transformation (cleaning-log step) |
|---|---|---|---|---|---|---|---|
| `created_at_utc` | Timestamp (UTC) | Time the record was created in Starrydata, converted to UTC. Present in `papers`, `samples` and `curves`. | Date-time, UTC | 0 parse failures; all values before the snapshot time (2026-09-30 17:00:01 UTC). Across all five timestamp columns the range is 2017-09-01 09:19:39 to 2026-09-30 08:34:52 UTC. | Not expected (0 nulls). | `created_at` | JavaScript date string parsed; +0900 (JST) offset converted to UTC (issue register #11). |
| `updated_at_utc` | Timestamp (UTC) | Time the record was last updated, converted to UTC. Present in `samples` and `curves` (`papers` has no `updated_at`). | Date-time, UTC | ≥ `created_at_utc` for every record (no record was updated before it was created). | Not expected (0 nulls). | `updated_at` | As for `created_at_utc` (issue register #11). |

### Publication date columns (`papers`)

| Field | Type | Definition | Unit | Constraints | Missing value means | Source column | Transformation (cleaning-log step) |
|---|---|---|---|---|---|---|---|
| `issued_year` | Integer (nullable) | Publication year. | Year | Earliest 1885 (44 papers before 1950, checked and genuine). | No usable date (207 papers: 20 `{}`, 187 empty-string year). | `issued` | First element of `date_parts` (issue register #7). |
| `issued_month` | Integer (nullable) | Publication month. | Month (1–12) | 1–12, except SID 31709, which carries the invalid month 0 as recorded (issue register #20). | The source gives only a year, or no date. Never imputed. | `issued` | Second element of `date_parts`, if present. |
| `issued_day` | Integer (nullable) | Publication day. | Day (1–31) | Valid calendar day (0 invalid days found). | The source gives no day. Never imputed. | `issued` | Third element of `date_parts`, if present. |
| `issued_precision` | String (category) | How precise the source date is. | n/a | One of `full` (25,192), `year-month` (24,570), `year` (6,526), `none` (207). | Not expected. | `issued` | Derived from the number of non-empty date parts. |

### `curve_points` (Python output, read by Tableau Prep) and `tier2_points`

`curve_points.csv` holds one row per digitized point: 4,839,779 rows from the 233,361 curves that have points. `tier2_points.csv` is its Tier 2 subset (2,337,212 rows from 134,539 curves) and additionally carries `prop_y` and `unit_y` from the joined curve.

| Field | Type | Definition | Unit | Constraints | Missing value means | Source column | Transformation (cleaning-log step) |
|---|---|---|---|---|---|---|---|
| `figure_id` | Integer | Figure identifier of the curve the point belongs to; part of `curve_key`. | n/a | Every (`figure_id`, `sample_id`) exists in raw `curves`. | Not expected. | `curves.figure_id` | Copied when the arrays are unpacked (issue register #2). |
| `sample_id` | Integer | Sample identifier of the curve; part of `curve_key`. | n/a | As above. | Not expected. | `curves.sample_id` | Copied when the arrays are unpacked. |
| `point_index` | Integer | Position of the point within the source `x`/`y` arrays; preserves the digitized order. | n/a | (`figure_id`, `sample_id`, `point_index`) is unique. Index base (0 or 1) as defined in the Python output specification. | Not expected. | Array position in `curves.x` / `curves.y` | Generated during unpacking. |
| `x_value` | Float | Digitized x-axis value of the point. | The curve's `unit_x`; K for every Tier 2 point. | Numeric; row count equals the sum of array lengths. | Not expected. | `curves.x` | JSON array unpacked, one element per row. |
| `y_value` | Float | Digitized y-axis value at the same position as `x_value`. | The curve's `unit_y`. | Numeric; `x` and `y` arrays have equal length in every source row. | Not expected. | `curves.y` | JSON array unpacked, one element per row. |
| `prop_y` (`tier2_points` only) | String | y-axis property of the point's curve. | n/a | One of the six exact core names (Seebeck coefficient, Electrical conductivity, Electrical resistivity, Thermal conductivity, Power factor, ZT). | Not expected. | `curves.prop_y` | Joined from `curves` on `curve_key`; Tier 2 filter (issue register #1, #3, #8). |
| `unit_y` (`tier2_points` only) | String | Unit of `y_value`. | n/a | Exactly one unit string per core property in scope (for example `V*K^(-1)` for Seebeck coefficient). | Not expected. | `curves.unit_y` | Joined from `curves` on `curve_key`. |



## Data Profiling Results 

The following results are from `01_data_profiling.ipynb` and describe the raw tables before cleaning or flattening. All were re-checked against the raw CSV files.
 
| Table / field | Profile result | Meaning for use |
|---|---|---|
| `papers` | 56,495 rows; 15 columns; `SID` is unique and has no nulls. | `SID` is suitable as the paper-table primary key in this snapshot. |
| `samples` | 106,331 rows; 9 columns; `sample_id` is unique and has no nulls. | Preserve `SID` with `sample_id` when linking samples to curves. |
| `curves` | 237,313 rows; 16 columns. | One row represents one digitized curve. |
| Line breaks inside `samples.composition_details` | 6,586 of the 106,331 sample records contain line breaks (all Windows CRLF) inside the quoted `composition_details` text (145,606 physical lines in the file); no other column in any of the three files does. | Quoted text qualifiers must be honoured by every reader. Parsed correctly by pandas and Tableau Prep. Corrects the 06 Nov statement of "0 line breaks inside fields". |
| Row counts in Tableau Prep | Each CSV ends with an extra blank line (`\n\n`). pandas skips it; Tableau Prep reads it as one all-empty row and shows 56,496 / 106,332 / 237,314 rows until it is filtered (tracker O27). | The counts above are pandas counts. Log the difference wherever the two tools are compared. |
| `samples.sample_info` | 72,456 valid JSON objects (68.14%); 31,561 empty objects (29.68%); 2,314 missing values (2.18%); no malformed JSON was found. | If flattened (D7), use null for unavailable attributes and retain the sample rows. Effective completeness is 68.14%, not 97.82%, because `{}` carries no information. |
| `samples.composition_details` | 87,433 missing (82.23%). | Keep the field nullable; do not drop samples solely because this optional description is missing. |
| `curves.comments` | 103,868 missing (43.77%). A further 87,594 rows hold the placeholder `"{}"` (an empty JSON object). | Treat both as "no comment": 191,462 rows (80.68%) carry no real comment text. Keep the field nullable; do not drop curve measurements solely because comments are absent. |
| Referential integrity: `samples` → `papers` | 9 orphan sample rows referencing 3 absent SIDs: `8534`, `8535`, `9026`. | Flag or quarantine these rows before an inner join; document any exclusion. |
| Referential integrity: `curves` → `papers` | 31 orphan curve rows referencing the same 3 absent SIDs. | Flag or quarantine these rows before an inner join; document any exclusion. |
| `curves.x`, `curves.y` | **Verified:** all 237,313 `x` and `y` cells parse as JSON arrays of numbers (0 failures, no nulls or strings), and `x` and `y` have equal length in every row (0 mismatches). 3,952 curves (1.67%) have empty arrays; 4,561 have a single point; the median curve has 15 points and the maximum is 804. | Safe to parse with `json.loads`. Empty-array curves yield no points and are flagged; single-point curves can be filtered if a model needs at least two points. |
| `papers.DOI` | 0 missing; 85 rows share 40 duplicated DOIs. | Not a key; use `SID`. |
| `papers.issued` | 207 papers have no usable date (20 `{}` plus 187 empty-string years); 6,526 are year-only, 24,570 year-month (one of them with the invalid month 0), 25,192 full. Corrects the earlier 6,713 year-only figure (tracker O17). | Keep precision explicit; do not force a full date. |
 
Other missingness reported by the notebook:
 
| Table | Column | Missing | % |
|---|---|---|---|
| `papers` | `issue` | 3,873 | 6.86 |
| `papers` | `page` | 2,266 | 4.01 |
| `papers` | `ISSN` | 1,901 | 3.36 |
| `papers` | `container_title_short` | 1,575 | 2.79 |
| `papers` | `volume` | 1,451 | 2.57 |
| `papers` | `publisher` | 20 | 0.04 |
| `papers` | `author` | 16 | 0.03 |
| `papers` | `container_title` | 1 | 0.00 |
| `samples` | `composition` | 191 | 0.18 |
| `samples` | `sample_name` | 27 | 0.03 |
| `curves` | `composition` | 362 | 0.15 |
 
All other columns have no missing values. The notebook's key and referential checks report zero missing `SID` values in child tables.

## Appendix A: Proposed flattened `sample_info` descriptor columns (D7)

The raw `sample_info` objects contain 138 distinct descriptor keys; after trimming and the proposed normalization above (D7, not yet applied) they would become 108 output columns. All are nullable. "Samples with key" counts samples whose `sample_info` contains the descriptor; "Samples with a value" counts those where the flattened value (category, else extracted text or string) is non-empty. Groups are assigned by the project label of the papers where the descriptor is populated. Descriptor meanings follow the column names, and the JSON `category` holds the selected value and `comment` holds free text.

#### General and thermoelectric sample descriptors

| Output column | Source keys merged | Samples with key | Samples with a value |
|---|---|---|---|
| `DataType` | 2 | 54,832 | 48,721 |
| `Form` | 1 | 54,760 | 40,355 |
| `FabricationProcess` | 1 | 53,648 | 31,673 |
| `FabricationProcess 2` | 1 | 18,127 | 1,821 |
| `FabricationProcess 3` | 1 | 17,683 | 133 |
| `Purity` | 1 | 52,732 | 20,629 |
| `RelativeDensity` | 2 | 52,644 | 2,446 |
| `GrainSize` | 2 | 52,605 | 1,508 |
| `MaterialFamily` | 7 | 37,500 | 22,140 |
| `ElectricalMeasurement` | 2 | 36,705 | 14,420 |
| `ThermalMeasurement` | 3 | 36,581 | 10,201 |
| `Other` | 1 | 26,422 | 1 |
| `laser flash and different thermal analyzer` | 1 | 26,294 | 2 |
| `DifferentialThermalAnalyzer` | 2 | 26,294 | 23 |
| `LaserFlash` | 1 | 26,293 | 16 |
| `Composition conversion` | 1 | 3,270 | 2 |
| `Measurement axis` | 1 | 3,270 | 2 |
| `AbsoluteDensity` | 1 | 635 | 133 |
| `PoreSize` | 1 | 635 | 25 |
| `Porosity` | 1 | 635 | 93 |
| `ClosedPorosity` | 1 | 635 | 0 |
| `OrganicMaterialFamily` | 2 | 342 | 342 |
| `OrganicFabricationProcess` | 2 | 325 | 313 |
| `OrganicFabricationProcess 2` | 1 | 53 | 49 |

#### Magnetic descriptors

| Output column | Source keys merged | Samples with key | Samples with a value |
|---|---|---|---|
| `MagneticMeasurement` | 1 | 16,352 | 16,121 |
| `Coercivity` | 3 | 15,822 | 1,414 |
| `Saturation magnetization` | 4 | 15,822 | 1,189 |
| `Remanence magnetization` | 4 | 15,822 | 915 |
| `Measurement temperature` | 5 | 15,821 | 11,879 |
| `magnetic field` | 2 | 15,821 | 863 |

#### Battery descriptors

| Output column | Source keys merged | Samples with key | Samples with a value |
|---|---|---|---|
| `Anode active material` | 1 | 14,292 | 12,165 |
| `Solvent 1` | 1 | 14,291 | 13,711 |
| `Solute 1` | 1 | 14,291 | 12,985 |
| `Cathode active material` | 1 | 14,254 | 9,152 |
| `Cathode conductive agent` | 1 | 14,176 | 8,190 |
| `Cathode binder 1` | 1 | 14,172 | 8,164 |
| `Cathode areal density (cathode loading)` | 1 | 14,037 | 7,197 |
| `Solvent 2` | 1 | 13,936 | 9,721 |
| `Solute 2` | 1 | 13,817 | 5,625 |
| `Ratio of electrolyte to cathode active material` | 1 | 13,795 | 2,195 |
| `Cathode binder 2` | 1 | 13,775 | 369 |
| `Anode binder 1` | 1 | 13,770 | 1,353 |
| `Solvent 3` | 1 | 13,756 | 1,070 |
| `Solute 3` | 1 | 13,740 | 159 |
| `Anode binder 2` | 1 | 13,729 | 21 |
| `Cathode volumetric density` | 1 | 13,727 | 0 |
| `Cathode additive 1` | 1 | 13,462 | 4,014 |
| `Anode conductive agent` | 1 | 13,449 | 1,321 |
| `Cathode additive 2` | 1 | 13,427 | 217 |
| `Anode additive 1` | 1 | 13,423 | 399 |
| `Anode additive 2` | 1 | 13,412 | 25 |
| `Cathode areal capacity` | 1 | 13,406 | 0 |
| `Separator` | 1 | 10,820 | 8,106 |
| `Cathode current collector` | 1 | 10,765 | 1,427 |
| `Cell type` | 1 | 10,708 | 5,663 |
| `Lower voltage limit` | 1 | 10,648 | 3,012 |
| `Upper voltage limit` | 1 | 10,637 | 2,983 |
| `Electrolyte additive 1` | 1 | 10,380 | 2,779 |
| `Current density` | 1 | 10,366 | 2,344 |
| `Anode current collector` | 1 | 10,337 | 2,044 |
| `Anode areal capacity` | 1 | 10,306 | 2,118 |
| `Coulombic efficiency` | 1 | 10,283 | 355 |
| `Electrolyte additive 2` | 1 | 10,279 | 31 |
| `N/P ratio\|A/C ratio` | 2 | 10,278 | 4 |
| `Electrolyte additive 3` | 1 | 9,958 | 0 |
| `Counter electrode` | 1 | 8,096 | 1,859 |
| `Reference electrode` | 1 | 8,076 | 960 |
| `Scan rate` | 1 | 8,061 | 0 |
| `Working electrode` | 1 | 8,061 | 426 |
| `Hysteresis` | 1 | 2,844 | 0 |
| `Cathode catalyst material` | 1 | 511 | 0 |
| `Catalyst loading` | 1 | 406 | 0 |
| `Redox mediator in electrolyte` | 1 | 353 | 0 |
| `Redox mediator in cathode` | 1 | 329 | 0 |
| `Cathode additive` | 1 | 329 | 0 |

#### Dielectric-project descriptors

| Output column | Source keys merged | Samples with key | Samples with a value |
|---|---|---|---|
| `Synthesis method1` | 1 | 1,656 | 98 |
| `Synthesis method2` | 1 | 1,656 | 65 |
| `Synthesis method3` | 1 | 1,656 | 47 |
| `Final product` | 1 | 1,656 | 60 |
| `Sintering method` | 1 | 1,656 | 54 |
| `Sintering temperature` | 1 | 1,656 | 95 |
| `Sintering time` | 1 | 1,656 | 88 |
| `Measurement method1` | 1 | 1,656 | 99 |
| `Measurement method2` | 1 | 1,656 | 98 |
| `Measurement method3` | 1 | 1,656 | 97 |
| `Chemical composition` | 1 | 1,656 | 81 |
| `Sample form` | 1 | 1,656 | 31 |
| `Starting material` | 1 | 1,656 | 96 |

#### Hypermaterial, condensed-matter and one-off descriptors

| Output column | Source keys merged | Samples with key | Samples with a value |
|---|---|---|---|
| `sintering temperature` | 1 | 1,103 | 24 |
| `lattice parameter` | 1 | 1,103 | 47 |
| `direction` | 1 | 1,103 | 43 |
| `composition type` | 1 | 1,103 | 599 |
| `annealing condition` | 1 | 1,095 | 386 |
| `sample info` | 1 | 1,092 | 387 |
| `other sample process info` | 1 | 1,092 | 616 |
| `other sample process info 2` | 1 | 956 | 33 |
| `6: other sample process info` | 1 | 114 | 1 |
| `AC/QC type` | 1 | 1,073 | 1,030 |
| `measurement condition` | 1 | 1,026 | 511 |
| `Applied field` | 1 | 680 | 9 |
| `2D iron-tetracyanoquinodimethane` | 1 | 156 | 1 |
| `comment` | 1 | 12 | 12 |
| `Peak efficiency` | 1 | 2 | 2 |
| `Maximum power` | 2 | 2 | 2 |
| `Module operated temperature` | 1 | 2 | 2 |
| `Note` | 1 | 1 | 1 |
| `Mn15Si26[001]` | 1 | 1 | 1 |
| `synthesis` | 1 | 1 | 1 |
## Appendix B: Property and unit vocabulary in `curves`

`prop_x` and `prop_y` are free-text names entered during digitization, so the same quantity can appear under several names (for example `Seebeck coefficient`, `thermopower`, `Thermopower` and `S`; or `Electrical resistivity`, `log(Electrical resistivity)`, `ln(Electrical resistivity)` and `Log(row)`). The tables below are generated by the script.
 
### B.1 Most frequent `prop_y` values with their most common unit
 
| `prop_y` | Most common `unit_y` | Curves |
|---|---|---|
| `Seebeck coefficient` | `V*K^(-1)` | 38,557 |
| `Thermal conductivity` | `W*m^(-1)*K^(-1)` | 25,799 |
| `Voltage` | `V` | 23,652 |
| `Electrical resistivity` | `ohm*m` | 23,100 |
| `Electrical conductivity` | `ohm^(-1)*m^(-1)` | 22,260 |
| `ZT` | `-` | 20,924 |
| `Power factor` | `W*m^(-1)*K^(-2)` | 18,195 |
| `magnetization_per_weight` | `emu*g^(-1)` | 13,809 |
| `Dielectric permittivity (ε’)` | `-` | 9,997 |
| `Discharge capacity` | `A*s/kg` | 9,796 |
| `Lattice thermal conductivity` | `W*m^(-1)*K^(-1)` | 6,876 |
| `Dielectric loss (tanδ)` | `-` | 5,298 |
| `Carrier concentration` | `m^(-3)` | 2,045 |
| `log(Electrical conductivity)` | `S*m^(-1)` | 1,989 |
| `magnetization_per_volume` | `A/m` | 1,564 |
| `Magnetization` | `T` | 1,511 |
| `Carrier mobility` | `m^2*V^(-1)*s^(-1)` | 1,378 |
| `Coulombic efficiency` | `-` | 958 |
| `Hall coefficient` | `m^3*C^(-1)` | 713 |
| `Electronic thermal conductivity` | `W*m^(-1)*K^(-1)` | 653 |
 
### B.2 Most frequent `prop_x` values with their most common unit
 
| `prop_x` | Most common `unit_x` | Curves |
|---|---|---|
| `Temperature` | `K` | 174,775 |
| `Magnetic field strength (H)` | `A/m` | 11,079 |
| `Cycle number` | `-` | 9,657 |
| `Discharge capacity` | `A*s/kg` | 9,020 |
| `Charge capacity` | `A*s/kg` | 8,813 |
| `Inverse temperature` | `K^(-1)` | 6,441 |
| `Magnetic field` | `T` | 4,819 |
| `C rate` | `-` | 2,729 |
| `Time` | `s` | 2,240 |
| `Areal capacity` | `A*s/m**2` | 906 |
 
Four `prop_y` values carry more than one unit (`Hall mobility`, `log(Electrical resistivity)`, `logσT`, `magnetization_per_weight`), so check `unit_y` per row.
 
### B.3 Property variants excluded from Tier 2 (reported as a finding)
 
**These names are excluded from Tier 2 and reported as a finding; none of them is merged, renamed or converted.** Tier 2 matches the six core names exactly. The table lists the near-matches found among the 159,593 thermoelectric curves: 31 names on 11,295 curves. The "Reading" column is a suggestion only; deciding whether a name really is the same quantity needs a domain check, and a unit label that looks wrong is reported as recorded.
 
**Group 1: same quantity under another name (12 names, 861 curves).** These curves measure the same property as one of the six core names, but are written differently or carry a wrong unit. They are the candidates for a later merge; a merge needs unit conversion and a check per variant.
 
| Core property | Excluded name | Curves | Recorded `unit_y` | Reading |
|---|---|---|---|---|
| Seebeck coefficient | `thermopower` | 552 | `V*K^(-1)` | Another name for the Seebeck coefficient |
| Seebeck coefficient | `S` | 71 | `V/K` | Symbol only; another name for the Seebeck coefficient |
| Seebeck coefficient | `Thermopower` | 54 | `kg*m**2/A/s**3` | Another name for the Seebeck coefficient; **unit error**, `kg*m**2/A/s**3` is the volt, not V/K |
| Seebeck coefficient | `Calculated Seebeck coefficient` | 6 | `V/K` | Same quantity, but calculated rather than measured |
| Seebeck coefficient | `Seebeck  coefficient` | 6 | `V` | Spelling variant (double space, trailing space); unit is volts, not V/K |
| Seebeck coefficient | `Seebeck coefficient at 550 K` | 1 | `m**2*kg/A/s**3/K` | Same quantity; the name carries a condition |
| Seebeck coefficient | `zero-B thermopower` | 1 | `m**2*kg/A/s**3/K` | Same quantity; the name carries a condition (zero magnetic field) |
| Electrical conductivity | `Conductivity` | 16 | `S/m` | Another name for the electrical conductivity |
| Electrical conductivity | `conductivity` | 2 | `-` | Another name for the electrical conductivity; **unit error**, unit recorded as `-` |
| Electrical resistivity | `Resistivity` | 14 | `ohm*m^-1` | Another name for the electrical resistivity; **unit error**, written `ohm*m^-1` instead of `ohm*m` |
| Thermal conductivity | `total thermal conductivity` | 134 | `W*m^(-1)*K^(-1)` | Another name for the thermal conductivity |
| ZT | `Figure of merit Zt` | 4 | `K^(-1)` | Name says ZT, but the unit `K^(-1)` belongs to Z; **unit error** |
 
**Group 2: related quantity, not the same (19 names, 10,434 curves).** These are logarithms, components, products or different quantities that only look like a core property. They must not be merged into it.
 
| Core property | Excluded name | Curves | Recorded `unit_y` | Reading |
|---|---|---|---|---|
| Electrical conductivity | `log(Electrical conductivity)` | 1,689 | `S*m^(-1)` | Logarithm of the quantity, labelled with a linear unit |
| Electrical conductivity | `ln(Electrical conductivity)` | 133 | `S*m^(-1)` | Natural logarithm, labelled with a linear unit |
| Electrical conductivity | `σT` | 6 | `A**2*s**3*K/kg/m**3` | Conductivity times temperature |
| Electrical conductivity | `Electrical conductivity0` | 5 | `A**2*s**2/kg/m**2` | Unclear name; the unit does not match siemens per metre |
| Electrical conductivity | `log(sigma)` | 4 | `A**2*s**3/kg/m**3` | Logarithm of the quantity |
| Electrical conductivity | `Surface Conductivity` | 3 | `ohm^(-1)` | Different quantity (surface, not bulk) |
| Electrical resistivity | `log(Electrical resistivity)` | 189 | `ohm*m` | Logarithm of the quantity, labelled with a linear unit |
| Electrical resistivity | `ln(Electrical resistivity)` | 150 | `ohm*m` | Natural logarithm, labelled with a linear unit |
| Electrical resistivity | `Log(row)` | 15 | `ohm*m` | Logarithm of the resistivity ("row" for the symbol ρ) |
| Electrical resistivity | `Contact resistivity` | 6 | `ohm*m^2` | Different quantity (contact, not bulk) |
| Thermal conductivity | `Lattice thermal conductivity` | 6,829 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity |
| Thermal conductivity | `Electronic thermal conductivity` | 647 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity |
| Thermal conductivity | `Carrier thermal conductivity` | 102 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity |
| Thermal conductivity | `electron thermal conductivity` | 99 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity (electronic) |
| Thermal conductivity | `Lattice+bipolar thermal conductivity` | 12 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity |
| Thermal conductivity | `Electrical thermal conductivity` | 3 | `W*m^(-1)*K^(-1)` | Component of the thermal conductivity (electronic) |
| ZT | `Figure of merit Z` | 501 | `K^(-1)` | Z = ZT / T; unit `K^(-1)` matches Z, so a different quantity from ZT |
| ZT | `Figure of merit` | 40 | `K^(-1)` | Unit `K^(-1)` points to Z, so a different quantity from ZT |
| ZT | `Figure of merit Z 1000` | 1 | `K^(-1)` | As above, with a condition in the name |
 
No name variants were found for `Power factor`.

**x-axis variants.** 141,910 thermoelectric curves carry one of the six exact core names; 136,679 are kept in Tier 2 because their `prop_x` is `Temperature`, and **5,231 are excluded by the x-axis rule**: `Inverse temperature` (3,693), `Carrier concentration` (701), `1000/T` (193), `T` (191, a candidate synonym of `Temperature`), `Electrical conductivity` (43), and 62 further `prop_x` names on 410 curves.

## Reproducibility
 
`dictionary_appendix_counts.py` reads the three raw CSVs (never modifies them) and regenerates every count in Appendix A and B and the verification figures quoted in the field specification and profiling sections.
 
```
python dictionary_appendix_counts.py --data-dir data/raw --out-dir docs/evidence/dictionary_counts
```
 
| Output | Content |
|---|---|
| `summary.json` | Headline figures (key counts 138 / 128 / 108, Tier 2 and `curve_points` counts, UTC reference values, `issued` precision counts) and the SHA-256 of each raw file |
| `appendix_a.md`, `appendix_a_descriptors.csv` | Appendix A tables and the same data as CSV |
| `appendix_a_merge_report.csv`, `sample_info_merge_conflicts.csv` | How often variant keys co-occur per column, and the 43 logged conflicts |
| `appendix_b.md`, `appendix_b_prop_y.csv`, `appendix_b_prop_x.csv` | Property and unit vocabulary |
| `tier2_excluded_variants.csv` | The data behind Appendix B.3 |
| `unit_notations.csv` | One unit written in several notations (for example siemens per metre in three), used as evidence in the FAIR assessment (I2) |
 

## References

- Figshare snapshot: <https://doi.org/10.6084/m9.figshare.34036677.v1>
- Starrydata dataset documentation and field descriptions: <https://starrydata.github.io/hp/en/manual/download/>
- Local source files used: `README(2).md`, `db_snapshot(1).txt`, and the three CSV files.
- Y. Katsura, M. Kumagai, T. Mato, et al., "Starrydata: from published plots to shared materials data", *Science and Technology of Advanced Materials: Methods* 5(1), 2506976 (2025). <https://doi.org/10.1080/27660400.2025.2506976>
- Original publications: the DOIs in `starrydata_papers.csv` (the `DOI` column is preserved in all outputs).
- Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 
- Canonical file names: `starrydata_papers.csv`, `starrydata_samples.csv`, `starrydata_curves.csv`, `README.md`, `db_snapshot.txt`, `01_data_profiling.ipynb`, `dictionary_appendix_counts.py`.

SHA-256 of the raw files:
 
| File | SHA-256 |
|---|---|
| `starrydata_papers.csv` | `b82ff398b28c15e42aa6ef6de1df9c26f3935a00dd9c76925e9dbbf1a6b4e222` |
| `starrydata_samples.csv` | `744b1b496368c0ed24231073ae324a2ef302076801331abb0f9c69dcf9754f55` |
| `starrydata_curves.csv` | `411515829de82041809e112a30d55c676567972c80a95965c37feb1b1ef41c96` |
| `README.md` | `0b8168491a702ed2f98e0771f15eb9949fd290661201d8c63cfaa08d62e2d55e` |