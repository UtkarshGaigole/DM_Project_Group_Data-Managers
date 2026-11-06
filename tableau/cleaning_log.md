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
| T1.1 Checksums | all files | — | — | — | ☐ |
| T1.2 Text-file inputs | papers | — | 56,496 | 56,496 | ☐ |
| T1.2 Text-file inputs | samples | — | 106,332 | 106,332 | ☐ |
| T1.2 Text-file inputs | curves | — | 237,314 | 237,314 | ☐ |
| T1.3 Trailing blank record | papers | O27 | 56,496 | 56,495 | ☐ |
| T1.3 Trailing blank record | samples | O27 | 106,332 | 106,331 | ☐ |
| T1.3 Trailing blank record | curves | O27 | 237,314 | 237,313 | ☐ |
| T2.1 Timestamps to UTC | papers | O4 | 56,495 | 56,495 | ☐ |
| T2.1 Timestamps to UTC | samples | O4 | 106,331 | 106,331 | ☐ |
| T2.1 Timestamps to UTC | curves | O4 | 237,313 | 237,313 | ☐ |

---

## Task 1: Data Ingestion & Integrity

### Step T1.1: Verify File Integrity via Checksums

**Status:** In Progress — 4 of 4 members verified; Sreelakshmi's `Format-List` re-run (⚠1) pending _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** _date_ / _name_ / _name_

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
| `starrydata_dataset.zip` | `32f4ab3cdcecc8f95ff85342c373c54d8ff2e39f953333845670a711da9b30c6` | ✓ ⚠1 | ✓ ⚠3 | n/a (not in .tflx) | ✓ |
| `README.md` | `0b8168491a702ed2f98e0771f15eb9949fd290661201d8c63cfaa08d62e2d55e` | ✓ ⚠1 | ✓ | n/a (not in .tflx) | ✓ |
| `db_snapshot.txt` | `d7b08c352a35298c0cfb3648b7f49dde43cdb102da285f7dc5d62768c4ca82b2` | ✓ ⚠1 | ✓ | n/a (not in .tflx) | ✓ |

**Validation performed**
- 2026-11-06: Sreelakshmi's and Aditya's outputs compared case-insensitively with the team reference. All three CSVs match for both members.
- 2026-11-06: team reference hashes for the zip, README.md and db_snapshot.txt added from the tracker's source record. Both members match on all three, so all six files match for both members.
- 2026-11-06: CSVs packaged in Utkarsh's `cleaning_flow.tflx` checked against the reference; all three match.
- 2026-11-06: Akshay's output compared case-insensitively with the team reference; all six files match. Full paths are visible, so each hash is tied to its file name.

**Notes / issues**
- ⚠1 Sreelakshmi — **content is proven, file names are not.** All six reference hashes are distinct, and her six reported hashes match all six references, so she holds all six files with identical content. What remains unproven is the name-to-content mapping: her Path column was truncated, so hashes are assigned to files only by row order. In principle her `papers.csv` could hold the samples content (e.g. swapped names). Supporting evidence: `Get-FileHash *` lists files alphabetically, and her row order matches Aditya's, whose full paths are visible. Her screenshot also shows only 5 rows (the zip row `32F4AB…` is in her pasted text only). Re-run requested with `| Format-List` so each hash appears next to its file name, with all six rows in the screenshot.
- ⚠3 Aditya's zip is named `starrydata_dataset (1).zip`, which looks like a browser's duplicate-download suffix. The hash depends on content, not on the file name, so this doesn't affect the check, but the name in the log differs from the expected file name.
- ✱ Utkarsh: Verified 06 Nov: CSVs packaged in `cleaning_flow.tflx` match reference SHA-256. These are the files Tableau Prep actually reads. Zip, README.md and db_snapshot.txt are not in the `.tflx`.
- Still needed from each member: where their copy came from (own download or shared copy, from whom) and the date.

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
- ☐ Screenshot of terminal output saved (e.g. `docs/evidence/checksums.png`)

---

### Step T1.2: Set Up Text-File Inputs in Tableau Prep

**Status:** In Progress _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** _date_ / _name_ / _name_

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | — (setup step) |
| Table | papers, samples, curves |
| Flow step name in `.tflx` | Raw Papers, Raw Samples, _curves input: to fill in_ |
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

**Notes**
- Record the sample setting with the exact label shown in the Data Sample tab of Tableau Prep 2026.3.0, so an examiner can find the same option.

**Evidence for presentation**
- ☐ Screenshot of the Input step settings and Data Sample tab, one per file

---

### Step T1.3: Remove Trailing Blank Record

