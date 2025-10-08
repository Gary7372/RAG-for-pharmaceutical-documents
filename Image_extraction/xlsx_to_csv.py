import os
import pandas as pd

# --- CONFIGURATION ---
root_folder = "results"               # Folder to search recursively
output_folder = "csv_files"        # Folder to save renamed CSVs

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# --- Function to clean and convert Excel to CSV ---
def clean_and_convert_excel(file_path, output_csv_path):
    try:
        # Try reading multi-row header
        df = pd.read_excel(file_path, header=[0, 1])
        df.columns = [' - '.join([str(i).strip() for i in col if str(i) != 'nan'])
                      .replace('_x000D_', ' ').replace('\r', ' ').replace('\n', ' ').strip()
                      for col in df.columns]
    except:
        # Fallback to single-row header
        df = pd.read_excel(file_path, header=0)
        df.columns = [str(col).replace('_x000D_', ' ').replace('\r', ' ').replace('\n', ' ').strip()
                      for col in df.columns]

    # Clean cell contents
    df = df.applymap(lambda x: str(x).replace('_x000D_', ' ').replace('\r', ' ').replace('\n', ' ').strip()
                     if isinstance(x, str) else x)

    # Save as CSV
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Saved: {output_csv_path}")

# --- Process all Excel files and save as csv1.csv, csv2.csv, ... ---
counter = 1

for dirpath, _, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.lower().endswith(".xlsx") and not filename.startswith("~$"):  # Skip temp files
            file_path = os.path.join(dirpath, filename)
            output_csv_name = f"csv{counter}.csv"
            output_csv_path = os.path.join(output_folder, output_csv_name)

            clean_and_convert_excel(file_path, output_csv_path)
            counter += 1
