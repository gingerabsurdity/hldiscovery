import os
import csv

def merge_matching_files(directories, output_dir):
    """
    Merges matching CSV files from multiple directories where file names match the first three letters.
    The rows from each file are combined side-by-side, aligning rows based on their index.

    Args:
        directories (list of str): List of directory paths to search for CSV files.
        output_dir (str): Path to the output directory where merged files are saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create output directory if it doesn't exist

    # Dictionary to hold file paths grouped by their prefixes
    files_by_prefix = {}

    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                prefix = filename[:3]  # Extract the first three characters
                if prefix not in files_by_prefix:
                    files_by_prefix[prefix] = []
                files_by_prefix[prefix].append(os.path.join(directory, filename))

    # Merge files with the same prefix
    for prefix, file_paths in files_by_prefix.items():
        if len(file_paths) > 2:  # Only merge if there is more than one file with the same prefix
            output_file = os.path.join(output_dir, f'{prefix}.csv')

            with open(output_file, 'w', newline='') as out:
                writer = csv.writer(out)

                # Open all files and merge them side-by-side
                readers = [csv.reader(open(file_path, 'r')) for file_path in file_paths]

                # Write merged rows
                while True:
                    rows = [next(reader, None) for reader in readers]
                    if all(row is None for row in rows):
                        break  # Exit loop if all readers are exhausted

                    merged_row = []
                    for row in rows:
                        if row is not None:
                            merged_row.extend(row)
                        else:
                            merged_row.extend([''] * len(next(readers[0], [])))  # Pad with empty cells if a file ends early

                    writer.writerow(merged_row)

            print(f'Merged file created: {output_file}')

# Example usage
directories = [
    'data//02_Location',  # Replace with the path to the first directory
    'data//03_Activity',  # Replace with the path to the second directory
    'data//06_Sub-Process'     # Replace with additional directories as needed
]
output_dir = 'data//merged'  # Replace with the path to the output directory

merge_matching_files(directories, output_dir)
