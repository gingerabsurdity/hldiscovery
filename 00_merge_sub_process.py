import os
import pandas as pd

# Paths to your folders
folders = ['data/06_Sub-Process_filtered/S01', 'data/06_Sub-Process_filtered/S03', 'data/06_Sub-Process_filtered/S04', 'data/06_Sub-Process_filtered/S07']
output_dir = 'data/06_Sub-Process_filtered/merged'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get the list of unique file names across all folders
all_files = set()
for folder in folders:
    all_files.update(os.listdir(folder))

# Filter for CSV files
csv_files = [f for f in all_files if f.endswith('.csv')]

# Process each CSV file
for file_name in csv_files:
    combined_data = pd.DataFrame()
    all_columns = set()  # To track all unique columns across files

    # Step 1: Collect all columns from all files
    for folder in folders:
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, nrows=1)  # Read only the header
            all_columns.update(data.columns)

    # Ensure consistent column ordering
    all_columns = sorted(all_columns)  # Sorted for consistent order

    # Step 2: Merge data from all files
    for folder in folders:
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            # Read the data and ensure all columns exist
            data = pd.read_csv(file_path)
            data = data.reindex(columns=all_columns, fill_value=0)  # Fill missing columns with 0
            combined_data = pd.concat([combined_data, data], ignore_index=True)

    # Step 3: Convert numeric columns to integers
    for col in all_columns:
        if combined_data[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            combined_data[col] = combined_data[col].fillna(0).astype(int)

    # Save the merged file to the output directory
    output_file_path = os.path.join(output_dir, file_name)
    combined_data.to_csv(output_file_path, index=False)
    print(f"Merged {file_name} saved to {output_file_path}")