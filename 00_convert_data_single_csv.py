import pandas as pd
from datetime import timedelta
import pm4py

def csv_to_xes(csv_file_path, output_xes_path):
    """
    Convert a single CSV file to an XES file.

    Args:
        csv_file_path (str): Path to the input CSV file.
        output_xes_path (str): Path to save the output XES file.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Combine columns with a value of 1 into a single activity name
    df['concept:name'] = df.apply(lambda row: ', '.join(row[row == 1].index), axis=1)

    # Add a case ID column
    df['case:concept:name'] = 'Case_1'  # Assuming a single case for simplicity

    # Add a timestamp column with sequential increments
    start_time = pd.Timestamp('2023-01-01 00:00:00')
    df['time:timestamp'] = [start_time + timedelta(seconds=0.5 * i) for i in range(len(df))]

    # Remove consecutive duplicate activities
    df = df[df['concept:name'].shift(periods=1) != df['concept:name']].dropna()

    # Format the dataframe for XES
    event_log = pm4py.format_dataframe(df, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')

    # Write to XES format
    pm4py.write_xes(event_log, output_xes_path)

# Example usage
if __name__ == "__main__":
    input_csv = 'data//06_Sub-Process//S01_Sub-Process_onlypacking_modified.csv'  # Replace with your CSV file path
    output_xes = 'preprocessed_data//06_Sub-Process//01_Sub-Process_onlypacking.xes'  # Replace with desired output XES file path
    csv_to_xes(input_csv, output_xes)
