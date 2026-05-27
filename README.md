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
