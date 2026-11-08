# Cleaning Log: Starrydata Tableau Prep Flow

**Project:** SRH Heidelberg, Data Management Exam Project
**Tool:** Tableau Prep Builder (Python equivalents in `src/`)
**Purpose:** Document and justify every data preparation step for the presentation and oral exam.

---

## Source

This block is the first link in the lineage chain. The lineage document should reference it.

| Item | Value |
|---|---|
| Dataset | Starrydata snapshot (`starrydata_dataset.zip`) |
| DOI | 10.6084/m9.figshare.34036677.v1 |
| Snapshot timestamp (from `db_snapshot.txt`) | 2026-10-01 02:00:01 JST (UTC+09:00) = 2026-09-30 17:00:01 UTC |
| Licence | CC BY 4.0 |
| Downloaded by | Utkarsh A. Gaigole |
| Download date | 2026-11-02 09:22:11 (CET, UTC+01:00) |
| Download URL | https://doi.org/10.6084/m9.figshare.34036677.v1 (stable DOI link, preferred over the direct Figshare file URL) |
| Source of these values | DOI, timestamp, hashes: tracker source record; download details: Utkarsh |

---

## Environment

| Item | Value |
|---|---|
| Tableau Prep Builder version | 2026.3.0 |
| Operating system | Windows (all members use PowerShell); relevant later if Tableau and Python handle line endings or encodings differently |
| Raw data location | `data/raw/` |
| Log started | 2026-11-06 |

---

## Summary of Steps

Fill in as you go. This table is the basis for the before/after slide.

| Step | Table | Issue ID | Rows before | Rows after | Validated |
|---|---|---|---|---|---|
| T1.1 Checksums | all files | — | — | — | ☑ |
| T1.2 Text-file inputs | papers | — | 56,496 | 56,496 | ☑ |
| T1.2 Text-file inputs | samples | — | 106,332 | 106,332 | ☑ |
| T1.2 Text-file inputs | curves | — | 237,314 | 237,314 | ☑ |
| T1.3 Trailing blank record | papers | O27 | 56,496 | 56,495 | ☑ |
| T1.3 Trailing blank record | samples | O27 | 106,332 | 106,331 | ☑ |
| T1.3 Trailing blank record | curves | O27 | 237,314 | 237,313 | ☑ |
| T2.1 Timestamps to UTC | papers | O4 | 56,495 | 56,495 | ☑ |
| T2.1 Timestamps to UTC | samples | O4 | 106,331 | 106,331 | ☑ |
| T2.1 Timestamps to UTC | curves | O4 | 237,313 | 237,313 | ☑ |
| T2.2 Publication date precision | papers | O17 | 56,495 | 56,495 | ☑ |
| T3.1 Tier 2 scope filter | curves | O23, D4, D12 (variants: O29) | 237,313 | 136,679 | ☑ |
| T4–T5 Joins + orphan flag | curves → samples → papers | O6, O7, D9 | 136,679 | 136,679 | ☑ |
| A1 Audit: sample uniqueness | samples (all) | — (passed check) | 106,331 | 106,331 (0 duplicates) | ☑ |
| T6–T7 Points count + empty flag | curves + curve_points | O21 | 136,679 | 136,679 | ☑ |
| T8 Tier 2 points (inner join) | curve_points | O22 | 4,839,779 | 2,337,212 | ☑ |
| T9–T10 Outputs | tier2_curves / tier2_points | — | 136,679 / 2,337,212 | 136,679 / 2,337,212 | ☑ |

---

## Task 1: Data Ingestion & Integrity

### Step T1.1: Verify File Integrity via Checksums

**Status:** Done — 4 of 4 members verified _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-06 / Utkarsh / Aditya

**Why this step matters**
- Tableau Prep cannot compute cryptographic checksums, so verification happens **before** ingestion, outside Tableau.
- The reference hashes were **computed by the team** from the snapshot downloaded on 2026-11-02 by Utkarsh A. Gaigole. They were **not** published by Figshare and do not appear in `README.md`.
- A match therefore confirms that **every team member works on an identical copy** of the team's reference snapshot. On its own, it does not prove that the download matches what Figshare serves.

**Link to the original source (optional, stronger claim)**
- Check whether Figshare shows a checksum (often MD5) for `starrydata_dataset.zip`.
- If it does, compare it with the zip and record the result below. Only then can the log claim the download matches the source.

| Check | Figshare-published value | Local value | Match? |
|---|---|---|---|
| `starrydata_dataset.zip` (_algorithm, e.g. MD5_) | _paste, or "not published"_ | _paste_ | ☐ Yes ☐ No ☐ N/A |

**Command used** (run from inside `data/raw/`)

| OS | Command |
|---|---|
| Windows PowerShell | `Get-FileHash -Path .\starrydata_papers.csv -Algorithm SHA256` |
| macOS Terminal | `shasum -a 256 starrydata_papers.csv` |

For MD5: `-Algorithm MD5` (PowerShell) or `md5 <file>` (macOS).

> **Comparison is case-insensitive.** PowerShell prints hashes in uppercase, `shasum` in lowercase. `B82FF3…` and `b82ff3…` are the **same** hash, so mark that as a match.

**Results: comparison against team reference (SHA-256)**

