#!/usr/bin/env python3
"""
Biomarker Investigation Script
Investigates why glycan biomarker count dropped from 95 (v2.6) to 19 (v2.9)
"""

import pandas as pd
import sys
from pathlib import Path
from collections import defaultdict

class BiomarkerInvestigator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.results = {}
        
    def load_files(self):
        """Load all four files"""
        print("=" * 80)
        print("LOADING FILES")
        print("=" * 80)
        
        files = {
            'v26_source': 'biomarker2.6_source.tsv',
            'v26_processed': 'biomarker2.6_processed.csv',
            'v29_source': 'biomarker2.9_source.tsv',
            'v29_processed': 'biomarker2.9_processed.csv'
        }
        
        data = {}
        for key, filename in files.items():
            filepath = self.base_path / filename
            if not filepath.exists():
                print(f"❌ ERROR: {filename} not found at {filepath}")
                return None
            
            try:
                if filename.endswith('.tsv'):
                    df = pd.read_csv(filepath, sep='\t', dtype=str)
                else:
                    df = pd.read_csv(filepath, dtype=str)
                
                data[key] = df
                print(f"✓ Loaded {filename}: {len(df)} records, {len(df.columns)} columns")
            except Exception as e:
                print(f"❌ ERROR loading {filename}: {e}")
                return None
        
        self.data = data
        return data
    
    def phase1_record_counts(self):
        """Phase 1: Count records at each stage"""
        print("\n" + "=" * 80)
        print("PHASE 1: RECORD COUNTS")
        print("=" * 80)
        
        results = {}
        
        # Source files
        print("\n📊 Source Files (Your Data):")
        results['v26_source_total'] = len(self.data['v26_source'])
        results['v29_source_total'] = len(self.data['v29_source'])
        print(f"  v2.6 source: {results['v26_source_total']:,} records")
        print(f"  v2.9 source: {results['v29_source_total']:,} records")
        print(f"  Change: {results['v29_source_total'] - results['v26_source_total']:+,} records")
        
        # Processed files (glycan only)
        print("\n📊 Processed Files (GlyGen's Output - Glycan Only):")
        results['v26_processed_glycans'] = len(self.data['v26_processed'])
        results['v29_processed_glycans'] = len(self.data['v29_processed'])
        print(f"  v2.6 glycan biomarkers: {results['v26_processed_glycans']:,}")
        print(f"  v2.9 glycan biomarkers: {results['v29_processed_glycans']:,}")
        print(f"  Change: {results['v29_processed_glycans'] - results['v26_processed_glycans']:+,} glycans")
        print(f"  📉 DROP: {results['v26_processed_glycans'] - results['v29_processed_glycans']} glycans lost!")
        
        self.results['counts'] = results
        return results
    
    def phase2_identify_glycans_in_source(self):
        """Phase 2: Identify glycan biomarkers in source files"""
        print("\n" + "=" * 80)
        print("PHASE 2: GLYCAN IDENTIFICATION IN SOURCE DATA")
        print("=" * 80)
        
        # Check what identifies a glycan in source files
        print("\n🔍 Checking 'assessed_entity_type' field in source files:")
        
        results = {}
        for version in ['v26', 'v29']:
            key = f'{version}_source'
            df = self.data[key]
            
            if 'assessed_entity_type' in df.columns:
                entity_types = df['assessed_entity_type'].value_counts()
                glycan_count = (df['assessed_entity_type'] == 'glycan').sum()
                results[f'{version}_source_glycans'] = glycan_count
                
                print(f"\n  {version.upper()} Source:")
                print(f"    Glycan records: {glycan_count}")
                print(f"    Entity type breakdown:")
                for entity_type, count in entity_types.head(10).items():
                    print(f"      - {entity_type}: {count}")
            else:
                print(f"  ⚠️  '{version}_source' missing 'assessed_entity_type' column")
        
        # Compare glycan counts
        if 'v26_source_glycans' in results and 'v29_source_glycans' in results:
            print(f"\n📊 Glycan Comparison in Source:")
            print(f"  v2.6 source glycans: {results['v26_source_glycans']}")
            print(f"  v2.9 source glycans: {results['v29_source_glycans']}")
            print(f"  Change: {results['v29_source_glycans'] - results['v26_source_glycans']:+,}")
        
        self.results['glycan_identification'] = results
        return results
    
    def phase3_trace_missing_biomarkers(self):
        """Phase 3: Identify which specific biomarkers were lost"""
        print("\n" + "=" * 80)
        print("PHASE 3: TRACING MISSING BIOMARKERS")
        print("=" * 80)
        
        # Get IDs from processed files (these are the glycans that made it through)
        v26_processed_ids = set(self.data['v26_processed']['biomarker_id'].dropna())
        v29_processed_ids = set(self.data['v29_processed']['biomarker_id'].dropna())
        
        print(f"\n🔍 Processed file biomarker IDs:")
        print(f"  v2.6: {len(v26_processed_ids)} unique IDs")
        print(f"  v2.9: {len(v29_processed_ids)} unique IDs")
        
        # Find missing IDs
        missing_ids = v26_processed_ids - v29_processed_ids
        remaining_ids = v26_processed_ids & v29_processed_ids
        new_ids = v29_processed_ids - v26_processed_ids
        
        print(f"\n📊 ID Changes:")
        print(f"  ✓ Remained: {len(remaining_ids)} glycan biomarkers")
        print(f"  ❌ Lost: {len(missing_ids)} glycan biomarkers")
        print(f"  ➕ New: {len(new_ids)} glycan biomarkers")
        
        # Check if missing IDs are in v2.9 source
        if 'biomarker_id' in self.data['v29_source'].columns:
            v29_source_ids = set(self.data['v29_source']['biomarker_id'].dropna())
            missing_in_source = missing_ids - v29_source_ids
            missing_but_in_source = missing_ids & v29_source_ids
            
            print(f"\n🔍 Where did the {len(missing_ids)} lost glycans go?")
            print(f"  {len(missing_in_source)} - Removed from your source data entirely")
            print(f"  {len(missing_but_in_source)} - Still in source but filtered out by GlyGen")
        
        self.results['missing_ids'] = missing_ids
        self.results['remaining_ids'] = remaining_ids
        self.results['new_ids'] = new_ids
        
        return missing_ids, remaining_ids, new_ids
    
    def phase4_deep_dive_missing_records(self, sample_size=10):
        """Phase 4: Examine sample of missing records in detail"""
        print("\n" + "=" * 80)
        print("PHASE 4: DETAILED ANALYSIS OF MISSING RECORDS")
        print("=" * 80)
        
        missing_ids = self.results.get('missing_ids', set())
        if not missing_ids:
            print("No missing IDs to analyze")
            return
        
        # Sample some missing IDs
        sample_ids = list(missing_ids)[:sample_size]
        print(f"\n🔬 Examining {len(sample_ids)} sample missing biomarkers:")
        
        for i, bio_id in enumerate(sample_ids, 1):
            print(f"\n  [{i}] Biomarker ID: {bio_id}")
            
            # Find in v2.6 processed
            v26_proc = self.data['v26_processed'][
                self.data['v26_processed']['biomarker_id'] == bio_id
            ]
            if not v26_proc.empty:
                row = v26_proc.iloc[0]
                print(f"      ✓ Found in v2.6 processed:")
                print(f"        - Biomarker: {row.get('biomarker', 'N/A')}")
                print(f"        - Entity: {row.get('assessed_biomarker_entity', 'N/A')}")
                print(f"        - Entity ID: {row.get('assessed_biomarker_entity_id', 'N/A')}")
                print(f"        - Entity Type: {row.get('assessed_entity_type', 'N/A')}")
                print(f"        - GlyTouCan AC: {row.get('glytoucan_ac', 'N/A')}")
            
            # Check if in v2.9 source
            if 'biomarker_id' in self.data['v29_source'].columns:
                v29_source = self.data['v29_source'][
                    self.data['v29_source']['biomarker_id'] == bio_id
                ]
                if not v29_source.empty:
                    row = v29_source.iloc[0]
                    print(f"      ⚠️  Found in v2.9 source but NOT in v2.9 processed:")
                    print(f"        - Entity Type: {row.get('assessed_entity_type', 'N/A')}")
                    print(f"        - Entity ID: {row.get('assessed_biomarker_entity_id', 'N/A')}")
                    print(f"        - Condition: {row.get('condition', 'N/A')}")
                else:
                    print(f"      ❌ NOT found in v2.9 source - removed from your data")
    
    def phase5_column_comparison(self):
        """Phase 5: Compare column structures"""
        print("\n" + "=" * 80)
        print("PHASE 5: COLUMN STRUCTURE COMPARISON")
        print("=" * 80)
        
        print("\n📋 Source File Columns:")
        v26_src_cols = set(self.data['v26_source'].columns)
        v29_src_cols = set(self.data['v29_source'].columns)
        
        print(f"  v2.6: {len(v26_src_cols)} columns")
        print(f"  v2.9: {len(v29_src_cols)} columns")
        
        removed_cols = v26_src_cols - v29_src_cols
        added_cols = v29_src_cols - v26_src_cols
        
        if removed_cols:
            print(f"  ❌ Removed columns: {', '.join(removed_cols)}")
        if added_cols:
            print(f"  ➕ Added columns: {', '.join(added_cols)}")
        if not removed_cols and not added_cols:
            print(f"  ✓ No column changes")
        
        print("\n📋 Processed File Columns:")
        v26_proc_cols = set(self.data['v26_processed'].columns)
        v29_proc_cols = set(self.data['v29_processed'].columns)
        
        print(f"  v2.6: {len(v26_proc_cols)} columns")
        print(f"  v2.9: {len(v29_proc_cols)} columns")
        
        removed_cols = v26_proc_cols - v29_proc_cols
        added_cols = v29_proc_cols - v26_proc_cols
        
        if removed_cols:
            print(f"  ❌ Removed columns: {', '.join(removed_cols)}")
        if added_cols:
            print(f"  ➕ Added columns: {', '.join(added_cols)}")
        if not removed_cols and not added_cols:
            print(f"  ✓ No column changes")
    
    def phase6_entity_id_analysis(self):
        """Phase 6: Analyze assessed_biomarker_entity_id patterns"""
        print("\n" + "=" * 80)
        print("PHASE 6: ENTITY ID FORMAT ANALYSIS")
        print("=" * 80)
        
        # Check entity ID formats in processed files
        print("\n🔍 Checking GlyTouCan AC vs Entity ID patterns:")
        
        for version, key in [('v2.6', 'v26_processed'), ('v2.9', 'v29_processed')]:
            df = self.data[key]
            print(f"\n  {version} Processed File:")
            
            if 'glytoucan_ac' in df.columns:
                has_glytoucan = df['glytoucan_ac'].notna().sum()
                print(f"    Records with GlyTouCan AC: {has_glytoucan}/{len(df)}")
            
            if 'assessed_biomarker_entity_id' in df.columns:
                entity_ids = df['assessed_biomarker_entity_id'].dropna()
                print(f"    Entity ID patterns (top 5):")
                
                # Analyze ID prefixes
                prefixes = entity_ids.str.split(':').str[0].value_counts()
                for prefix, count in prefixes.head(5).items():
                    print(f"      {prefix}: {count}")
    
    def generate_summary_report(self):
        """Generate final summary report"""
        print("\n" + "=" * 80)
        print("SUMMARY REPORT")
        print("=" * 80)
        
        missing_count = len(self.results.get('missing_ids', set()))
        
        print(f"\n🎯 KEY FINDINGS:")
        print(f"  • {missing_count} glycan biomarkers were lost between v2.6 and v2.9")
        
        # Determine likely causes
        print(f"\n💡 LIKELY CAUSES (check these):")
        
        counts = self.results.get('counts', {})
        glycan_id = self.results.get('glycan_identification', {})
        
        # Check if source data changed
        if 'v26_source_total' in counts and 'v29_source_total' in counts:
            source_diff = counts['v29_source_total'] - counts['v26_source_total']
            if source_diff < 0:
                print(f"  ⚠️  Source data decreased by {abs(source_diff)} records")
        
        # Check glycan counts in source
        if 'v26_source_glycans' in glycan_id and 'v29_source_glycans' in glycan_id:
            glycan_source_diff = glycan_id['v29_source_glycans'] - glycan_id['v26_source_glycans']
            if glycan_source_diff < 0:
                print(f"  ⚠️  Glycan records in YOUR source decreased by {abs(glycan_source_diff)}")
                print(f"      → Check if glycan biomarkers were accidentally removed from v2.9 source")
        
        print(f"\n📝 RECOMMENDED NEXT STEPS:")
        print(f"  1. Review the detailed analysis above")
        print(f"  2. Check missing biomarker samples for patterns")
        print(f"  3. Verify v2.9 source data completeness")
        print(f"  4. Contact GlyGen team if their filtering logic changed")
        print(f"  5. Review any data cleaning/transformation scripts")
    
    def save_detailed_report(self, output_file='investigation_report.txt'):
        """Save missing IDs to file for further analysis"""
        missing_ids = self.results.get('missing_ids', set())
        remaining_ids = self.results.get('remaining_ids', set())
        new_ids = self.results.get('new_ids', set())
        
        output_path = self.base_path / output_file
        with open(output_path, 'w') as f:
            f.write("BIOMARKER INVESTIGATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Missing Biomarker IDs ({len(missing_ids)}):\n")
            f.write("-" * 80 + "\n")
            for bio_id in sorted(missing_ids):
                f.write(f"{bio_id}\n")
            
            f.write(f"\nRemaining Biomarker IDs ({len(remaining_ids)}):\n")
            f.write("-" * 80 + "\n")
            for bio_id in sorted(remaining_ids):
                f.write(f"{bio_id}\n")
            
            f.write(f"\nNew Biomarker IDs ({len(new_ids)}):\n")
            f.write("-" * 80 + "\n")
            for bio_id in sorted(new_ids):
                f.write(f"{bio_id}\n")
        
        print(f"\n✓ Detailed report saved to: {output_path}")
    
    def run_full_investigation(self):
        """Run all phases of the investigation"""
        print("\n" + "=" * 80)
        print("BIOMARKER INVESTIGATION - v2.6 to v2.9")
        print("=" * 80)
        
        # Load files
        if not self.load_files():
            return False
        
        # Run all phases
        self.phase1_record_counts()
        self.phase2_identify_glycans_in_source()
        self.phase3_trace_missing_biomarkers()
        self.phase4_deep_dive_missing_records(sample_size=10)
        self.phase5_column_comparison()
        self.phase6_entity_id_analysis()
        self.generate_summary_report()
        self.save_detailed_report()
        
        return True


def main():
    """Main entry point"""
    # Check if files exist in current directory
    investigator = BiomarkerInvestigator(".")
    
    success = investigator.run_full_investigation()
    
    if success:
        print("\n" + "=" * 80)
        print("Investigation complete! ✓")
        print("=" * 80)
    else:
        print("\n❌ Investigation failed. Please check file paths.")
        sys.exit(1)


if __name__ == "__main__":
    main()
