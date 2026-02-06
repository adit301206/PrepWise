import pandas as pd

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'

try:
    # Read without header
    df = pd.read_excel(file_path, header=None)
    
    # Pick a row that definitely looked like data (e.g. index 19 from previous output)
    # The previous output showed "Row 19: ['17', '1', ...]", so let's check index 19.
    target_row_index = 19
    
    if len(df) > target_row_index:
        row = df.iloc[target_row_index].values
        print(f"--- MAPPING COLUMNS USING ROW {target_row_index} ---")
        for i, val in enumerate(row):
            print(f"Col {i}: {str(val).strip()}")
            
    else:
        print("File has fewer rows than expected.")

except Exception as e:
    print(f"Error: {e}")