✓ = matches reference (case-insensitive) · ⏳ = pending · ⚠ = see notes. Full hashes per member are in the appendix at the end of this step.

| File | Team reference SHA-256 | Sreelakshmi | Aditya | Utkarsh ✱ | Akshay |
|---|---|---|---|---|---|
| `starrydata_papers.csv` | `b82ff398b28c15e42aa6ef6de1df9c26f3935a00dd9c76925e9dbbf1a6b4e222` | ✓ ⚠1 | ✓ | ✓ | ✓ |
| `starrydata_samples.csv` | `744b1b496368c0ed24231073ae324a2ef302076801331abb0f9c69dcf9754f55` | ✓ ⚠1 | ✓ | ✓ | ✓ |
| `starrydata_curves.csv` | `411515829de82041809e112a30d55c676567972c80a95965c37feb1b1ef41c96` | ✓ ⚠1 | ✓ | ✓ | ✓ |
| `starrydata_dataset.zip` | `32f4ab3cdcecc8f95ff85342c373c54d8ff2e39f953333845670a711da9b30c6` | ✓ ⚠1 | ✓ ⚠3 | ✓ | ✓ |
| `README.md` | `0b8168491a702ed2f98e0771f15eb9949fd290661201d8c63cfaa08d62e2d55e` | ✓ ⚠1 | ✓ | ✓ | ✓ |
| `db_snapshot.txt` | `d7b08c352a35298c0cfb3648b7f49dde43cdb102da285f7dc5d62768c4ca82b2` | ✓ ⚠1 | ✓ | ✓ | ✓ |

**Validation performed**
- 2026-11-06: Sreelakshmi's and Aditya's outputs compared case-insensitively with the team reference. All three CSVs match for both members.
- 2026-11-06: team reference hashes for the zip, README.md and db_snapshot.txt added from the tracker's source record. Both members match on all three, so all six files match for both members.
- 2026-11-06: CSVs packaged in Utkarsh's `cleaning_flow.tflx` checked against the reference; all three match.
- 2026-11-06: Akshay's output compared case-insensitively with the team reference; all six files match. Full paths are visible, so each hash is tied to its file name.

**Notes / issues**
- ⚠1 Sreelakshmi — **content is proven, file names are not.** All six reference hashes are distinct, and her six reported hashes match all six references, so she holds all six files with identical content. What remains unproven is the name-to-content mapping: her Path column was truncated, so hashes are assigned to files only by row order. In principle her `papers.csv` could hold the samples content (e.g. swapped names). Supporting evidence: `Get-FileHash *` lists files alphabetically, and her row order matches Aditya's, whose full paths are visible. Her screenshot also shows only 5 rows (the zip row `32F4AB…` is in her pasted text only). Re-run requested with `| Format-List` so each hash appears next to its file name, with all six rows in the screenshot. _Status at sign-off: re-run ⏳ not yet received; content match is proven, name mapping rests on the row-order evidence above._
- ⚠3 Aditya's zip is named `starrydata_dataset (1).zip`, which looks like a browser's duplicate-download suffix. The hash depends on content, not on the file name, so this doesn't affect the check, but the name in the log differs from the expected file name.
- ✱ Utkarsh: 06 Nov, CSVs packaged in the .tflx matched the reference; 08 Nov, all six files in data\raw\ re-hashed with Get-FileHash and all six match.
- Provenance of each member's copy. All four copies hold the six files with hashes identical to the team reference, i.e. the same content as the Figshare snapshot (DOI 10.6084/m9.figshare.34036677.v1). How each copy was obtained (own download or shared copy) was not recorded at the time.

