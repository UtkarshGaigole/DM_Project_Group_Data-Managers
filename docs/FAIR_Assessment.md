# FAIR Assessment and Metadata Record (Before Clean up)

**Dataset:** Starrydata dataset snapshot  
**Version DOI:** [10.6084/m9.figshare.34036677.v1](https://doi.org/10.6084/m9.figshare.34036677.v1)  
**Dataset files:** `starrydata_papers.csv`, `starrydata_samples.csv`, `starrydata_curves.csv`  
**Assessment prepared by:** Project Group "Data-Managers", SRH University of Applied Sciences Heidelberg  
**Assessment date:** 5 November 2026  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Assessment method:** Manual review of the dataset record and its documentation, supplemented by the group’s F-UJI assessment.

## 1. Dataset and metadata record
 
Starrydata contains data digitized from figures in materials science publications. Its files describe papers, material samples, and curves. The documented schema uses `SID` to link papers, samples, and curves, and `sample_id` to relate samples and curves. Some fields contain JSON-encoded data, including sample descriptors and curve point arrays.

The Figshare DOI identifies this specific dataset version, supporting reproducible citation. The dataset record and accompanying documentation provide citation information; the paper and curve records also include bibliographic identifiers such as DOI.

| Metadata element | Record |
|---|---|
| Title | Starrydata dataset snapshot |
| Repository | Figshare |
| Version DOI | 10.6084/m9.figshare.34036677.v1 |
| Data files | `starrydata_papers.csv`; `starrydata_samples.csv`; `starrydata_curves.csv` |
| Data format | CSV, with some JSON-encoded fields |
| License | CC BY 4.0 |
| Domain | Materials science; thermoelectric, battery, and magnetic materials |
| Citation | Cite the version DOI and Starrydata publication; cite original source papers when using their data |
| Retrieval date | [Enter the date your group downloaded the files] |

## 2. FAIR assessment

Scores use **Satisfied**, **Partially satisfied**, and **Failed**. They describe the dataset and its documentation as assessed by the group; they are not a substitute for the F-UJI report.

### F-UJI - FAIR Assessment Summary

| FAIR Principle      | Score Earned | Fair Level |
|---------------------|-------------|------------|
| Findable (F)        | 4 of 7      | Moderate   |
| Accessible (A)      | 3 of 7      | Moderate   |
| Interoperable (I)   | 4 of 6      | Moderate   |
| Reusable (R)        | 4 of 6      | Initial    |


### Findable

| Sub-criterion | Score | Justification |
|---|---|---|
| F1 — The data is assigned a globally unique and persistent identifier. | **Satisfied** | The Figshare snapshot has a version-specific DOI: `10.6084/m9.figshare.34036677.v1`. |
| F2 — The data is described with rich metadata. | **Partially satisfied** | The record provides citation metadata, and the files include paper, sample, and curve fields, but the completeness of domain-specific metadata needs further evaluation.
| F3 — Metadata clearly includes the identifier of the data it describes. | **Satisfied** | The DOI identifies the specific snapshot described by the Figshare metadata. |
| F4 — Metadata is registered or indexed in a searchable resource. | **Partially  Satisfied** | The dataset is discoverable through Figshare, but additional indexing and search-engine discoverability should be verified.ys. |

### Accessible

| Sub-criterion | Score | Justification |
|---|---|---|
| A1.1 — Data can be retrieved using a standard communications protocol. | **Satisfied** | The public Figshare record and files are retrievable through the web using HTTPS. |
| A1.2 — The protocol is open, free, and universally implementable. | **Satisfied** | HTTPS is an open, widely supported protocol and does not require proprietary access software. |
| A1.2.1 — The protocol allows authentication and authorization where necessary. | **Satisfied** | The snapshot is publicly accessible without authentication; authentication is not required for this dataset. |
| A2 — Metadata remains accessible even if the data is no longer available. | **Partially satisfied** | The DOI provides a persistent record, but long-term metadata availability should be considered separately from file availability. |

### Interoperable

| Sub-criterion | Score | Justification |
|---|---|---|
| I1 — The data uses a formal, accessible, shared, and broadly applicable language for knowledge representation. | **Partially satisfied** | CSV and JSON are open, machine-readable formats, but the files do not appear to express their data model through a formal semantic framework such as RDF. |
| I2 — The data uses vocabularies that follow FAIR principles. | **Partially satisfied** | The schema documents domain-specific fields and SI-style unit notation, but the group has not identified mappings to shared, controlled materials-science vocabularies for all properties and descriptors. |
| I3 — The data includes qualified references to other data. | **Partially satisfied** | DOI, `SID`, and `sample_id` fields support links between records and source papers, but their relational integrity must be validated. |

### Reusable

| Sub-criterion | Score | Justification |
|---|---|---|
| R1.1 — The data is released with a clear and accessible data usage license. | **Satisfied** | The dataset is licensed under CC BY 4.0, as confirmed by Dr. Mato. |
| R1.2 — The data is associated with detailed provenance. | **Partially satisfied** | Citation metadata and links to original papers provide provenance, but users may need additional extraction and curation details to reproduce every digitized value. |
| R1.3 — The data meets domain-relevant community standards. | **Partially satisfied** | The dataset documents its tables, fields, relationships, and units, but its CSV/JSON schema is not fully mapped to a shared community data model. |

## 3. Summary

The dataset is **strongly findable and accessible** because the snapshot has a DOI and is publicly retrievable. Its **interoperability is partial**: CSV and JSON are machine-readable, but the group has not established that all field names and descriptors use shared, controlled vocabularies. Its **reusability is supported** by the CC BY 4.0 license and citation metadata, while further provenance and schema documentation would help users reproduce and combine the data.

## 4. Evidence and references

- Figshare dataset snapshot: <https://doi.org/10.6084/m9.figshare.34036677.v1>
- Starrydata download documentation and data schema: <https://starrydata.github.io/hp/en/manual/download/>
- Starrydata citation guidance: <https://starrydata.github.io/hp/cite/>
- F-UJI FAIR assessment: <https://www.f-uji.net/index.php>
- License: CC BY 4.0

