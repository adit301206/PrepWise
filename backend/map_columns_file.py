import pandas as pd
import sys

# Set encoding to utf-8 for output
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'
output_file = r'e:\PrepWise\backend\excel_map.txt'

try:
    df = pd.read_excel(file_path, header=None)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Check a few rows to be sure
        for row_idx in [18, 19, 20]:
            if len(df) > row_idx:
                row = df.iloc[row_idx].values
                f.write(f"--- ROW {row_idx} ---\n")
                for i, val in enumerate(row):
                    clean_val = str(val).strip().replace('\n', ' ')
                    f.write(f"Col {i}: {clean_val}\n")
                f.write("\n")

    print(f"Output written to {output_file}")

except Exception as e:
    print(f"Error: {e}")