| Member | Location of the copy | Hashes verified | Result |
|---|---|---|---|
| Utkarsh | `data\raw\` in the project folder | 08 Nov 2026 (`Get-FileHash`) | 6 of 6 match |
| Aditya | `data\raw\` in the project folder | 06 Nov 2026 | 6 of 6 match |
| Sreelakshmi | Project folder on Desktop (path truncated in output) | 06 Nov 2026 | 6 of 6 match |
| Akshay | `data\raw\` in the project folder | 06 Nov 2026 | 6 of 6 match |

**Appendix: reported hashes per member** (as reported, Windows PowerShell, uppercase)

| File | Sreelakshmi | Aditya | Akshay |
|---|---|---|---|
| `db_snapshot.txt` | `D7B08C352A35298C0CFB3648B7F49DDE43CDB102DA285F7DC5D62768C4CA82B2` | `D7B08C352A35298C0CFB3648B7F49DDE43CDB102DA285F7DC5D62768C4CA82B2` | `D7B08C352A35298C0CFB3648B7F49DDE43CDB102DA285F7DC5D62768C4CA82B2` |
| `README.md` | `0B8168491A702ED2F98E0771F15EB9949FD290661201D8C63CFAA08D62E2D55E` | `0B8168491A702ED2F98E0771F15EB9949FD290661201D8C63CFAA08D62E2D55E` | `0B8168491A702ED2F98E0771F15EB9949FD290661201D8C63CFAA08D62E2D55E` |
| `starrydata_curves.csv` | `411515829DE82041809E112A30D55C676567972C80A95965C37FEB1B1EF41C96` | `411515829DE82041809E112A30D55C676567972C80A95965C37FEB1B1EF41C96` | `411515829DE82041809E112A30D55C676567972C80A95965C37FEB1B1EF41C96` |
| `starrydata_dataset.zip` | `32F4AB3CDCECC8F95FF85342C373C54D8FF2E39F953333845670A711DA9B30C6` | `32F4AB3CDCECC8F95FF85342C373C54D8FF2E39F953333845670A711DA9B30C6` | `32F4AB3CDCECC8F95FF85342C373C54D8FF2E39F953333845670A711DA9B30C6` |
| `starrydata_papers.csv` | `B82FF398B28C15E42AA6EF6DE1DF9C26F3935A00DD9C76925E9DBBF1A6B4E222` | `B82FF398B28C15E42AA6EF6DE1DF9C26F3935A00DD9C76925E9DBBF1A6B4E222` | `B82FF398B28C15E42AA6EF6DE1DF9C26F3935A00DD9C76925E9DBBF1A6B4E222` |
| `starrydata_samples.csv` | `744B1B496368C0ED24231073AE324A2EF302076801331ABB0F9C69DCF9754F55` | `744B1B496368C0ED24231073AE324A2EF302076801331ABB0F9C69DCF9754F55` | `744B1B496368C0ED24231073AE324A2EF302076801331ABB0F9C69DCF9754F55` |

**Evidence for presentation**
- ☑ Checksum output saved as text: `docs/evidence/checksums_example_output.txt` (one member's PowerShell output, as an example of the raw tool output; all four members' results are compared in the table above)

---

### Step T1.2: Set Up Text-File Inputs in Tableau Prep

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-06 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O33 (quoted line breaks in samples) |
| Table | papers, samples, curves |
| Flow step name in `.tflx` | Raw Papers, Raw Samples, Raw Curves |
| Python equivalent (`src/`) | `src/load_data.py → load_starrydata_file()` |

**Why this step matters**
- The text settings decide how every row is parsed. A wrong delimiter or qualifier would split or merge fields silently.
- The sampling setting decides whether the row counts and profiles in the editor describe the full table or only a sample. Recording it shows the "Rows before" numbers are real totals.

**Input settings (per file)**

| Setting | papers | samples | curves |
|---|---|---|---|
| Delimiter | `,` (comma) | `,` (comma) | `,` (comma) |
| Text qualifier | `"` | `"` | `"` |
| Header row | 1 | 1 | 1 |
| Data sample setting | Maximum | Maximum | Maximum |
| Rows read (incl. trailing blank record, see T1.3) | 56,496 | 106,332 | 237,314 |
| Columns | 15 | 9 | 16 |

**Validation performed**
- Row counts read by Tableau equal the real record count plus the one trailing blank record (T1.3), consistent with the full csv-module scan. So the sampling setting did not reduce the counts.
- Text qualifier evidence (O33): samples has 6,586 records with quoted line breaks in `composition_details`, so the file has 145,606 physical lines for 106,331 records. Tableau's count (106,332 = 106,331 records + the trailing blank record) follows the records, not the physical lines, which shows the `"` qualifier was applied correctly.

**Notes**
- Record the sample setting with the exact label shown in the Data Sample tab of Tableau Prep 2026.3.0, so an examiner can find the same option.

**Evidence for presentation**
- ☐ Screenshot of the Input step settings and Data Sample tab, one per file

---

### Step T1.3: Remove Trailing Blank Record

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-06 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O27 |
| Table | papers, samples, curves (all three) |
| Columns affected | All (the record is empty in every column); filter condition on `SID` |
| Flow step name in `.tflx` | papers: Remove trailing empty row - Papers; samples: Remove trailing empty row - Samples; curves: Remove trailing empty row - Curves |
| Python equivalent (`src/`) | `src/load_data.py → load_starrydata_file()`. Done: sets `skip_blank_lines=True` explicitly and asserts 56,495 / 106,331 / 237,313 rows. |

**Exam explanation**
> Each source CSV ends with an extra blank line. Tableau Prep reads it as an empty record; pandas skips it by default. We remove it in Tableau so both pipelines start from the same row counts. Verified: 0 rows with the wrong number of columns; papers and curves have 0 line breaks inside fields, and the line breaks inside samples fields are quoted and parsed correctly.

**Why this step matters / problem addressed**
- This isn't a data-quality problem in the source content. Tableau Prep and pandas parse the same file differently.
- If it isn't handled, every Tableau row count is one higher than the Python count, and the Tableau↔Python equivalence check (T-14) fails from the very first step.

**Actions taken (Tableau Prep step / settings)**
- One filter step per input: exclude rows where `SID` is null.
- Why this filter is safe: `SID` has 0 nulls in all real records (profiling), so this filter can only remove the blank record.

**Size of the problem**

| Metric | papers: Before | papers: After | samples: Before | samples: After | curves: Before | curves: After |
|---|---|---|---|---|---|---|
| Rows (table total) | 56,496 | 56,495 | 106,332 | 106,331 | 237,314 | 237,313 |
| Columns (table total) | 15 | 15 | 9 | 9 | 16 | 16 |
| Records affected by this step | 1 | — | 1 | — | 1 | — |
| Rows removed or flagged → destination | 1 → deleted | | 1 → deleted | | 1 → deleted | |
| Nulls in `SID` | 1 (the blank record) | 0 | 1 (the blank record) | 0 | 1 (the blank record) | 0 |

