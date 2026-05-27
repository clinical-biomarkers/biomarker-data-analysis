#!/usr/bin/env python3
"""
Biomarker Join Script
Performs inner join between v2.6 and v2.9 processed files by assessed_biomarker_entity_id
"""

import pandas as pd
import sys
from pathlib import Path


def join_biomarker_files(v26_file, v29_file, output_file):
    """
    Join v2.6 and v2.9 processed files by assessed_biomarker_entity_id
    
    Args:
        v26_file: Path to biomarker2.6_processed.csv
        v29_file: Path to biomarker2.9_processed.csv
        output_file: Path to output TSV file
    """
    print("=" * 80)
    print("BIOMARKER INNER JOIN")
    print("=" * 80)
    
    # Load files
    print(f"\n📂 Loading files...")
    try:
        df_v26 = pd.read_csv(v26_file, dtype=str)
        print(f"✓ Loaded {v26_file}: {len(df_v26)} records")
    except Exception as e:
        print(f"❌ ERROR loading {v26_file}: {e}")
        return False
    
    try:
        df_v29 = pd.read_csv(v29_file, dtype=str)
        print(f"✓ Loaded {v29_file}: {len(df_v29)} records")
    except Exception as e:
        print(f"❌ ERROR loading {v29_file}: {e}")
        return False
    
    # Check required columns
    print(f"\n🔍 Checking required columns...")
    required_cols = ['biomarker_id', 'biomarker', 'assessed_biomarker_entity', 'assessed_biomarker_entity_id']
    
    missing_v26 = [col for col in required_cols if col not in df_v26.columns]
    missing_v29 = [col for col in required_cols if col not in df_v29.columns]
    
    if missing_v26:
        print(f"❌ ERROR: v2.6 file missing columns: {missing_v26}")
        return False
    if missing_v29:
        print(f"❌ ERROR: v2.9 file missing columns: {missing_v29}")
        return False
    
    print(f"✓ All required columns present")
    
    # Select columns for join
    cols_to_keep = ['biomarker_id', 'biomarker', 'assessed_biomarker_entity', 'assessed_biomarker_entity_id']
    df_v26_subset = df_v26[cols_to_keep].copy()
    df_v29_subset = df_v29[cols_to_keep].copy()
    
    print(f"\n🔗 Performing inner join on 'assessed_biomarker_entity_id'...")
    
    # Perform inner join
    result = pd.merge(
        df_v29_subset,
        df_v26_subset,
        on='assessed_biomarker_entity_id',
        how='inner',
        suffixes=('_v29', '_v26')
    )
    
    print(f"✓ Join completed: {len(result)} matching records")
    
    # Reorder columns to match requested output
    output_columns = [
        'biomarker_id_v29',
        'biomarker_v29',
        'assessed_biomarker_entity_v29',
        'assessed_biomarker_entity_id',
        'biomarker_id_v26',
        'biomarker_v26',
        'assessed_biomarker_entity_v26'
    ]
    
    result = result[output_columns]
    
    # Rename columns to be clearer
    result.columns = [
        'biomarker_id_v2.9',
        'biomarker_v2.9',
        'assessed_biomarker_entity_v2.9',
        'assessed_biomarker_entity_id',
        'biomarker_id_v2.6',
        'biomarker_v2.6',
        'assessed_biomarker_entity_v2.6'
    ]
    
    # Save to TSV
    print(f"\n💾 Saving to {output_file}...")
    try:
        result.to_csv(output_file, sep='\t', index=False)
        print(f"✓ Successfully saved {len(result)} records to {output_file}")
    except Exception as e:
        print(f"❌ ERROR saving file: {e}")
        return False
    
    # Print summary statistics
    print(f"\n📊 Summary:")
    print(f"  v2.6 input records: {len(df_v26)}")
    print(f"  v2.9 input records: {len(df_v29)}")
    print(f"  Matched records: {len(result)}")
    print(f"  Match rate v2.9: {len(result)/len(df_v29)*100:.1f}%")
    print(f"  Match rate v2.6: {len(result)/len(df_v26)*100:.1f}%")
    
    # Check for differences in matched records
    print(f"\n🔍 Checking for differences in matched records:")
    
    # Compare biomarker_id
    id_differences = (result['biomarker_id_v2.9'] != result['biomarker_id_v2.6']).sum()
    print(f"  Biomarker ID changes: {id_differences}/{len(result)}")
    
    # Compare biomarker name
    biomarker_differences = (result['biomarker_v2.9'] != result['biomarker_v2.6']).sum()
    print(f"  Biomarker name changes: {biomarker_differences}/{len(result)}")
    
    # Compare entity name
    entity_differences = (result['assessed_biomarker_entity_v2.9'] != result['assessed_biomarker_entity_v2.6']).sum()
    print(f"  Entity name changes: {entity_differences}/{len(result)}")
    
    if id_differences > 0 or biomarker_differences > 0 or entity_differences > 0:
        print(f"\n  ⚠️  Some fields changed between versions!")
        
        # Show examples of differences
        if id_differences > 0:
            print(f"\n  Sample biomarker_id changes:")
            diff_rows = result[result['biomarker_id_v2.9'] != result['biomarker_id_v2.6']].head(3)
            for idx, row in diff_rows.iterrows():
                print(f"    {row['biomarker_id_v2.6']} → {row['biomarker_id_v2.9']}")
    else:
        print(f"  ✓ All matched records have consistent values")
    
    print(f"\n{'=' * 80}")
    print(f"Join complete! ✓")
    print(f"{'=' * 80}")
    
    return True


def main():
    """Main entry point"""
    # File paths
    v26_file = "biomarker2.6_processed.csv"
    v29_file = "biomarker2.9_processed.csv"
    output_file = "biomarker_joined.tsv"
    
    # Check if input files exist
    if not Path(v26_file).exists():
        print(f"❌ ERROR: {v26_file} not found in current directory")
        print(f"   Please ensure the file is in the same directory as this script")
        sys.exit(1)
    
    if not Path(v29_file).exists():
        print(f"❌ ERROR: {v29_file} not found in current directory")
        print(f"   Please ensure the file is in the same directory as this script")
        sys.exit(1)
    
    # Perform join
    success = join_biomarker_files(v26_file, v29_file, output_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
