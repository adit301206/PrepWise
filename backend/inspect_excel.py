import pandas as pd
import os

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string())
except Exception as e:
    print(f"Error reading excel: {e}")