**Validation performed**
- Full scan of all records with Python's csv module, 06 Nov (supervisor check): 0 rows with the wrong number of columns; each file ends with `\n\n`.
- Papers and curves: 0 line breaks inside fields. Samples: 6,586 records contain quoted line breaks in `composition_details` (145,606 physical lines for 106,331 records); parsed correctly, as the row count confirms. This is why the text qualifier `"` matters (T1.2). Logged as O33.
- So the empty record comes from the trailing blank line, not from a broken multi-line value.
- Profiling: `SID` has 0 nulls in all real records, so the `SID is null` filter removes only the blank record.
- Tableau row counts, confirmed: papers 56,496 → 56,495; samples 106,332 → 106,331; curves 237,314 → 237,313. Exactly 1 row removed per table.
- Tableau row count after this step equals the pandas row count, per table: `load_data.py` asserts 56,495 / 106,331 / 237,313.

**Decisions & justification (exam defence)**
- Delete rather than flag: the record holds no data in any field, so there is nothing to preserve or quarantine.
- Filter on `SID is null` rather than "all fields null": simpler, and safe because `SID` is never null in real records (profiling). It cannot delete real data.
- One purpose per step: on the curves branch, the filter and the timestamp formatting were previously combined in one step ("Remove Ghost Row & Format UTC"). They were split (07 Nov) into a filter step (T1.3, changes the row count) and a formatting step (T2.1, changes columns only). _Final step names: see the Flow step name rows._ The flow now shows exactly which step changes the row count.
- Remove it in Tableau rather than add a blank row in Python: both pipelines should match the actual records in the source, not a parsing artefact.

**Evidence for presentation**
- ☐ Screenshot of the Tableau input profile showing the empty record before the filter
- ☐ Row counts after the filter next to the pandas counts

---

## Task 2: Standardisation

### Step T2.1: Convert Timestamps to UTC

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-06 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O4 (JavaScript date strings) |
| Table | papers, samples, curves |
| Columns affected | `papers.created_at`, `samples.created_at`, `samples.updated_at`, `curves.created_at`, `curves.updated_at` → each replaced by a `_utc` column |
| Flow step name in `.tflx` | papers: Format Timestamps (UTC) - Papers; samples: Format Timestamps (UTC) - Samples; curves: Format Timestamps (UTC) - Curves. Curves step sits directly after the trailing-row filter. |
| Python equivalent (`src/`) | `clean_timestamp_column()` in `src/clean_data.py` (on main) |

**Why this step matters / problem addressed**
- Raw values are JavaScript date strings, e.g. `Thu Jan 25 2018 13:56:56 GMT+0900 (Japan Standard Time)`.
- All rows use the same fixed offset (+09:00, 0 exceptions).
- Tableau's auto-detection can't read this format, so the values stay text and can't be sorted or compared as dates.

**Actions taken (Tableau Prep step / settings)**
- Rule: take characters 5–24 (`MID(…, 5, 20)`, e.g. `Jan 25 2018 13:56:56`), parse with `DATEPARSE` using `MMM dd yyyy HH:mm:ss`, then `DATEADD` −9 hours to convert JST to UTC.
- Exact calculated field as in the flow (every `_utc` field; `[updated_at]` in place of `[created_at]` for the updated columns):
  `DATEADD('hour', -9, DATEPARSE("MMM dd yyyy HH:mm:ss", MID([created_at], 5, 20)))`
- Original column removed; `_utc` column added.

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | unchanged: 56,495 / 106,331 / 237,313 | unchanged |
| Columns (table total) | 15 / 9 / 16 | 15 / 9 / 16 (unchanged: one column replaced by one) |
| Records affected by this step | all rows in each table | — |
| Rows removed or flagged → destination | 0 | — |
| Nulls in touched column(s) | 0 in raw; n/a (new column) | 0 in all five columns |

**Results after parsing** (as displayed in Tableau Prep: DD/MM/YYYY, 12-hour clock)

| Column | Nulls after parsing | Min (UTC) | Max (UTC) |
|---|---|---|---|
| `papers.created_at` | 0 | 25/01/2018, 04:56:56 am | 18/09/2026, 01:43:28 am |
| `samples.created_at` | 0 | 01/09/2017, 09:19:39 am | 30/09/2026, 08:25:24 am |
| `samples.updated_at` | 0 | 01/09/2017, 09:19:39 am | 30/09/2026, 08:34:52 am |
| `curves.created_at` | 0 | 01/09/2017, 09:19:39 am | 30/09/2026, 08:33:51 am |
| `curves.updated_at` | 0 | 01/09/2017, 09:19:39 am | 30/09/2026, 08:33:55 am |

