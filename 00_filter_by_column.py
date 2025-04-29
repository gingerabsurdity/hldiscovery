import os
import csv

def filter_csv_by_columns(input_folder, output_folder, columns):
    """
    Filters rows in all CSV files in a folder where the value in specified columns is '1' and creates separate files for each column,
    with each input file having its own folder in the output directory.

    Args:
        input_folder (str): Path to the input folder containing CSV files.
        output_folder (str): Folder path to save the filtered CSV files.
        columns (list): List of column names to filter by.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create output folder if it doesn't exist

    for input_file in os.listdir(input_folder):
        if input_file.endswith('.csv'):
            input_file_path = os.path.join(input_folder, input_file)

            # Create a specific folder for each input file
            file_output_folder = os.path.join(output_folder, os.path.splitext(input_file)[0])
            if not os.path.exists(file_output_folder):
                os.makedirs(file_output_folder)

            with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                rows = list(reader)  # Read all rows at once
                # for row in rows:                    
                #     print(row)
                #print(rows)
                
                for column_name in columns:
                    filtered_rows = [row for row in rows if row.get(column_name) == '1']

                    #print(filtered_rows)

                    if not filtered_rows:
                        print(f"No rows with value '1' in the column '{column_name}' were found in file '{input_file}'.")
                        continue

                    output_file = os.path.join(file_output_folder, f"{column_name}.csv")

                    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
                        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
                        writer.writeheader()
                        writer.writerows(filtered_rows)
                        print(f"Filtered CSV for column '{column_name}' saved to {output_file}.")

# Usage
input_folder = 'data/merged_clean'  # Path to the input folder containing CSV files
output_folder = 'data/06_Sub-Process_filtered'  # Folder to save the filtered CSV files
columns = [
         "Collecting order and hardware",
            "Collecting cart",
            "Collecting empty cardboard boxes",
            "Collecting packed cardboard boxes",
            "Transport a cart to the base",
            "Picking",
            "Transport to the packing+sorting area",
            "Unpacking",
            "Packing",
            "Storing",
            "Handing over packed cardboard boxes",
            "Returning empty cardboard boxes",
            "Returning cart",
            "Returning hardware",
            "Waiting",
            "Report and clarify the incident",
            "Transition"
]  # Replace with the column names you want to filter

filter_csv_by_columns(input_folder, output_folder, columns)
