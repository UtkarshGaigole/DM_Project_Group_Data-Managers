# Starrydata: Trustworthiness and AI-Readiness Assessment

**Group 6 "Data-Managers"** · Data Management group exam project · SRH University of Applied Sciences Heidelberg · Prof. Dr. Mehrdad Jalali · November 2026

> **Can this data be trusted, reused, and fed into an AI model — and how do you prove it?**

We take a licensed snapshot of the Starrydata materials database, profile it, clean and transform it in **two independent pipelines** (Tableau Prep and Python) that apply the same rules, and compare their outputs to prove they agree. Every step is documented with row counts before and after.

**Scope (two tiers)**

- **Tier 1 — integrity, whole snapshot:** keys, orphan records, timestamps, publication dates, JSON and array validity across all three tables.
- **Tier 2 — deep cleaning and AI-readiness:** thermoelectric curves for six properties (Seebeck coefficient, electrical conductivity, electrical resistivity, thermal conductivity, power factor, ZT) measured against temperature — **136,679 curves**. Properties are matched by exact name; name variants and unit errors are counted and reported, not merged.

---

## 1. Data source and licence

| Item | Value |
|---|---|
| Dataset | Starrydata snapshot `20261001_starrydata2` (Figshare) |
| DOI | [10.6084/m9.figshare.34036677.v1](https://doi.org/10.6084/m9.figshare.34036677.v1) |
| Database snapshot | 2026-10-01 02:00:01 JST (2026-09-30 17:00:01 UTC), from `db_snapshot.txt` |
| Licence | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) — confirmed in writing by the Starrydata team (NIMS) |
| Tables | `starrydata_papers.csv` (56,495 rows) · `starrydata_samples.csv` (106,331 rows) · `starrydata_curves.csv` (237,313 rows) |

**This repository contains modified, derived data and code.** The original data are © the Starrydata team and the authors of the original publications, used under CC BY 4.0. When you use the data, cite:

1. Y. Katsura, M. Kumagai, T. Mato, et al., "Starrydata: from published plots to shared materials data", *Science and Technology of Advanced Materials: Methods* 5(1), 2506976 (2025). https://doi.org/10.1080/27660400.2025.2506976
2. The Figshare snapshot: https://doi.org/10.6084/m9.figshare.34036677.v1
3. The original publications the data were taken from (DOIs in the `DOI` column of `starrydata_papers.csv`).

---

## 2. Get the data

Raw data are **not** committed to Git (see `.gitignore`).

1. Download `starrydata_dataset.zip` from the DOI above.
2. Extract `starrydata_papers.csv`, `starrydata_samples.csv` and `starrydata_curves.csv` into `data/raw/`.
3. Verify the files are identical to the ones we used (SHA-256):

| File | SHA-256 |
|---|---|
| `starrydata_papers.csv` | `b82ff398b28c15e42aa6ef6de1df9c26f3935a00dd9c76925e9dbbf1a6b4e222` |
| `starrydata_samples.csv` | `744b1b496368c0ed24231073ae324a2ef302076801331abb0f9c69dcf9754f55` |
| `starrydata_curves.csv` | `411515829de82041809e112a30d55c676567972c80a95965c37feb1b1ef41c96` |

Windows PowerShell: `Get-FileHash .\data\raw\starrydata_papers.csv -Algorithm SHA256` · macOS/Linux: `shasum -a 256 data/raw/starrydata_papers.csv`. Hashes are case-insensitive.

---

## 3. Setup

Requires Python 3 with the packages in `requirements.txt`. Run every command from the **repository root**.