**Validation performed**
- 0 nulls after parsing in all five columns, so no value failed to parse.
- All maxima are earlier than the snapshot timestamp (2026-09-30 17:00:01 UTC, see Source), so no parsed timestamp lies after the data was exported. This plausibility check would catch a wrong offset that pushed values forward.
- **Tableau↔Python equivalence (first evidence):** null counts and min/max are identical to an independent Python computation with the same rule (06 Nov).
- Spot-check across midnight, where a wrong rule is most visible (847 papers have a UTC date one day earlier than the Japanese date): SID 18761, raw `Sun Jan 06 2019 01:04:51 GMT+0900` → expected `05/01/2019, 04:04:51 pm` (16:04:51 UTC, previous day). Shown in Tableau: confirmed `05/01/2019, 04:04:51 pm`.

**Decisions & justification (exam defence)**
- UTC, not JST (D10): one unambiguous time base, and Python uses exactly the same rule.
- Weekday and the "(Japan Standard Time)" label are dropped: both are redundant with the date and the fixed offset.
- Raw column removed in the flow: the original value stays available in `data/raw/`, so lineage isn't lost.
- Output in ISO 8601 (`YYYY-MM-DD HH:MM:SS`). The DD/MM/YYYY values in the results table are only how Tableau displays dates under this computer's locale settings.
- Separate step from the row filter (see T1.3): this step changes columns only; rows stay at 237,313 on curves.

**Evidence for presentation**
- ☐ Screenshot of the profile (min/max, null count) for each parsed column

---

### Step T2.2: Publication Date Precision

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O17 (variable-precision JSON dates) |
| Table | papers |
| Columns affected | `issued` → new columns `issued_year`, `issued_month`, `issued_day`, `issued_precision` |
| Flow step name in `.tflx` | Extract Publication Precision (formerly "Clean 4") |
| Python equivalent (`src/`) | `clean_publication_precision()` |

**Why this step matters / problem addressed**
- `papers.issued` is a JSON object holding a nested array, with a year only, year + month, or year + month + day.
- Coercing it to a standard Date type makes Tableau invent the missing parts (e.g. 1 January). For AI training that creates false seasonality: papers would cluster on January 1st.

**Actions taken (Tableau Prep step / settings)**
- Extracted the parts with `REGEXP_EXTRACT` and `SPLIT` into `issued_year`, `issued_month`, `issued_day`, then changed their type to whole number.
- Added `issued_precision` with the values YMD, YM, Y, Unknown.
- Exact calculated fields as in the flow:
  - `issued_cleaned` = `REGEXP_EXTRACT([issued], '\[\[(.*?)\]\]')`
  - `issued_year` = `TRIM(SPLIT([issued_cleaned], ",", 1))`
  - `issued_month` = `TRIM(SPLIT([issued_cleaned], ",", 2))`
  - `issued_day` = `TRIM(RIGHT([issued_cleaned], IF FINDNTH([issued_cleaned], ",", 2) > 0 THEN LEN([issued_cleaned]) - FINDNTH([issued_cleaned], ",", 2) ELSE 0 END))`
  - `issued_precision` = `IF NOT ISNULL([issued_day]) THEN "YMD" ELSEIF NOT ISNULL([issued_month]) THEN "YM" ELSEIF NOT ISNULL([issued_year]) THEN "Y" ELSE "Unknown" END`
- `[[""]]` (187 papers) becomes null when converted to a whole number, so it is classified Unknown, which matches Python.
- SID 31709 has month 0 (`[[2018,0]]`); it is kept as recorded and classified YM (O35).

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | 56,495 | 56,495 |
| Columns (table total) | 15 | 18 |
| Records affected by this step | all rows | — |
| Rows removed or flagged → destination | 0 removed; every row flagged in `issued_precision` | — |
| Nulls in `issued_precision` | n/a (new column) | 0 |
| Nulls in `issued_month` | n/a (new column) | 6,733 (Y + Unknown), intentional |
| Nulls in `issued_day` | n/a (new column) | 31,303 (YM + Y + Unknown), intentional |

**Precision categories**

| `issued_precision` | Expected (baseline) | Rows in Tableau profile | Match? |
|---|---|---|---|
| YMD | 25,192 | 25,192 | ☑ Yes |
| YM | 24,570 | 24,570 | ☑ Yes |
| Y | 6,526 | 6,526 | ☑ Yes |
| Unknown | 207 | 207 | ☑ Yes |
| **Total** | 56,495 | 56,495 | ☑ Yes |

**Validation performed**
- Row counts per precision category match the baseline exactly (confirmed in the Tableau profile).
- The intended nulls follow from the categories: `issued_month` 6,733 = Y 6,526 + Unknown 207; `issued_day` 31,303 = YM 24,570 + 6,733.
- 0 nulls in `issued_precision`: every row has an explicit precision state, including Unknown.

**Decisions & justification (exam defence)**
- Parsed the nested date arrays into explicit year/month/day columns with a precision flag (YMD, YM, Y, Unknown).
- Did not coerce to a standard Date type: this would fabricate missing months and days. The output keeps the true precision of each date.

**Evidence for presentation**
- ☐ Screenshot of the `issued_precision` profile with category counts

---

## Task 3: Scope

### Step T3.1: Tier 2 Scope Filter on Curves

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O23 (Tier 2 scope); O29 (name variants); Decisions D4, D12 |
| Table | curves |
| Columns affected | `project_names`, `prop_y`, `prop_x` (filter conditions only; no values changed) |
| Flow step name in `.tflx` | Filter: Tier 2 Scope |
| Python equivalent (`src/`) | `filter_tier2_curves()` |

