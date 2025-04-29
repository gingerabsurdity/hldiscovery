import pandas as pd
from datetime import timedelta
import pm4py
import os

# Input and output directories
dirname = 'data//06_Sub-Process_filtered//S07'
output_dirname = 'preprocessed_data//S07//'

# Ensure the output directory exists
os.makedirs(output_dirname, exist_ok=True)

# Define filtering list
merge_list = ["Path"]  

# Define first and second merge lists
first_merge_list = [                "Tick off / confirm",
            "Scan",
            "Pull",
            "Push",
            "Handling upwards",
            "Handling centred",
            "Handling downwards",
            "Walking",
            "Standing",
            "Sitting",]  
second_merge_list = [ "Office",
            "Cart area",
            "Cardboard box area",
            "Base",
            "Packing/sorting area",
            "Issuing/receiving area","Path (Office)",
            "Path (Cardboard box area)",
            "Path (Cart area)",
            "Path (Issuing area)",
            "1-2",
            "2-3",
            "3-4",
            "4-5",
            "1",
            "2",
            "3",
            "4",
            "5",
            "front",
            "back"] 

# Process all CSV files in the input directory
for i, filename in enumerate(os.listdir(dirname)):
    if filename.endswith('.csv'):
        file_path = os.path.join(dirname, filename)
        df = pd.read_csv(file_path)
        print(f"Processing: {filename[:filename.rfind('.')]}")
        
        merge_list = ["Path", "Place cardboard box/item in a cart.1", filename[:filename.rfind(".")]] 

        # Filter rows to exclude activities in the merge_list
        df = df[df.columns.difference(merge_list)]  # Exclude columns in merge_list

        # Now filter the rows where no value in the merge_list is present (if you want to filter based on values)
        df = df[~df.isin(merge_list).any(axis=1)]  # This excludes rows where any cell contains a value from merge_list

        # Transform the DataFrame for merging:
        # Apply first merge list and second merge list separately
        df['concept:name'] = df.apply(
            lambda row: ', '.join(
                [col for col in first_merge_list if row[col] == 1] +
                [col for col in second_merge_list if row[col] == 1]
            ), 
            axis=1
        )

        # Filter out rows where 'concept:name' does not contain a comma (no merging occurred)
        df = df[df['concept:name'].str.contains(',', na=False)]

        # Keep only the 'concept:name' column
        df = df[['concept:name']]

        # Assign case ID
        df['case:concept:name'] = f'Case_{i}'  # Assuming single case ID, can be customized

        # Add timestamp column
        start_time = pd.Timestamp('2023-01-01 00:00:00')
        df['time:timestamp'] = [start_time + timedelta(seconds=0.5 * j) for j in range(len(df))]

        # Ensure the rows are in the correct order
        df = df.sort_index()  # Explicitly sort by the original index to preserve order

        # Keep only the first occurrence of each activity
        df = df.where(df['concept:name'].shift(periods=1) != df['concept:name']).dropna()

        # Format DataFrame for PM4Py and write to XES
        event_log = pm4py.format_dataframe(df, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        xes_path = os.path.join(output_dirname, filename + '.xes')
        pm4py.write_xes(event_log, xes_path)
