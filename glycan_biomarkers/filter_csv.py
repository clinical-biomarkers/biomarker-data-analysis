#!/usr/bin/env python3
"""
Filter TSV file by removing rows where a column value appears in another TSV file.

Usage:
    python filter_tsv.py file1.tsv file2.tsv column_name output.tsv
"""

import sys
import csv


def filter_tsv(file1_path, file2_path, column_name, output_path):
    """
    Remove rows from file1 where column_name value exists in file2's column_name.
    
    Args:
        file1_path: Path to first CSV file (to be filtered)
        file2_path: Path to second CSV file (reference for values to remove)
        column_name: Name of the column to compare
        output_path: Path for the filtered output file
    """
    
    # Read file2 and collect all values from the specified column
    excluded_values = set()
    
    with open(file2_path, 'r', encoding='utf-8') as f2:
        reader = csv.DictReader(f2, delimiter=',')
        
        if column_name not in reader.fieldnames:
            raise ValueError(f"Column '{column_name}' not found in {file2_path}")
        
        for row in reader:
            excluded_values.add(row[column_name])
    
    print(f"Found {len(excluded_values)} unique values to exclude from column '{column_name}'")
    
    # Read file1, filter rows, and write to output
    rows_read = 0
    rows_written = 0
    
    with open(file1_path, 'r', encoding='utf-8') as f1, \
         open(output_path, 'w', encoding='utf-8', newline='') as out:
        
        reader = csv.DictReader(f1, delimiter=',')
        
        if column_name not in reader.fieldnames:
            raise ValueError(f"Column '{column_name}' not found in {file1_path}")
        
        writer = csv.DictWriter(out, fieldnames=reader.fieldnames, delimiter='\t')
        writer.writeheader()
        
        for row in reader:
            rows_read += 1
            if row[column_name] not in excluded_values:
                writer.writerow(row)
                rows_written += 1
    
    rows_excluded = rows_read - rows_written
    print(f"\nProcessed {rows_read} rows from {file1_path}")
    print(f"Excluded {rows_excluded} rows")
    print(f"Written {rows_written} rows to {output_path}")


def main():
    if len(sys.argv) != 5:
        print("Usage: python filter_tsv.py <file1.tsv> <file2.tsv> <column_name> <output.tsv>")
        print("\nExample:")
        print("  python filter_tsv.py data.tsv exclude.tsv user_id filtered_data.tsv")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    column_name = sys.argv[3]
    output_path = sys.argv[4]
    
    try:
        filter_tsv(file1_path, file2_path, column_name, output_path)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