**Why this step matters / problem addressed**
- The project scope restricts deep cleaning, unit validation and cross-property consistency checks to Tier 2: thermoelectric curves for six core properties measured against temperature.
- This defines the validation boundary; it is not deleting data. The full dataset stays in `data/raw/`. The AI-readiness assessment covers only Tier 2.

**Actions taken (Tableau Prep step / settings)**
- Three conditions, applied in this order:
  1. `CONTAINS([project_names], "ThermoelectricMaterials")`;
  2. `[prop_y]` exactly one of: "Seebeck coefficient", "Electrical conductivity", "Electrical resistivity", "Thermal conductivity", "Power factor", "ZT" (OR-chain of equality tests);
  3. `[prop_x] = "Temperature"`.
- Execution order verified in the Changes pane (07 Nov).
- Exact matching only (D12): about 760 name variants (e.g. "thermopower") are excluded, not merged (O29).

| After condition | Rows remaining | Removed by this condition |
|---|---|---|
| Start (after T2.1) | 237,313 | — |
| 1. Thermoelectric tag | 159,593 | 77,720 |
| 2. Six exact properties | 141,910 | 17,683 |
| 3. x = Temperature | 136,679 | 5,231 |

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | 237,313 | 136,679 |
| Columns (table total) | 16 | 16 |
| Records affected by this step | 100,634 | — |
| Rows removed or flagged → destination | 100,634 → excluded from the Tier 2 output; retained in `data/raw/` | — |
| Nulls in touched column(s) | n/a (filtering operation) | n/a |

**Validation performed**
- Final count 136,679, with the intermediate count after each condition recorded above, so every removal can be attributed to one rule.
- Counts per property sum exactly to the total:

| Property (`prop_y`) | Curves |
|---|---|
| Seebeck | 36,939 |
| Thermal conductivity | 23,564 |
| ZT | 20,712 |
| Electrical conductivity | 18,839 |
| Electrical resistivity | 18,582 |
| Power factor | 18,043 |
| **Total** | 136,679 |

- Intermediate and per-property counts confirmed in the Tableau profile; they match Aditya's local run of `filter_tier2_curves()` (07 Nov, 09:03); code not yet on main. _Update once Aditya pushes to main._

**Decisions & justification (exam defence)**
- Defined the AI-readiness validation boundary.
- Strict exact matching (D12): name and unit variants are excluded and reported as upstream data-quality findings, rather than merged silently. Merging would hide the inconsistency; reporting it makes it fixable at the source. Variants reported as O29 in the issue register.

**Evidence for presentation**
- ☐ Screenshot of the filter condition and the resulting row count

---

## Task 4: Integration

### Steps T4–T5: Relational Joins & Orphan Flag

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O6, O7 (orphans); Decision D9 |
| Table | curves → samples → papers (combined) |
| Columns affected | Adds samples and papers columns; adds `is_orphan`; drops redundant join keys (e.g. `SID-1`) |
| Flow step name in `.tflx` | "Left Join: Enrich Curves with Samples" → "Left Join: Enrich with Paper Metadata" → "Flag Orphans & Clean Schema" |
| Python equivalent (`src/`) | `join_tier2_datasets()` |

**Why this step matters / problem addressed**
- curves is the most granular table (fact table), so the joins start from it.
- Some curves reference an `SID` that does not exist in papers (orphans). An inner join would drop them silently.

**Actions taken (Tableau Prep step / settings)**
- Left join curves → samples on `sample_id`; then left join → papers on `SID`.
- `is_orphan` = TRUE when the papers-side foreign key `SID-2` is null after the join. The flag evaluates the key itself, not a proxy metadata field such as `title`: a real paper with a missing title would otherwise be a false positive. It is computed from the join result, not from a hard-coded list of SIDs, so it still works after a data refresh.
- Exact calculated field as in the flow: `IF ISNULL([SID-2]) THEN TRUE ELSE FALSE END`
- Removed the duplicate join columns (e.g. `SID-1`, `SID-2`) **after** `is_orphan` was computed, since the flag depends on `SID-2`. Both happen in "Flag Orphans & Clean Schema". Order confirmed by the result: `is_orphan` = 28 could not be computed if `SID-2` were already removed.

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | 136,679 | 136,679 |
| Columns (table total) | 16 | 34 (+3 samples, +14 papers, +`is_orphan`, after removing duplicate keys) |
| Records affected by this step | 28 orphans | — |
| Rows removed or flagged → destination | 0 removed; 28 flagged in `is_orphan` | — |
| Nulls in `is_orphan` | n/a (new column) | 0 |

**Validation performed**
- 28 orphans identified (`is_orphan` = TRUE), matching the target (confirmed).
- 0 unmatched samples.
- Row count unchanged after both joins (136,679), so no duplicate keys on the samples or papers side multiplied rows.

**Decisions & justification (exam defence)**
- Left joins preserve every curve.
- Orphans are flagged, not dropped (D9): this surfaces unresolved paper references as feedback for upstream stakeholders without losing curve data. The cause is not known.
- Flag on the foreign key (`SID-2`), not on `title`: a null key after a left join means "no matching paper" by definition, whereas a null title could also mean a real paper with incomplete metadata. This keeps the flag free of false positives after future data refreshes.
- Redundant join columns dropped, so each field appears once in the output schema.

