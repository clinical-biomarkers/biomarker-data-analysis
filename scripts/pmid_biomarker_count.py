#!/usr/bin/env python3
import json
import glob
import csv
import sys
from collections import defaultdict

data_dir = "/data/shared/biomarkerdb/releases/data/current/jsondb/biomarkerdb"

# intermediate: set of (biomarker_id, pmid, database) tuples
tuples = set()

for filepath in glob.glob(f"{data_dir}/batch.*.json"):
    with open(filepath) as f:
        batch = json.load(f)
    for obj in batch:
        biomarker_id = obj.get("biomarker_id")
        if not biomarker_id:
            continue
        citations = obj.get("citation", [])
        pmids = set()
        databases = set()
        for citation in citations:
            pmids = set()
            databases = set()
            for ref in citation.get("reference", []):
                if ref.get("type") == "PubMed":
                    pmids.add(ref.get("id"))
            for evidence in citation.get("evidence", []):
                db = evidence.get("database")
                if db:
                    databases.add(db)
        for pmid in pmids:
            for db in databases:
                if pmid:
                    tuples.add((biomarker_id, pmid, db))

# group by pmid
pmid_biomarkers = defaultdict(set)
pmid_databases = defaultdict(set)

for biomarker_id, pmid, db in tuples:
    pmid_biomarkers[pmid].add(biomarker_id)
    pmid_databases[pmid].add(db)

writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
writer.writerow(["pmid", "database"])

for pmid, biomarkers in pmid_biomarkers.items():
    if len(biomarkers) >= 10:
        writer.writerow([pmid, ";".join(sorted(pmid_databases[pmid]))])
