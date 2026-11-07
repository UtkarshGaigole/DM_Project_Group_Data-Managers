#!/usr/bin/env python3
"""
dictionary_appendix_counts.py
=============================
Reproduces every count that appears in Appendix A (sample_info descriptor
columns) and Appendix B (property / unit vocabulary) of docs/Data_Dictionary.md,
plus the verification figures quoted in its profiling section.

It READS the three raw CSVs and never modifies them.

Usage
-----
    python dictionary_appendix_counts.py --data-dir data/raw \
                                         --out-dir docs/evidence/dictionary_counts

Outputs (all in --out-dir)
--------------------------
    summary.json                      headline figures + SHA-256 of the raw files
    appendix_a_descriptors.csv        one row per flattened sample_info column
    appendix_a.md                     the same, as the grouped Markdown tables
    appendix_a_merge_report.csv       per column: how often variant keys co-occur
    sample_info_merge_conflicts.csv   records where >=2 variant keys hold
                                      DIFFERENT non-empty values (needs a decision)
    appendix_b_prop_y.csv / _prop_x.csv   property vocabulary with most common unit
    appendix_b.md                     the top-N tables as Markdown
    tier2_excluded_variants.csv       property names NOT in Tier 2 (reported finding)
    unit_notations.csv                one unit written in several notations (FAIR I2)

Status of the rules implemented here
------------------------------------
    * Variant mapping and merge rule ........ PROPOSED (decision D7, still open)
    * issued_* split ........................ PROPOSED (decision D8)
    * UTC conversion ........................ PROPOSED (decision D10)
    * Tier 2 scope .......................... FINAL (decision D4)
    * curve_points contract ................. FINAL (decision D11)
Change the constants below if a decision changes; the dictionary tables are then
regenerated from this script rather than edited by hand.
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------
# Constants (decisions)
# --------------------------------------------------------------------------
SNAPSHOT_UTC = datetime(2026, 9, 30, 17, 0, 1)        # 2026-10-01 02:00:01 JST
TIER2_PROPS = ["Seebeck coefficient", "Electrical conductivity",
               "Electrical resistivity", "Thermal conductivity",
               "Power factor", "ZT"]                   # D4
TIER2_PROJECT = "ThermoelectricMaterials"              # D4
TIER2_PROP_X = "Temperature"                           # D4
TOP_N_Y, TOP_N_X = 20, 10

# D7 (PROPOSED): canonical output column -> source-key variants. Applied AFTER
# trimming and collapsing whitespace; lookup is case-insensitive. Keys that are
# not listed keep their trimmed spelling (and their case).
VARIANT_MAP = {
    "Measurement temperature": ["measurement temperatur", "measurement temperature"],
    "Remanence magnetization": ["remanence magnetion", "emanence magnetion"],
    "Saturation magnetization": ["saturation magnetization", "saturation magnetizatio"],
    "Coercivity": ["coercivity", "oercivity"],
    "MaterialFamily": ["material family", "materials family", "materialfamily",
                       "materialsfamily", "materialfarmily"],
    "ThermalMeasurement": ["thermalmeasurement", "thermal measurement", "thermalmeaasurement"],
    "ElectricalMeasurement": ["electricalmeasurement", "electrical measurement"],
    "DifferentialThermalAnalyzer": ["differentialthermalanalyzer", "differential thermal analyzer"],
    "DataType": ["datatype", "data type"],
    "GrainSize": ["grainsize", "grain size"],
    "RelativeDensity": ["relativedensity", "relative density"],
    "OrganicFabricationProcess": ["organicfabricationprocess", "organic fabrication process"],
    "OrganicMaterialFamily": ["organicmaterialfamily", "organic material family"],
    "N/P ratio|A/C ratio": ["n/p ratio|a/c ratio", "n/p ratio| a/c ratio"],
    "magnetic field": ["magnetic field"],
    "Maximum power": ["maximum power"],
}
LOOKUP = {v: canon for canon, vs in VARIANT_MAP.items() for v in vs}

# Grouping used for the Appendix A tables (by project of the papers where the
# descriptor is populated). Columns not listed fall into "Ungrouped".
GROUPS = {
    "General and thermoelectric sample descriptors": [
        "DataType", "Form", "FabricationProcess", "FabricationProcess 2", "FabricationProcess 3",
        "Purity", "RelativeDensity", "GrainSize", "MaterialFamily", "ElectricalMeasurement",
        "ThermalMeasurement", "Other", "laser flash and different thermal analyzer",
        "DifferentialThermalAnalyzer", "LaserFlash", "Composition conversion", "Measurement axis",
        "AbsoluteDensity", "PoreSize", "Porosity", "ClosedPorosity", "OrganicMaterialFamily",
        "OrganicFabricationProcess", "OrganicFabricationProcess 2"],
    "Magnetic descriptors": [
        "MagneticMeasurement", "Coercivity", "Saturation magnetization",
        "Remanence magnetization", "Measurement temperature", "magnetic field"],
    "Battery descriptors": [
        "Anode active material", "Solvent 1", "Solute 1", "Cathode active material",
        "Cathode conductive agent", "Cathode binder 1", "Cathode areal density (cathode loading)",
        "Solvent 2", "Solute 2", "Ratio of electrolyte to cathode active material",
        "Cathode binder 2", "Anode binder 1", "Solvent 3", "Solute 3", "Anode binder 2",
        "Cathode volumetric density", "Cathode additive 1", "Anode conductive agent",
        "Cathode additive 2", "Anode additive 1", "Anode additive 2", "Cathode areal capacity",
        "Separator", "Cathode current collector", "Cell type", "Lower voltage limit",
        "Upper voltage limit", "Electrolyte additive 1", "Current density",
        "Anode current collector", "Anode areal capacity", "Coulombic efficiency",
        "Electrolyte additive 2", "N/P ratio|A/C ratio", "Electrolyte additive 3",
        "Counter electrode", "Reference electrode", "Scan rate", "Working electrode",
        "Hysteresis", "Cathode catalyst material", "Catalyst loading",
        "Redox mediator in electrolyte", "Redox mediator in cathode", "Cathode additive"],
    "Dielectric-project descriptors": [
        "Synthesis method1", "Synthesis method2", "Synthesis method3", "Final product",
        "Sintering method", "Sintering temperature", "Sintering time", "Measurement method1",
        "Measurement method2", "Measurement method3", "Chemical composition", "Sample form",
        "Starting material"],
    "Hypermaterial, condensed-matter and one-off descriptors": [
        "sintering temperature", "lattice parameter", "direction", "composition type",
        "annealing condition", "sample info", "other sample process info",
        "other sample process info 2", "6: other sample process info", "AC/QC type",
        "measurement condition", "Applied field", "2D iron-tetracyanoquinodimethane", "comment",
        "Peak efficiency", "Maximum power", "Module operated temperature", "Note",
        "Mn15Si26[001]", "synthesis"],
}
GROUP_OF = {c: g for g, cols in GROUPS.items() for c in cols}

# Units that are written in more than one notation for the SAME unit (reported as a
# finding for the FAIR assessment, I2). Nothing is converted or merged.
UNIT_NOTATION_GROUPS = {
    "siemens per metre (electrical conductivity)": ["ohm^(-1)*m^(-1)", "S*m^(-1)", "S/m"],
    "volt per kelvin (Seebeck coefficient)": ["V*K^(-1)", "V/K"],
    "per kelvin (inverse temperature)": ["K^(-1)", "1/K"],
}

# Name patterns used ONLY to list candidate variants of the Tier 2 properties
# (reported as a finding; nothing is merged or renamed).
VARIANT_PATTERNS = {
    "Seebeck coefficient": r"seebeck|thermopower|^s$",
    "Electrical conductivity": r"conductivity|^σ|sigma",
    "Electrical resistivity": r"resistivity|^rho|row",
    "Thermal conductivity": r"thermal conductivity",
    "Power factor": r"power factor|^pf$",
    "ZT": r"^zt$|figure of merit",
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ws_norm(key: str) -> str:
    return re.sub(r"\s+", " ", key).strip()


def canonical(key: str) -> str:
    k = ws_norm(key)
    return LOOKUP.get(k.lower(), k)


def flatten_value(val) -> str:
    """First non-blank of category, then extracted; plain-string values as they are.

    Whitespace-only text counts as empty (e.g. ' '), so the D7 merge rule
    'keep the non-empty value' is well defined.
    """
    if isinstance(val, dict):
        for key in ("category", "extracted"):
            v = val.get(key)
            if isinstance(v, str) and v.strip():
                return v
        return ""
    return val if isinstance(val, str) and val.strip() else ""


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def to_utc(series: pd.Series) -> pd.Series:
    """Characters 5-24 of 'Thu Jan 25 2018 13:56:56 GMT+0900 (...)', minus 9 h."""
    assert series.str.contains(r"GMT\+0900", regex=True).all(), "non-JST timestamp found"
    parsed = pd.to_datetime(series.str[4:24], format="%b %d %Y %H:%M:%S", errors="coerce")
    return parsed - timedelta(hours=9)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="data/raw", type=Path)
    ap.add_argument("--out-dir", default="docs/evidence/dictionary_counts", type=Path)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir

    files = {n: args.data_dir / f"starrydata_{n}.csv" for n in ("papers", "samples", "curves")}
    papers = pd.read_csv(files["papers"], low_memory=False)
    samples = pd.read_csv(files["samples"], low_memory=False)
    curves = pd.read_csv(files["curves"], low_memory=False)
    summary = {"sha256": {f.name: sha256(f) for f in files.values()},
               "rows": {"papers": len(papers), "samples": len(samples), "curves": len(curves)}}

    # ---------------- Appendix A: sample_info descriptors -----------------
    project_of = dict(zip(papers.SID, papers.project_names.map(
        lambda v: json.loads(v) if isinstance(v, str) else [])))
    raw_keys, ws_keys = set(), set()
    present, nonempty, raw_variants = defaultdict(set), defaultdict(set), defaultdict(set)
    merge = defaultdict(Counter)
    conflicts = []
    for sid, paper, info in zip(samples.sample_id, samples.SID, samples.sample_info):
        if not isinstance(info, str):
            continue
        groups = defaultdict(list)                       # canonical -> [(raw key, flat value)]
        for key, val in json.loads(info).items():
            raw_keys.add(key)
            ws_keys.add(ws_norm(key))
            col = canonical(key)
            raw_variants[col].add(key)
            present[col].add(sid)
            flat = flatten_value(val)
            groups[col].append((key, flat))
            if flat:
                nonempty[col].add(sid)
        for col, items in groups.items():
            if len(items) < 2:
                continue
            m = merge[col]
            m["records_with_variants"] += 1
            values = [v for _, v in items]
            distinct_nonempty = sorted({v for v in values if v})
            if len(set(values)) > 1:
                m["values_differ"] += 1
            if len(distinct_nonempty) == 1 and "" in values:
                m["one_nonempty_rest_empty"] += 1
            if len(distinct_nonempty) > 1:
                m["two_nonempty_differ"] += 1
                conflicts.append({"sample_id": sid, "SID": paper, "output_column": col,
                                  "source_keys": " || ".join(repr(k) for k, _ in items),
                                  "values": " || ".join(repr(v) for _, v in items)})
    top_project = {}
    for col in present:
        cnt = Counter()
        sid_to_paper = dict(zip(samples.sample_id, samples.SID))
        for sid in nonempty[col]:
            cnt.update(project_of.get(sid_to_paper[sid], []))
        top_project[col] = cnt.most_common(1)[0][0] if cnt else ""
    rows = [{"output_column": c, "group": GROUP_OF.get(c, "Ungrouped"),
             "source_keys_merged": len(raw_variants[c]),
             "samples_with_key": len(present[c]), "samples_with_value": len(nonempty[c]),
             "top_project_where_populated": top_project[c]} for c in present]
    desc = pd.DataFrame(rows).sort_values(["group", "samples_with_key", "output_column"],
                                          ascending=[True, False, True])
    desc.to_csv(out / "appendix_a_descriptors.csv", index=False)
    pd.DataFrame([{"output_column": c, **dict(m)} for c, m in sorted(merge.items())]) \
        .fillna(0).to_csv(out / "appendix_a_merge_report.csv", index=False)
    pd.DataFrame(conflicts).to_csv(out / "sample_info_merge_conflicts.csv", index=False)

    lines = []
    ordered = list(GROUPS) + (["Ungrouped"] if (desc.group == "Ungrouped").any() else [])
    for g in ordered:
        sub = desc[desc.group == g].sort_values(["samples_with_key", "output_column"],
                                                ascending=[False, True])
        lines += [f"#### {g}", "",
                  "| Output column | Source keys merged | Samples with key | Samples with a value |",
                  "|---|---|---|---|"]
        for r in sub.itertuples():
            lines.append(f"| `{md_escape(r.output_column)}` | {r.source_keys_merged} | "
                         f"{r.samples_with_key:,} | {r.samples_with_value:,} |")
        lines.append("")
    (out / "appendix_a.md").write_text("\n".join(lines), encoding="utf-8")

    # string values are checked so the 'one conflicting-value' statement is exact
    summary["sample_info"] = {
        "raw_keys": len(raw_keys), "after_whitespace_normalisation": len(ws_keys),
        "after_variant_mapping": len(present),
        "merge_records_with_variants": sum(m["records_with_variants"] for m in merge.values()),
        "merge_values_differ": sum(m["values_differ"] for m in merge.values()),
        "merge_one_nonempty_rest_empty": sum(m["one_nonempty_rest_empty"] for m in merge.values()),
        "merge_two_nonempty_differ": sum(m["two_nonempty_differ"] for m in merge.values()),
        "ungrouped_columns": desc[desc.group == "Ungrouped"].output_column.tolist(),
    }

    # ---------------- Appendix B: property / unit vocabulary --------------
    def vocab(prop_col, unit_col):
        g = curves.groupby(prop_col)
        t = pd.DataFrame({"curves": g.size(),
                          "most_common_unit": g[unit_col].agg(lambda x: x.value_counts().index[0]),
                          "distinct_units": g[unit_col].nunique()})
        return t.sort_values(["curves"], ascending=False).reset_index()
    vy, vx = vocab("prop_y", "unit_y"), vocab("prop_x", "unit_x")
    vy.to_csv(out / "appendix_b_prop_y.csv", index=False)
    vx.to_csv(out / "appendix_b_prop_x.csv", index=False)
    md = []
    for name, v, n, col in (("prop_y", vy, TOP_N_Y, "unit_y"), ("prop_x", vx, TOP_N_X, "unit_x")):
        md += [f"| `{name}` | Most common `{col}` | Curves |", "|---|---|---|"]
        for r in v.head(n).itertuples():
            md.append(f"| `{md_escape(r[1])}` | `{md_escape(r.most_common_unit)}` | {r.curves:,} |")
        md.append("")
    (out / "appendix_b.md").write_text("\n".join(md), encoding="utf-8")
    multi = vy[vy.distinct_units > 1].iloc[:, 0].tolist()
    summary["properties"] = {"distinct_prop_x": len(vx), "distinct_prop_y": len(vy),
                             "distinct_unit_x": curves.unit_x.nunique(),
                             "distinct_unit_y": curves.unit_y.nunique(),
                             "prop_y_with_more_than_one_unit": multi}

    # ---------------- Unit notations (FAIR I2) ------------------------------
    unit_rows = []
    for group, units in UNIT_NOTATION_GROUPS.items():
        for u in units:
            sub_y = curves[curves.unit_y == u]
            unit_rows.append({"unit_group": group, "unit_string": u,
                              "curves_in_unit_y": len(sub_y),
                              "curves_in_unit_x": int((curves.unit_x == u).sum()),
                              "top_prop_y": "; ".join(f"{k} ({v:,})" for k, v in
                                                      sub_y.prop_y.value_counts().head(3).items())})
    unit_df = pd.DataFrame(unit_rows)
    unit_df.to_csv(out / "unit_notations.csv", index=False)
    summary["unit_notations"] = {g: {r.unit_string: r.curves_in_unit_y for r in
                                     unit_df[unit_df.unit_group == g].itertuples()}
                                 for g in UNIT_NOTATION_GROUPS}

    # ---------------- Tier 2 scope (D4) and excluded variants -------------
    te = curves[curves.project_names.str.contains(TIER2_PROJECT)]
    tier2 = te[te.prop_y.isin(TIER2_PROPS) & (te.prop_x == TIER2_PROP_X)]
    exact = te[te.prop_y.isin(TIER2_PROPS)]
    per_prop_units = {p: tier2[tier2.prop_y == p].unit_y.value_counts().to_dict() for p in TIER2_PROPS}
    var_rows = []
    tab = te.groupby("prop_y").agg(curves=("prop_y", "size"),
                                   unit_y=("unit_y", lambda x: x.value_counts().index[0]))
    for fam, rx in VARIANT_PATTERNS.items():
        for name, r in tab.iterrows():
            if name in TIER2_PROPS or not re.search(rx, name, re.I):
                continue
            if fam == "Electrical conductivity" and "thermal" in name.lower():
                continue
            var_rows.append({"core_property": fam, "excluded_name": name,
                             "curves": int(r.curves), "recorded_unit_y": r.unit_y})
    var_df = pd.DataFrame(var_rows).sort_values(["core_property", "curves"], ascending=[True, False])
    var_df.to_csv(out / "tier2_excluded_variants.csv", index=False)
    xvar = exact[(exact.prop_x != TIER2_PROP_X)].prop_x.value_counts().to_dict()
    summary["tier2"] = {
        "thermoelectric_curves": len(te), "thermoelectric_distinct_prop_y": te.prop_y.nunique(),
        "thermoelectric_distinct_unit_y": te.unit_y.nunique(),
        "tier2_curves": len(tier2), "units_per_core_property": per_prop_units,
        "core_name_curves_total": len(exact),
        "core_name_curves_excluded_by_prop_x": len(exact) - len(tier2),
        "excluded_prop_x_distinct_values": len(xvar),
        "excluded_prop_x_top10": dict(list(xvar.items())[:10]),
        "excluded_variant_names": int(len(var_df)),
        "excluded_variant_curves": int(var_df.curves.sum()),
    }

    # ---------------- curve_points contract (D11) -------------------------
    lens = curves.x.map(lambda v: len(json.loads(v)))
    ylens = curves.y.map(lambda v: len(json.loads(v)))
    t2_idx = tier2.index
    summary["curve_points"] = {
        "curve_key_figure_id_sample_id_duplicates": int(curves.duplicated(["figure_id", "sample_id"]).sum()),
        "null_figure_id": int(curves.figure_id.isna().sum()),
        "fully_duplicate_rows": int(curves.duplicated().sum()),
        "x_y_length_mismatches": int((lens != ylens).sum()),
        "total_points": int(lens.sum()), "curves_non_empty": int((lens > 0).sum()),
        "curves_empty_arrays": int((lens == 0).sum()), "curves_single_point": int((lens == 1).sum()),
        "median_points_per_curve": float(lens.median()), "max_points_per_curve": int(lens.max()),
        "tier2_points": int(lens[t2_idx].sum()), "tier2_curves_non_empty": int((lens[t2_idx] > 0).sum()),
        "tier2_curves_empty": int((lens[t2_idx] == 0).sum()),
    }

    # ---------------- Dates (D8, D10) -------------------------------------
    stamps = {}
    for tname, df in (("samples", samples), ("curves", curves)):
        stamps[f"{tname}.updated_before_created"] = int((to_utc(df["updated_at"]) < to_utc(df["created_at"])).sum())
    for tname, df in (("papers", papers), ("samples", samples), ("curves", curves)):
        for col in [c for c in ("created_at", "updated_at") if c in df.columns]:
            u = to_utc(df[col])
            stamps[f"{tname}.{col}"] = {"parse_failures": int(u.isna().sum()),
                                        "min_utc": str(u.min()), "max_utc": str(u.max()),
                                        "after_snapshot": int((u > SNAPSHOT_UTC).sum())}
    invalid_parts = Counter()

    def date_parts(v):
        """Integer date parts as recorded. '' (empty-string year) and {} mean no date.
        Precision follows the STRUCTURE of the list (3 = full, 2 = year-month,
        1 = year), which is the rule implemented in Tableau (T2.2) and Python (D8).
        Out-of-range months/days are kept and only counted, so they can be flagged."""
        if not isinstance(v, str):
            return []
        parts = (json.loads(v).get("date_parts") or [[]])[0]
        out_ = []
        for i, p in enumerate(parts):
            if not isinstance(p, int):
                break
            if i == 1 and not 1 <= p <= 12:
                invalid_parts["month"] += 1
            if i == 2:
                try:
                    datetime(out_[0], out_[1], p)
                except ValueError:
                    invalid_parts["day"] += 1
            out_.append(p)
        return out_
    iss = papers.issued.map(date_parts)
    prec = iss.map(lambda p: {3: "full", 2: "year-month", 1: "year"}.get(len(p), "none"))
    empty_obj = int((papers.issued == "{}").sum())
    empty_year = int(papers.issued.str.contains(r'\[\[""\]\]', regex=True, na=False).sum())
    years = iss.map(lambda p: p[0] if len(p) >= 1 else None).dropna()
    summary["timestamps_utc"] = stamps
    summary["issued"] = {"precision_counts": prec.value_counts().to_dict(),
                         "none_because_empty_object": empty_obj,
                         "none_because_empty_string_year": empty_year,
                         "year_min": int(years.min()), "year_max": int(years.max()),
                         "invalid_month_kept_as_recorded": invalid_parts["month"],
                         "invalid_day_kept_as_recorded": invalid_parts["day"]}

    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
