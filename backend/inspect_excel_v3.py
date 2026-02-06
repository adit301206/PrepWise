import pandas as pd

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'

try:
    # Read first 20 rows with no header
    df = pd.read_excel(file_path, header=None, nrows=20)
    
    print("Searching for potential headers...")
    for index, row in df.iterrows():
        # Clean row data for display: remove NaNs and strip strings
        clean_row = [str(x).strip() for x in row.values if pd.notna(x)]
        if clean_row:
            print(f"Row {index}: {clean_row}")

except Exception as e:
    print(f"Error reading excel: {e}")