**Status:** In Progress _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** _date_ / _name_ / _name_

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O27 |
| Table | papers, samples, curves (all three) |
| Columns affected | All (the record is empty in every column); filter condition on `SID` |
| Flow step name in `.tflx` | _to fill in, one per input_ |
| Python equivalent (`src/`) | `src/load_data.py → load_starrydata_file()`. Currently relies on the `pandas.read_csv` default (`skip_blank_lines=True`). **Pending (Aditya):** set `skip_blank_lines=True` explicitly and assert the row count, so the matching behaviour is visible in the code. |

**Exam explanation**
> Each source CSV ends with an extra blank line. Tableau Prep reads it as an empty record; pandas skips it by default. We remove it in Tableau so both pipelines start from the same row counts. Verified: 0 line breaks inside fields, 0 rows with the wrong number of columns.

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
- Full scan of all records with Python's csv module, 06 Nov (supervisor check): 0 line breaks inside fields, 0 rows with the wrong number of columns; each file ends with `\n\n`. This confirms the empty record comes from the trailing blank line and not from a broken multi-line value.
- Profiling: `SID` has 0 nulls in all real records, so the `SID is null` filter removes only the blank record.
- Tableau row counts, confirmed: papers 56,496 → 56,495; samples 106,332 → 106,331; curves 237,314 → 237,313. Exactly 1 row removed per table.
- Tableau row count after this step equals the pandas row count, per table. _Pending Aditya's row-count assertion._

**Decisions & justification (exam defence)**
- Delete rather than flag: the record holds no data in any field, so there is nothing to preserve or quarantine.
- Filter on `SID is null` rather than "all fields null": simpler, and safe because `SID` is never null in real records (profiling). It cannot delete real data.
- Remove it in Tableau rather than add a blank row in Python: both pipelines should match the actual records in the source, not a parsing artefact.

**Evidence for presentation**
- ☐ Screenshot of the Tableau input profile showing the empty record before the filter
- ☐ Row counts after the filter next to the pandas counts

---

## Task 2: Standardisation

### Step T2.1: Convert Timestamps to UTC

**Status:** In Progress _(Not Started / In Progress / Under Review / Done)_
**Date / author / reviewer:** _date_ / _name_ / _name_

| Field | Value |
|---|---|
| Issue ID(s) (issue register) | O4 (JavaScript date strings) |
| Table | papers, samples, curves |
| Columns affected | `papers.created_at`, `samples.created_at`, `samples.updated_at`, `curves.created_at`, `curves.updated_at` → each replaced by a `_utc` column |
| Flow step name in `.tflx` | _to fill in: one distinct name per table, e.g. "Format Timestamps (UTC) – Papers", "… – Samples", "… – Curves". The papers and samples steps currently share one name; rename before filling in._ |
| Python equivalent (`src/`) | Pending (Aditya): same rule in `src/clean_data.py` |

**Why this step matters / problem addressed**
- Raw values are JavaScript date strings, e.g. `Thu Jan 25 2018 13:56:56 GMT+0900 (Japan Standard Time)`.
- All rows use the same fixed offset (+09:00, 0 exceptions).
- Tableau's auto-detection can't read this format, so the values stay text and can't be sorted or compared as dates.

**Actions taken (Tableau Prep step / settings)**
- Rule: take characters 5–24 (`MID(…, 5, 20)`, e.g. `Jan 25 2018 13:56:56`), parse with `DATEPARSE` using `MMM dd yyyy HH:mm:ss`, then `DATEADD` −9 hours to convert JST to UTC.
- Exact calculated field as in the flow: _paste expression here_
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
- Spot-check across midnight, where a wrong rule is most visible (847 papers have a UTC date one day earlier than the Japanese date): SID 18761, raw `Sun Jan 06 2019 01:04:51 GMT+0900` → expected `05/01/2019, 04:04:51 pm` (16:04:51 UTC, previous day). Shown in Tableau: _⏳ to confirm_

**Decisions & justification (exam defence)**
- UTC, not JST (D10): one unambiguous time base, and Python uses exactly the same rule.
- Weekday and the "(Japan Standard Time)" label are dropped: both are redundant with the date and the fixed offset.
- Raw column removed in the flow: the original value stays available in `data/raw/`, so lineage isn't lost.
- Output in ISO 8601 (`YYYY-MM-DD HH:MM:SS`). The DD/MM/YYYY values in the results table are only how Tableau displays dates under this computer's locale settings.

**Evidence for presentation**
- ☐ Screenshot of the profile (min/max, null count) for each parsed column

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