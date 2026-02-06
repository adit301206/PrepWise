import pandas as pd

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'

try:
    df = pd.read_excel(file_path, header=None, nrows=20)
    
    header_row_index = -1
    
    print("Scanning for header row...")
    for index, row in df.iterrows():
        # Convert row to string check
        row_str = str(row.values).lower()
        if "question" in row_str or "sr no" in row_str or "unit no" in row_str:
            print(f"FOUND HEADER CANDIDATE AT INDEX {index}:")
            print(row.values)
            header_row_index = index
            
    if header_row_index != -1:
        print(f"\nVerifying data structure using header row {header_row_index}...")
        df_final = pd.read_excel(file_path, header=header_row_index)
        print("Columns found:", df_final.columns.tolist())
        print("First data row:")
        print(df_final.iloc[0].values)
    else:
        print("Could not find header row with keywords.")

except Exception as e:
    print(f"Error: {e}")