**Evidence for presentation**
- ☐ Screenshot of the join settings and the `is_orphan` profile

---

### Step A1 (Audit Branch): Sample Uniqueness Check

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | — (passed check) |
| Table | samples, all 106,331 rows (Tier 1) |
| Columns affected | None (read-only audit; nothing feeds an output) |
| Flow step name in `.tflx` | "Audit: Count Sample IDs" → "Filter: Duplicates > 1" (branches off "Format Timestamps (UTC) - Samples") |
| Python equivalent (`src/`) | Primary-key test in `src/validate.py` |

**Why this step matters / problem addressed**
- A duplicate sample would multiply curves in the samples join (T4–T5) and inflate row counts.
- The audit proves `sample_id` is a unique key of the samples table, instead of assuming it.

**Actions taken (Tableau Prep step / settings)**
- Separate audit branch, starting from "Format Timestamps (UTC) - Samples", off the main flow, so the check does not change any output.
- It runs on the samples table itself, not on the curves: one sample has several curves, so counting `sample_id` across curves would show repeats that are not duplicates.
- "Audit: Count Sample IDs": group by `sample_id`, count with `Number of Rows`.
- "Filter: Duplicates > 1": keep only groups where the count is greater than 1.

**Size of the problem**

| Metric | Result |
|---|---|
| Sample keys checked | 106,331 `sample_id` values (all rows of samples) |
| Keys with `Number of Rows` > 1 | **0** |
| Rows removed or flagged → destination | 0 (audit only, no output) |

**Validation performed**
- Exactly 0 duplicate `sample_id` values in all 106,331 samples rows, so the key also holds for every subset, including the samples referenced by Tier 2 curves.
- Consistent with T4–T5: the row count stayed at 136,679 after the samples join, which a duplicated key would have increased.

**Decisions & justification (exam defence)**
- Kept as a separate audit branch, not inside the main flow: the check documents a data property without altering data, so lineage of the outputs stays clean.
- Re-runs with every flow execution, so a future data refresh with duplicates would be caught.

**Evidence for presentation**
- ☐ Screenshot of the Aggregate step showing 0 rows with count > 1

---

### Steps T6–T7: Ingest Curve Points & Flag Empty Curve

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O21 (curves without digitised points) |
| Table | curves + `curve_points.csv` |
| Columns affected | Adds point count per curve and `has_points` |
| Flow step name in `.tflx` | input "curve_points" → "Profile Raw Points" → aggregate "Count points per curve" → "Left Join: Ingest Point Counts" → "Flag Empty Curve" |
| Python equivalent (`src/`) | `build_tier2_outputs()` in `src/clean_data.py`: counts points per curve, leaves `n_points` null for curves without points, derives `has_points`. Verified equal to Tableau (2,140 nulls in both; `docs/evidence/equivalence_report.md`). |

**Why this step matters / problem addressed**
- The x/y coordinates are stored as string arrays inside curves. Aditya's Python code unpacks them into `curve_points.csv`, one row per coordinate pair.
- Some curves have no digitised points; cause unknown. Downstream models must be able to see that.

**Actions taken (Tableau Prep step / settings)**
- Input `curve_points.csv`; aggregate the point count per curve; left join the counts to the Tier 2 curves.
- `has_points` = FALSE where the curve has no points. Exact calculated field: `IF ISNULL([Number of Rows (Aggregated)]) THEN FALSE ELSE TRUE END`; the count column is then renamed to `n_points`.
- Raw `x` and `y` string arrays removed in this branch (see T9–T10 for the 1NF reasoning).

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | 136,679 | 136,679 |
| Columns (table total) | 34 | 34 (+`n_points`, +`has_points`, −`x`, −`y`) |
| Records affected by this step | 2,140 empty curves | — |
| Rows removed or flagged → destination | 0 removed; 2,140 flagged `has_points` = FALSE | — |
| Nulls in `has_points` | n/a (new column) | 0 |

| `has_points` | Curves |
|---|---|
| TRUE | 134,539 |
| FALSE | 2,140 |
| **Total** | 136,679 |

**Validation performed**
- `has_points`: TRUE 134,539, FALSE 2,140; together exactly 136,679, so every curve is classified (confirmed in the Tableau profile).
- Row count unchanged (136,679), so the aggregation produced one row per curve before the join.

**Decisions & justification (exam defence)**
- Integrated the Python-extracted coordinates back into the visual pipeline to measure completeness.
- Empty curves are flagged, not dropped: `has_points` gives downstream AI models explicit metadata, so they don't train on empty records.

**Evidence for presentation**
- ☐ Screenshot of the `has_points` profile

---

### Step T8: Tier 2 Points (Inner Join)

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O22 (scope reduction for coordinates) |
| Table | `curve_points.csv` → Tier 2 points |
| Columns affected | Output schema restricted to 7 columns: `sample_id`, `figure_id`, `prop_y`, `unit_y`, `point_index`, `x_value`, `y_value` |
| Flow step name in `.tflx` | "Join: Filter T2 Points" → "Format Points Schema" |
| Python equivalent (`src/`) | `build_tier2_outputs()` in `src/clean_data.py`; writes the same 7 columns in the same order. Verified equal to Tableau (`docs/evidence/equivalence_report.md`). |

