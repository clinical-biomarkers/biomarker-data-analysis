import pandas as pd

# Read both TSV files
df1 = pd.read_csv('biomarker2.9_processed.csv', sep=',')
df2 = pd.read_csv('biomarker2.6_processed.csv', sep=',')

# Method 1: Remove rows from df1 that exist in df2 (based on all columns)
result = df1[~df1.isin(df2.to_dict('list')).all(axis=1)]
"""
# Method 2: Using merge with indicator (more explicit)
result = df1.merge(df2, how='outer', indicator=True)
result = result[result['_merge'] == 'left_only'].drop('_merge', axis=1)

# Method 3: If you have specific key columns to match on
key_columns = ['col1', 'col2']  # specify your key columns
result = df1[~df1[key_columns].apply(tuple, axis=1).isin(
    df2[key_columns].apply(tuple, axis=1)
)]
"""
# Save the result
result.to_csv('result_processed_9-6.csv', sep=',', index=False)
