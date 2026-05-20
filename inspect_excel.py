
import pandas as pd

try:
    df = pd.read_excel('CP handles(1-468).xlsx')
    with open('columns_info.txt', 'w', encoding='utf-8') as f:
        f.write("Columns found:\n")
        for i, col in enumerate(df.columns):
            f.write(f"{i}: {col}\n")
        
        f.write("\nFirst row sample:\n")
        row = df.iloc[0]
        for col in df.columns:
            f.write(f"{col}: {row[col]}\n")
            
except Exception as e:
    with open('columns_info.txt', 'w') as f:
        f.write(f"Error: {e}")
