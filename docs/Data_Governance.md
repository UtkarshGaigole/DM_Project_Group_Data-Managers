# Data Governance and AI Risk Assessment

**Project:** Starrydata — Data-Managers, SRH University of Applied Sciences Heidelberg  
**Source snapshot:** `20261001_starrydata2`  
**Snapshot timestamp:** `2026-10-01 02:00:01 UTC+0900 (JST)` (`2026-09-30 17:00:01 UTC`)  
**Dataset DOI:** [10.6084/m9.figshare.34036677.v1](https://doi.org/10.6084/m9.figshare.34036677.v1)  
**Source files:** `starrydata_papers.csv`, `starrydata_samples.csv`, `starrydata_curves.csv`  
**Version:** v1.3, 2026-11-14 (data dictionary stewardship corrected to Sreelakshmi Koyambrath Sivaraman; earlier: DOI-grouped splits, parallel Python/Tableau lineage, D12 wording, flattening blocker scoped)  
**License:** CC BY 4.0, shown on the Figshare record and confirmed by Dr. Mato in email dated 29 October 2026. The Figshare snapshot is the project source; a later GitHub release without a stated license is excluded.  


## 1. Governance purpose and responsibilities

This document records ownership, stewardship, lineage, and the controls required before machine-learning use. Role assignments reflect the project tracker and should be confirmed with the dataset owner where they concern upstream decisions.

| Role | Responsibility | Assigned person or group |
|---|---|---|
| Source data owner | Maintains Starrydata and decides on upstream corrections or clarification requests. | Starrydata Research Team; Dr. Mato is the project contact. |
| Project lead and integration | Coordinates scope, decisions, and integration of the project outputs. | Utkarsh Gaigole. |
| Data steward and documentation | Maintains the issue register, data dictionary, governance and AI-risk documentation, FAIR record, and documentation of decisions. | Akshay Anilkumar Sreedevi (governance and AI-risk documentation); Sreelakshmi Koyambrath Sivaraman (data dictionary, FAIR/metadata and issue register). |
| Pipeline and profiling | Maintains the profiling notebook and Python loading, flattening, validation, and transformation functions. | Aditya Sanjay Pawar. |
| Tableau Prep flow | Maintains the visible Tableau Prep cleaning and transformation flow. | Utkarsh Gaigole. |
| Data users | Use the documented outputs for analysis and model development, subject to their scope and limitations. | Materials science researchers and data scientists. |

These project responsibilities do not transfer ownership of the upstream Starrydata data or authorize the group to alter the source record.

## 2. Lineage and change control

The project uses the frozen Figshare snapshot identified above. The source database timestamp is recorded in `db_snapshot.txt`; the raw CSVs should be retained unchanged. The GitHub release dated 20 October 2026 is excluded because the tracker records no license statement for it.

The intended lineage is: Figshare snapshot → immutable raw files → profiling and validation → Python preparation of curve points and other agreed inputs → Tableau Prep transformations and documented joins/filters → validated project outputs. The project decision log specifies that curve arrays are unpacked once in Python into `data/interim/curve_points.csv`; Tableau Prep then applies the visible scope, axis, join and flag logic, with one aggregation (`n_points` per curve). In parallel, the Python pipeline produces the same Tier 2 outputs independently from the raw files, and the two sets of outputs are compared column by column (row counts, columns, types, null counts, key sets, values); this parallel design is the reproducibility evidence. `data/interim/` is for intermediate/prototype data; reserve `data/processed/` for outputs that have passed the agreed validations.

For each run, retain the input snapshot/DOI, code and flow version, transformation rules, row counts at each stage, validation results, output names, and reasons for any flagged or excluded records. Preserve source values alongside normalized values where practical. Never silently overwrite conflicting source values or remove rows without recording the rule and counts. Freeze the version used for the presentation/report and record later changes in the project log.

## 3. Machine-learning readiness declaration

**Status: The raw snapshot is not ready for direct model training. It is conditionally suitable for exploratory, task-specific machine-learning work after the transformation issues below are resolved and the final outputs pass validation.** A readiness decision applies to a defined prediction target and population; it does not certify the whole database for every modeling task.

The team-reproduced raw snapshot contains 56,495 paper rows, 106,331 sample rows, and 237,313 curve rows. For `samples.sample_info`, 72,456 values contain JSON content (68.14%), 31,561 are empty JSON objects `{}` (29.68%), and 2,314 are null (2.18%); no malformed JSON was found. Empty objects are valid JSON but provide no descriptor values. `composition_details` is null in 87,433 rows (82.23%), and curve `comments` is null in 103,868 rows (43.77%). These are different forms of missingness and must not be converted to numeric zero or merged into one missingness category.

The tracker also records 9 sample rows and 31 curve rows referencing paper SIDs absent from the papers table, 3,952 curve records with empty x/y arrays, and 40 DOIs shared by 85 paper rows with different SIDs (45 surplus rows). All curve arrays parsed as JSON and had matching x/y lengths in the reproduced profiling; this structural check does not establish that digitized values are scientifically accurate. The deep-cleaning scope is final (decisions D4 and D12): thermoelectric data and six core properties. The Tier 2 outputs have been produced independently by Tableau Prep and Python and compared column by column: they match in all 41 columns with 0 substantive mismatches (differences are limited to Tableau's CSV export rounding, at most 5×10⁻¹⁰, and line endings; `docs/evidence/equivalence_report.md`), and 31 automated tests pass. This establishes reproducibility of the transformation; it does not by itself make the outputs AI-ready (see section 5). The tracker (O29) also records unit errors and name variants in the property and unit labels; these are excluded from Tier 2 by exact-name matching and reported (D12).

A defect has been observed in `clean_data.py` v1: sample-info keys differing only by whitespace were collapsed into one output column. The tracker (O31) records 22,298 overwrites across 15,786 records, in each of which one value was silently overwritten. The defect is a blocker **only for flattened descriptor output**: the v1 flattened output must not be used as model input. It does **not** affect the Tier 2 outputs (`tier2_curves.csv`, `tier2_points.csv`), which keep `sample_info` as raw JSON text and contain no flattened columns.

The proposed fix has been tested on the full samples table with the counting script: with the variant mapping and the rule "keep the non-empty value", 15,063 (record, column) pairs have differing variants. 15,020 of them are a value against an empty string, so no recorded value is lost; only 43 are genuine conflicts between two different non-empty values (26 of them from one paper, SID 61072). The 43 are logged in `sample_info_merge_conflicts.csv` for manual review. The mapping itself is still an open project decision (D7); the team must merge the fix, document the mapping, review the 43 conflicts, and re-run checks before approving flattened features.

## 4. AI risk register

| Risk | Evidence and status | Possible impact | Required control before or during modeling |
|---|---|---|---|
| Sparse or absent sample descriptors | 29.68% of `sample_info` values are `{}` and 2.18% are null; 68.14% contain JSON content. | A model can learn documentation/measurement practices instead of material behavior; feature availability may vary across subsets. | Keep empty and null states distinguishable; preserve missing values as null; report missingness per flattened feature and subgroup. Do not replace missing descriptors with zero without a justified, feature-specific meaning. |
| Lossy JSON flattening and inconsistent keys | The v1 prototype collapsed whitespace variants, causing 22,298 silent overwrites in 15,786 records (O31). There are 138 distinct source keys, including spelling and spacing variants. D7 mapping is open. The tested fix leaves 43 genuine conflicts (logged); all other differing pairs are value against empty. Tier 2 outputs are unaffected (no flattening). | Features can be corrupted or misclassified, and the same scientific concept can be split across columns. | Do not train on v1 flattened output. Define reviewed canonical mappings and conflict precedence; retain raw JSON; count conflicts; test the corrected flattening on full data and compare representative records before using it. |
| Missing composition metadata and comments | `composition_details` is 82.23% null; `comments` is 43.77% null. | Text/descriptor analyses may use a biased subset and missingness may correlate with paper, material, or era. | Treat fields as optional and nullable; state whether excluded or used; report inclusion counts and missingness by relevant subgroup. |
| Publication and selection bias | Data are curated from published literature and digitized figures, not sampled randomly from all materials or experiments. Bias magnitude is not quantified. | Published, studied, or noteworthy materials, properties, and results may be overrepresented; generalization to all materials is unsupported. | Define the target population; profile coverage by paper, year, material family, project, and property where available; describe results as applying to the evaluated dataset unless externally validated. |
| Digitization uncertainty | Values are extracted from figures using WebPlotDigitizer/StarryDigitizer. The snapshot does not provide per-point uncertainty estimates. | Axis calibration, line thickness, rounding, and figure quality can add error to the values used as model labels or features. | Treat values as digitized estimates; preserve paper, figure, and sample identifiers; validate units and arrays; compare selected curves to source figures when feasible; do not claim measurement precision beyond the source. |
| Unit and semantic heterogeneity | The tracker reports 170 distinct `prop_y` and 69 distinct `unit_y` labels across curves; temperature and inverse temperature both occur as x-axis concepts. O29 additionally records unit errors and name variants. | Mixing properties or incompatible axes/units can make features and targets scientifically invalid. | Restrict models to a clearly defined property/unit scope; document canonical labels, name-variant mappings, unit-error corrections, and conversions; preserve raw labels; apply domain review before merging variants. |
| Unresolved relational links and duplicate DOI records | 9 sample rows and 31 curve rows have SIDs absent from `papers`; 40 DOIs are shared by 85 paper rows with different SIDs (45 surplus rows). | Joins can drop records or attach them ambiguously, changing the modeling population. | Flag unmatched records (D9) and keep the flag in the outputs; exclude them from a given model only under a logged rule; investigate duplicate DOIs; report counts before and after joins. Do not silently discard them. |
| Empty curve arrays | 3,952 curve records have empty x and y arrays. Non-empty arrays parsed and had matching lengths in profiling. | Empty curves contain no point-level training observations; retaining them as if they contained values can distort counts or aggregation. | Exclude from point-level modeling or retain only as metadata under a stated rule; report the count. Revalidate parseability, numeric values, and equal lengths in the pipeline. |
| Correlated observations and leakage | Curves can share a paper, sample, or figure; the tracker defines `figure_id` + `sample_id` as the curve composite key. | Random row-level train/test splits can put related data in both sets and overstate performance. | Group train/test splits by DOI (or SID where DOI is missing), see issue register #5: 40 DOIs sit on several SIDs, so a split by SID alone would let duplicate papers leak between train and test. Keep related observations together and document the split unit. |
| Non-random project/domain coverage | The final deep-cleaning scope (D4/D12) is a subset: thermoelectric curves and six core properties with temperature as x. | Results from this subset cannot be assumed to apply to battery, magnetic, or other thermoelectric properties. | State the exact scope in the model card/report; do not generalize beyond included properties, units, and source groups without separate evaluation. |
| Timestamp misuse | `created_at` and `updated_at` are database record timestamps; they are not established experimental measurement dates. | Using them as experiment time can create misleading temporal conclusions or leakage. | Use them for provenance only unless a task establishes their scientific meaning; do not label them measurement dates. |
| Attribution and license obligations | Figshare record and Dr. Mato's email confirm CC BY 4.0; source-paper citation metadata is present. The README's `XXX License` placeholder is inconsistent with the Figshare license. | Incorrect licensing statements or omitted attribution weaken lawful reuse and reproducibility. | Cite the Figshare DOI and relevant original papers; link CC BY 4.0; identify the group’s modifications; report the README inconsistency rather than copying it. |

## 5. Minimum release gate for model use

Before describing a dataset export as AI-ready or using it for training, the team should:

1. Define the target, prediction unit, population, intended use, and permitted feature set.
2. If flattened descriptors are used: fix the v1 `sample_info` overwrite bug; close D7 with a documented, reviewed key-mapping and conflict-handling rule (including the 43 logged conflicts); preserve the original JSON.
3. Run the corrected pipeline on the full agreed scope and compare its output against source rows, including conflicting key variants.
4. Validate primary/composite keys, foreign-key joins, orphan handling, duplicate DOI treatment, JSON parsing, numeric curve arrays, equal x/y lengths, units, and row counts.
5. Keep missing values and empty arrays distinct; document every exclusion, imputation, normalization, unit conversion, and flag with before/after counts.
6. Use grouped train/test splits by DOI (or SID where DOI is missing), see issue register #5, and check for leakage across samples/figures.
7. Report coverage and performance by relevant material, paper, year, and property groups where sample sizes permit; state uncertainty and limits on generalization.
8. Record the exact source DOI, code/flow version, output version, and license attribution with the model dataset.

Until the final outputs pass these checks, refer to them as prototypes or intermediate outputs rather than validated AI-ready data. The flattening defect blocks only outputs that contain flattened `sample_info` columns; it is not a blocker for the Tier 2 outputs, which keep `sample_info` as raw JSON.

## 6. Intended use and limitations

After the release gate is met, the documented, scoped outputs may support exploratory materials-science analysis and baseline model development. They should not be presented as a complete or unbiased census of materials, or as direct ground-truth laboratory measurements. Scientific claims and operational decisions require task-specific validation and, where possible, evaluation against independent data. The project should report unresolved issues and limitations alongside any model results.