```bash
python -m venv venv
# Windows: venv\Scripts\activate   ·   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Run the pipeline

Run in this order, from the repository root:

| Step | Command | What it does | Output |
|---|---|---|---|
| 1 | `python src/load_data.py` | Loads the three raw tables, checks the schema and the expected row counts, reads IDs as text, stops on any error | Console report |
| 2 | `python src/create_curve_points.py` | Unpacks the `x`/`y` arrays stored in one cell per curve into one row per point; runs 9 validation checks | `data/interim/curve_points.csv` (4,839,779 rows), `data/interim/curve_points_validation.log` |
| 3 | `python src/clean_data.py` | Applies the cleaning rules (UTC timestamps, publication-date precision, Tier 2 scope filter, joins, orphan and empty-curve flags) | `data/processed/tier2_curves.csv`, `data/processed/tier2_points.csv` |
| 4 | `python src/validate.py` | Quality checks: unique keys, referential integrity, orphans, array consistency, Tier 2 counts | Console report |
| 5 | `python -m pytest` | Automated tests | Test results |
| 6 | `python src/compare_outputs.py` | Compares the Tableau and Python outputs (rows, columns, nulls, keys, values, timestamps) | `docs/evidence/equivalence_report.md` |
| — | `python src/dictionary_appendix_counts.py` | Recomputes every count in the data dictionary appendices from the raw files | `docs/evidence/dictionary_counts/` |

The profiling notebook `notebooks/01_data_profiling.ipynb` documents the initial data-quality analysis (row counts, missing values, keys, referential integrity, JSON validity).

### Tableau Prep flow

`tableau/Starrydata_Pipeline.tfl` is the visual pipeline (Tableau Prep Builder 2026.3). It reads `data/raw/*.csv` and `data/interim/curve_points.csv`, so **run step 2 first**. Input and output paths are stored as absolute Windows paths; on another machine, re-point the four input steps and the two output steps to your copy of the repository. The packaged flow with its data (`.tflx`, 110 MB) is part of the course submission ZIP; it exceeds GitHub's file-size limit.

Every Tableau step, with row counts before and after and the reason for each decision, is documented in [`tableau/cleaning_log.md`](tableau/cleaning_log.md).

---

## 5. Outputs

| File | Rows | Columns | One row is |
|---|---|---|---|
| `data/processed/tier2_curves.csv` | 136,679 | 34 | one Tier 2 curve, with its sample and paper metadata, UTC timestamps, publication-date parts and precision, and the flags `is_orphan`, `n_points`, `has_points` |
| `data/processed/tier2_points.csv` | 2,337,212 | 7 | one data point of a Tier 2 curve: `figure_id`, `sample_id`, `point_index`, `x_value`, `y_value`, `prop_y`, `unit_y` |

Curves are identified by `figure_id` + `sample_id`. Timestamps are ISO 8601 in UTC. Orphan curves (paper ID not found) and curves without points are **flagged, not dropped**. `sample_info` is kept as the original JSON text.

---

## 6. Key cleaning decisions

| Issue found | Decision |
|---|---|
| Timestamps stored as JavaScript text in Japan time | Parsed and converted to UTC, identically in both pipelines |
| Publication dates with year only or year-month (31,303 papers) | Split into year / month / day plus a precision flag; no missing month or day is invented |
| x-axis mixes temperature and inverse temperature | Tier 2 keeps only curves with `Temperature` (all in K) |
| Property name variants and unit errors (e.g. `thermopower`, `S`, wrong units) | Excluded and reported, not merged |
| 40 rows referencing papers that do not exist (3 paper IDs) | Flagged `is_orphan`; 28 of these curves are in Tier 2 |
| 3,952 curves with empty point arrays (2,140 in Tier 2) | Flagged `has_points = FALSE` |
| Each CSV ends with a blank line | Removed in Tableau; pandas skips it by default |

All 20 issues, with counts, impact and treatment, are in the [issue register](docs/Issue_Register.md).

---

## 7. Documentation

| Document | Content |
|---|---|
| [`tableau/cleaning_log.md`](tableau/cleaning_log.md) | Every cleaning step: rows before/after, validation, decisions, Python equivalent |
| [`docs/Issue_Register.md`](docs/Issue_Register.md) | 20 data-quality issues with counts, impact-based severity and treatment |
| [`docs/FAIR_Assessment.md`](docs/FAIR_Assessment.md) | FAIR assessment and metadata record of the source (F-UJI: 57%, "moderate") |
| [`docs/Data_Dictionary.md`](docs/Data_Dictionary.md) | Field definitions, types, units, constraints and transformations |
| [`docs/Data_Governance.md`](docs/Data_Governance.md) | Roles, lineage, AI-readiness verdict and AI risks |
| [`docs/evidence/`](docs/evidence/) | F-UJI results, dictionary counts, checksums, equivalence report |

---

## 8. Repository structure

```
DM_Project_Group_Data-Managers/
├── data/
│   ├── raw/          # original CSVs from Figshare (not in Git)
│   ├── interim/      # curve_points.csv + validation log
│   └── processed/    # final Tier 2 outputs (not in Git; produced by the pipeline)
├── docs/             # issue register, FAIR, dictionary, governance, evidence/
├── notebooks/        # 01_data_profiling.ipynb
├── src/              # load_data, create_curve_points, clean_data, validate, compare_outputs, dictionary_appendix_counts
├── tableau/          # Starrydata_Pipeline.tfl + cleaning_log.md
├── tests/            # pytest tests
├── requirements.txt
└── README.md
```

---

## 9. Limitations

- Deep cleaning and the AI-readiness assessment cover **Tier 2 only**; other material domains were integrity-checked but not cleaned.
- Values were digitised from published plots; their accuracy against the original measurements cannot be checked from the data alone.
- `sample_info` descriptors are kept as raw JSON in the outputs; merging their spelling variants is proposed but not applied.
- The data are not ready for direct model training: see the readiness verdict and the required controls (e.g. grouped train/test splits by paper) in [`docs/Data_Governance.md`](docs/Data_Governance.md).

---

## 10. Team

| Member | Role |
|---|---|
| Utkarsh Gaigole | Project lead · Tableau Prep flow and cleaning log · integration |
| Aditya Sanjay Pawar | Profiling notebook · Python pipeline and tests |
| Sreelakshmi Koyambrath Sivaraman | Issue register · FAIR assessment · dictionary counts script · slides |
| Akshay Anilkumar Sreedevi | Data dictionary · data governance and AI-risk assessment |