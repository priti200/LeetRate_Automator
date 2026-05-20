
import pandas as pd

INPUT_CSV = 'final_leetcode_results.csv'
OUTPUT_CSV = 'final_leetcode_results_sorted.csv'

try:
    df = pd.read_csv(INPUT_CSV)
    print(f"Original rows: {len(df)}")
    
    # Deduplicate
    df = df.drop_duplicates(subset=['Student LeetCode Username'], keep='last')
    print(f"Deduplicated rows: {len(df)}")
    
    # Convert Rating to numeric, coercing errors to NaN
    # "Not Found/Error" will become NaN
    df['Rating_Numeric'] = pd.to_numeric(df['Fetched LeetCode Rating'], errors='coerce').fillna(0)
    
    # Sort
    df_sorted = df.sort_values(by='Rating_Numeric', ascending=False)
    
    # Drop helper column
    df_sorted = df_sorted.drop(columns=['Rating_Numeric'])
    
    # Save
    df_sorted.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved sorted data to {OUTPUT_CSV}")
    print("Top 5:")
    print(df_sorted[['Student Name', 'Fetched LeetCode Rating']].head(5).to_string())

except Exception as e:
    print(f"Error: {e}")
