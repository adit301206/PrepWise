import pandas as pd

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'

try:
    # Read first 10 rows with no header to see structure
    df = pd.read_excel(file_path, header=None, nrows=10)
    print("First 10 rows raw:")
    print(df.to_string())
except Exception as e:
    print(f"Error reading excel: {e}")
