# Starrydata Data Dictionary

**Dataset snapshot:** `2026-10-01 02:00:01 UTC+0900 (JST)` (`db_snapshot.txt`)  
**Source DOI:** [10.6084/m9.figshare.34036677.v1](https://doi.org/10.6084/m9.figshare.34036677.v1)  
**Source files:** `starrydata_papers.csv`, `starrydata_samples.csv`, `starrydata_curves.csv`  
**Prepared by:** Data-Managers, SRH University of Applied Sciences Heidelberg  
**Version:** *need to update - discussion

## Scope and assumptions

Starrydata is a database of numerical property data digitized from plots in published papers. The upstream README describes thermoelectric, battery, and magnetic materials, but the snapshot is broader: paper-level `project_names` contain 14 distinct project labels (ThermoelectricMaterials, MagneticMaterials, DielectricMaterials, BatteryMaterials, LowThermalConductivityMaterials, PiezoelectricMaterials, GeneralDB, Resistor, CondensedMatter, HighThermalConductivityMaterials, Hypermaterial, OrganicThermoelectricMaterials, SolidStateBatteryMaterials, AirBatteryMaterials). Values were digitized from figures with WebPlotDigitizer and StarryDigitizer.

The data product is documented as three related tables (`papers`, `samples`, `curves`) to preserve the source relationships. The `sample_info` JSON in `samples` is retained as `sample_info_raw` for provenance and flattened into nullable descriptor columns. A flattened descriptor column contains the JSON `category` value; if no category is present, the source string or `extracted` value is used. The original JSON preserves comments and any values not represented in the flattened columns.


## Table relationships

| Table | Row grain | Key | Relationship |
|---|---|---|---|
| `papers` | One paper record | `SID` | `SID` is referenced by `samples` and `curves`. |
| `samples` | One material sample record | (`SID`, `sample_id`) | `SID` links to `papers`; the composite key relates samples to curves. |
| `curves` | One digitized curve | (`SID`, `figure_id`, `sample_id`) | `SID` links to `papers`; (`SID`, `sample_id`) links to `samples`. `figure_id` groups curves from the same figure. |

The profiling notebook found no duplicate or missing `SID` values in `papers`, and no duplicate or missing `sample_id` values in `samples` for this snapshot. Use (`SID`, `sample_id`) for the sample-to-curve relationship; this avoids relying on `sample_id` alone across other snapshots.

## `papers` Table

| Column | Logical type | Definition |
|---|---|---|
| `SID` | Integer identifier | Primary key - Starrydata identifier for a paper. |
| `DOI` | String | Digital Object Identifier of the source paper, when supplied. |
| `URL` | URL string | URL associated with the paper DOI. |
| `issued` | JSON object stored as string  | Publication date as `{"date_parts":[[year, month, day]]}`. The inner list has 3 elements for 25,192 rows, 2 (year-month) for 24,570, 1 (year only) for 6,713, and the object is empty (`{}`) for 20 rows. Parse to an ISO 8601 date (or partial date) in the processed output if required. |
| `author` | JSON array stored as string| Author records; each contain given name, family name, or affiliation data. |
| `title` | String | Title of the source publication. |
| `container_title` | String | Full journal, book, or other containing-work title. |
| `container_title_short` | String | Abbreviated title of the containing work. |
| `volume` | String | Volume value as recorded for the publication. |
| `issue` | String | Issue value as recorded for the publication. |
| `page` | String | Page range or page value as recorded for the publication. |
| `ISSN` | String | International Standard Serial Number value(s), if supplied. |
| `publisher` | String | Publisher name. |
| `project_names` | JSON array | Starrydata project labels associated with the paper. |
| `created_at` | Timestamp string | Time the paper record was created in Starrydata; source timestamp includes a timezone. |

## `samples` Table

| Column | Logical type | Definition |
|---|---|---|
| `sample_name` | String | Name or label assigned to the material sample. |
| `sample_id` | Integer identifier | Starrydata sample identifier; use with `SID` to identify a sample across related records. |
| `composition` | String | Reported chemical composition or sample description. |
| `composition_details` | String | Additional composition or sample detail. |
| `SID` | Integer identifier | Starrydata identifier of the paper describing the sample; foreign key to `papers.SID`. |
| `DOI` | String | DOI of the publication associated with the sample. |
| `created_at` | Timestamp string | Time the sample record was created; source timestamp includes a timezone. |
| `updated_at` | Timestamp string | Time the sample record was last updated; source timestamp includes a timezone. |
| `sample_info_raw` | JSON object stored as string | Original `sample_info` content retained unchanged for provenance, including category, comment, extracted text, and source-specific details. |


### Structure of `sample_info`

In the raw data every non-missing `sample_info` is a JSON object (72,456 populated, 31,561 empty `{}`, 2,314 missing). Each key is a sample descriptor, and each value is one of:

- an object `{"category": "", "comment": ""}` (592,384 key-value pairs);
- an object `{"category": "", "comment": "", "extracted": ""}` (618,550 pairs), where `extracted` holds text extracted from the paper;
- a plain string (130,186 pairs, most of them empty).

Many descriptor values are empty strings even when the key is present, so a key being present does not mean a value was recorded; Appendix A lists both counts.

### Source-key normalization applied to flattened names

Before the variants below are applied, all keys are trimmed of leading/trailing whitespace (spaces and tabs) and repeated internal whitespace is collapsed. The following obvious variations are then consolidated into one output column; original spellings are preserved in `sample_info_raw`:

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



## `curves` Table

| Column | Logical type | Definition |
|---|---|---|
| `SID` | Integer identifier | Starrydata identifier of the source paper; foreign key to `papers.SID`. |
| `DOI` | String | DOI of the source paper. |
| `composition` | String | Composition associated with the curve. |
| `sample_id` | Integer identifier | Sample identifier; use with `SID` to link to `samples`. |
| `figure_id` | Integer identifier | Identifier used to group curves associated with a figure. |
| `figure_name` | String | Figure or panel label as recorded in the source paper. |
| `prop_x` | String | Name of the property represented on the x-axis. |
| `prop_y` | String | Name of the property represented on the y-axis. |
| `unit_x` | String | Unit for x-axis values, using the source unit notation. |
| `unit_y` | String | Unit for y-axis values, using the source unit notation. |
| `x` | JSON array of numbers stored as string | Ordered digitized x-axis values for one curve. |
| `y` | JSON array of numbers stored as string | Ordered digitized y-axis values corresponding position-by-position to `x`. |
| `created_at` | Timestamp string | Time the curve record was created; source timestamp includes a timezone. |
| `updated_at` | Timestamp string | Time the curve record was last updated; source timestamp includes a timezone. |
| `project_names` | JSON array | Starrydata project labels associated with the curve. |
| `comments` | String | Source comments or measurement conditions recorded for the curve. |

## Data Profiling Results 

The following results are from `01_data_profiling.ipynb` and describe the raw tables before cleaning or flattening.

| Table / field | Profile result | Meaning for use |
|---|---|---|
| `papers` | 56,495 rows; 15 columns; `SID` is unique and has no nulls. | `SID` is suitable as the paper-table primary key in this snapshot. |
| `samples` | 106,331 rows; 9 columns; `sample_id` is unique and has no nulls. | Preserve `SID` with `sample_id` when linking samples to curves. |
| `curves` | 237,313 rows; 16 columns. | One row represents one digitized curve. |
| `samples.sample_info` | 72,456 valid JSON objects (68.14%); 31,561 empty objects (29.68%); 2,314 missing values (2.18%); no malformed JSON was found. | Flatten safely; use null for unavailable attributes and retain the sample rows. |
| `samples.composition_details` | 87,433 missing (82.23%). | Keep the field nullable; do not drop samples solely because this optional description is missing. |
| `curves.comments` | 103,868 missing (43.77%). | Keep the field nullable; do not drop curve measurements solely because comments are absent. |
| Referential integrity: `samples` → `papers` | 9 orphan sample rows referencing 3 absent SIDs: `8534`, `8535`, `9026`. | Flag or quarantine these rows before an inner join; document any exclusion. |
| Referential integrity: `curves` → `papers` | 31 orphan curve rows referencing the same 3 absent SIDs. | Flag or quarantine these rows before an inner join; document any exclusion. |

Other missingness reported by the notebook includes paper `issue` (6.86%), `page` (4.01%), `ISSN` (3.36%), `container_title_short` (2.79%), and `volume` (2.57%). The notebook's key and referential checks report zero missing `SID` values in child tables. These profiling results do not verify that every `x` and `y` cell contains a valid numeric JSON array; that should be checked in the transformation pipeline if those arrays are used as model inputs.

## Appendix A: Flattened `sample_info` descriptor columns

The raw `sample_info` objects contain 138 distinct descriptor keys; after trimming and the normalization above they become 108 output columns. All are nullable. "Samples with key" counts samples whose `sample_info` contains the descriptor; "Samples with a value" counts those where the flattened value (category, else extracted text or string) is non-empty. Groups are assigned by the project label of the papers where the descriptor is populated. Descriptor meanings follow the column names, and the JSON `category` holds the selected value and `comment` holds free text.

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

`prop_x` and `prop_y` are free-text names entered during digitization, so the same quantity can appear under several names (for example `Seebeck coefficient`, `thermopower`, `Thermopower` and `S`; or `Electrical resistivity`, `log(Electrical resistivity)`, `ln(Electrical resistivity)` and `Log(row)`). Consolidate synonyms before analysis. Most frequent `prop_y` values with their most common unit:

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
| `magnetization_per_volume` | `A/m` | 1,564 |
| `Magnetization` | `T` | 1,511 |
| `Carrier mobility` | `m^2*V^(-1)*s^(-1)` | 1,378 |
| `Coulombic efficiency` | `-` | 958 |
| `Hall coefficient` | `m^3*C^(-1)` | 713 |

Most frequent `prop_x` values with their most common unit:

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

Four `prop_y` values carry more than one unit (`Hall mobility`, `log(Electrical resistivity)`, `logσT`, `magnetization_per_weight`), so check `unit_y` per row.

## References

- Figshare snapshot: <https://doi.org/10.6084/m9.figshare.34036677.v1>
- Starrydata dataset documentation and field descriptions: <https://starrydata.github.io/hp/en/manual/download/>
- Local source files used: `README(2).md`, `db_snapshot(1).txt`, and the three CSV files.