**Why this step matters / problem addressed**
- `curve_points.csv` covers the whole database (4,839,779 rows), but only the 136,679 Tier 2 curves were validated.

**Actions taken (Tableau Prep step / settings)**
- Inner join points to the Tier 2 curves; only points of in-scope curves are kept.
- Schema reduced to the 7 point-definition columns.

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | 4,839,779 | 2,337,212 |
| Columns (table total) | 39 (5 point columns + 34 curve columns, after the join) | 7 |
| Records affected by this step | 2,502,567 (4,839,779 − 2,337,212) | — |
| Rows removed or flagged → destination | 2,502,567 → out-of-scope points excluded; retained in `curve_points.csv` | — |
| Nulls in the 5 point columns | — | 0 in all 5 (checked across all 2,337,212 Tier 2 points) |

**Validation performed**
- Schema restricted to the 7 point-definition columns.
- Cross-check: the sum of `n_points` over the Tier 2 curves (T7) = 2,337,212, the expected row count of this step. Two independent routes give the same number.
- Row count in the Tableau output: confirmed exactly 2,337,212 after the flow run.

**Decisions & justification (exam defence)**
- Inner join discards out-of-scope points, so `tier2_points.csv` aligns exactly with the validated Tier 2 curves.

**Evidence for presentation**
- ☐ Screenshot of the join and the output row count

---

## Task 5: Outputs

### Steps T9–T10: Final Outputs

**Status:** Done _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** 2026-11-07 / Utkarsh / Aditya

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | — (schema enforcement and export) |
| Table | `tier2_curves.csv`, `tier2_points.csv` |
| Flow step name in `.tflx` | Output "tier2_curves.csv" (after "Flag Empty Curve"); output "tier2_points.csv" (after "Format Points Schema") |
| Python equivalent (`src/`) | Read back by Aditya for cross-validation |

**Actions taken**
- Output steps: file type CSV, location `data/processed/`, named `tier2_curves.csv` and `tier2_points.csv`.
- Raw `x` and `y` string arrays are intentionally absent from `tier2_curves.csv` (removed upstream in T6–T7).
- Ran the full flow. Flow in the repo as `.tfl`; packaged `.tflx` (110 MB) in the Moodle ZIP.

**Size of the problem**

| Output | Rows | Columns |
|---|---|---|
| `tier2_curves.csv` | 136,679 | 34 (no `x`, `y`) |
| `tier2_points.csv` | 2,337,212 | 7 |

**Validation performed**
- Schema printed and checked in pandas (column index); row counts compared with the target scopes. Actual counts read back after the run:

| Check after the flow run | Expected | Actual |
|---|---|---|
| `tier2_curves.csv` rows / columns | 136,679 / 34, no `x`/`y` | 136,679 / 34, no `x`/`y` ☑ |
| `tier2_points.csv` rows / columns | 2,337,212 / 7 | 2,337,212 / 7 ☑ |
| `is_orphan` = TRUE | 28 | 28 ☑ |
| `has_points` = FALSE | 2,140 | 2,140 ☑ |
| Precision counts (T2.2) | 25,192 / 24,570 / 6,526 / 207 | 25,192 / 24,570 / 6,526 / 207 ☑ |

- Both files and the header line of each sent to Aditya: ☐

**Decisions & justification (exam defence)**
- Redundant join keys removed, so each field appears once.
- `x` and `y` arrays dropped from `tier2_curves.csv` to enforce First Normal Form (1NF): an array packs many values into one cell, so it is not atomic. The same coordinates are already stored atomically, one point per row, in `tier2_points.csv`, linked to the curve by its key. Keeping both would duplicate the data and bloat the file. _Validation: confirm no `x`/`y` column in the pandas column index of `tier2_curves.csv`._
- Clean CSVs exported for the Python cross-validation; flow in the repo as `.tfl`, and packaged as `.tflx` (110 MB, with data) in the Moodle ZIP so the run can be reproduced.

**Evidence for presentation**
- ☐ Screenshot of the output settings and the run result

---

## Step Template (copy for each new step)

### Step _ID_: _Title_

**Status:** Not Started _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** _date_ / _name_ / _name_

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | _e.g. O4, O17_ |
| Table | _papers / samples / curves_ |
| Columns affected | |
| Flow step name in `.tflx` | |
| Python equivalent (`src/`) | _module.function_ |

**Why this step matters / problem addressed**
-

**Actions taken (Tableau Prep step / settings)**
-

**Size of the problem**

| Metric | Before | After |
|---|---|---|
| Rows (table total) | | |
| Columns (table total) | | |
| Records affected by this step | | — |
| Rows removed or flagged → destination | | _deleted / flag column `name` / quarantine file `path`_ |
| Nulls in touched column(s) | _n/a (new column) if derived_ | |

> For a new derived column (e.g. a parsed date), write **n/a (new column)** under Before. Never leave it blank.

**Validation performed**
- _e.g. 0 new nulls; min/max checked; 5 rows spot-checked against raw file_

**Decisions & justification (exam defence)**
-

**Evidence for presentation**
- ☐