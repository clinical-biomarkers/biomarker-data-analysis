# biomarker-data-analysis
This repository contains data analysis scripts for BiomarkerKB

To print the "skeleton" of a JSON file:
```
jq '[leaf_paths | join(".")] | map(gsub("\\.[0-9]+\\."; ".*.") | gsub("\\.[0-9]+$"; ".*") | gsub("^[0-9]+\\."; "")) | unique | .[]' file.json
```
The three passes handle:
- `.[0-9]+.` → middle indices like .0.
- `.[0-9]+$` → trailing indices like .0
- `^[0-9]+.` → leading index like 0.

# Scripts
Make sure to activate your Python virtual environment before running.

## `pmid_biomarker_count.py`
Scans the BiomarkerDB JSON batch files and outputs a quoted CSV of PubMed IDs (PMIDs) associated with 10 or more distinct biomarkers.
### Output
A CSV with columns:
- `pmid` — PubMed ID
- `database` — semicolon-delimited list of evidence databases associated with that PMID
### Logic
For each biomarker object, each citation is processed independently: its PubMed references are paired with its evidence databases to produce (`biomarker_id`, `pmid`, `database`) tuples. Tuples are deduplicated globally. PMIDs appearing in fewer than 10 distinct biomarkers are excluded.
### Usage
```bash
python pmid_biomarker_count.py > output.csv
```
