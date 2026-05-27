#!/usr/bin/env python3
import pandas as pd
import json
import sys

def compare_tsv_files(file1_path, file2_path, output_json_path):
    """
    Compare two TSV files and create a JSON with differences grouped by biomarker.
    
    Args:
        file1_path: Path to first TSV file
        file2_path: Path to second TSV file
        output_json_path: Path for output JSON file
    """
    # Read both TSV files
    df1 = pd.read_csv(file1_path, sep=',')
    df2 = pd.read_csv(file2_path, sep=',')
    
    # Columns to disregard
    columns_to_ignore = ['biomarker_canonical_id', 'evidence', 'tag']
    
    # Remove ignored columns if they exist
    for col in columns_to_ignore:
        if col in df1.columns:
            df1 = df1.drop(columns=[col])
        if col in df2.columns:
            df2 = df2.drop(columns=[col])
    
    # Make string columns case-insensitive for comparison
    for col in df1.columns:
        if df1[col].dtype == 'object':
            df1[col] = df1[col].astype(str).str.strip()
            df2[col] = df2[col].astype(str).str.strip()
    
    # Get biomarker column
    if 'biomarker' not in df1.columns:
        raise ValueError("'biomarker' column not found in the files")
    
    # Group by biomarker
    biomarkers = set(df1['biomarker'].unique()) | set(df2['biomarker'].unique())
    
    result = {}
    
    for biomarker in biomarkers:
        # Get rows for this biomarker from both files
        df1_biomarker = df1[df1['biomarker'] == biomarker].copy()
        df2_biomarker = df2[df2['biomarker'] == biomarker].copy()
        
        if df1_biomarker.empty and df2_biomarker.empty:
            continue
        
        # Find differences for each column
        biomarker_diffs = {}
        
        # Get all columns except biomarker itself
        comparison_columns = [col for col in df1.columns if col != 'biomarker']
        
        for col in comparison_columns:
            # Get values from both dataframes
            values1 = set(df1_biomarker[col].dropna().unique()) if not df1_biomarker.empty else set()
            values2 = set(df2_biomarker[col].dropna().unique()) if not df2_biomarker.empty else set()
            
            # Find all unique values across both files
            all_values = values1 | values2
            
            # Only include if there are differences
            if values1 != values2 and len(all_values) > 0:
                # Combine all values from both files
                biomarker_diffs[col] = sorted(list(all_values))
        
        # Only add biomarker to result if there are differences
        if biomarker_diffs:
            result[biomarker] = biomarker_diffs
    
    # Write to JSON file
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"Comparison complete. Results saved to {output_json_path}")
    print(f"Found differences for {len(result)} biomarker(s)")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compare_tsv.py <file1.tsv> <file2.tsv> <output.json>")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output = sys.argv[3]
    
    compare_tsv_files(file1, file2, output)
