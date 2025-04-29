import pandas as pd
import os

def delete_columns_and_zero_rows_from_csv(input_csv, columns_to_delete, output_folder):
    """
    Deletes specified columns from a CSV file and removes rows consisting entirely of zeros.
    Saves the modified version in the specified output directory.

    Args:
        input_csv (str): Path to the input CSV file.
        columns_to_delete (list): List of column names to delete.
        output_folder (str): Path to the folder where modified CSV files will be saved.

    Returns:
        str: Path to the modified CSV file.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Remove specified columns
    df = df.drop(columns=[col for col in columns_to_delete if col in df.columns])

    # Remove rows where all remaining values are 0
    df = df.loc[~(df.select_dtypes(include=[int, float]).fillna(0).eq(0).all(axis=1))]

    # Generate a new filename for the modified CSV
    base_name = os.path.basename(input_csv)
    modified_csv = os.path.join(output_folder, f"{base_name}")

    # Save the modified DataFrame to the new file
    df.to_csv(modified_csv, index=False)
    print(f"Processed: {input_csv} -> {modified_csv}")

    return modified_csv

def process_folder(input_folder, output_folder, columns_to_delete):
    """
    Processes all CSV files in a given folder by removing specified columns and rows consisting entirely of zeros.

    Args:
        input_folder (str): Path to the folder containing input CSV files.
        output_folder (str): Path to the folder where modified CSV files will be saved.
        columns_to_delete (list): List of column names to delete.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            input_csv = os.path.join(input_folder, file_name)
            delete_columns_and_zero_rows_from_csv(input_csv, columns_to_delete, output_folder)

# Example usage
if __name__ == "__main__":
    input_folder = "data/merged"  # Path to the input folder containing CSV files
    output_folder = "data/merged_clean"  # Path to the output folder

    # columns_to_delete = [
    # "ANOTHER SUB-PROCESS", "SUB-PROCESS UNKNOWN", "Remove cardboard box/item from the cart",
    # "Move to next position", "Placing items on a rack", "Retrieval of items", "Move to a cart", 
    # "Place cardboard box/item in a cart", "Place cardboard box/item on a table", "Open cardboard box",
    # "Disposal of filling material or shipping label", "Sorting", "Fill cardboard box with filling material",
    # "Print shipping label and return slip", "Prepare/add return label", "Attach shipping label",
    # "Remove elastic band", "Seal cardboard box", "Place cardboard box/item in a cart", "Place cardboard box/item in a cart.1"
    # "Tie elastic band around cardboard", "Retrieval", "Storage", "ANOTHER MAIN-PROCESS",
    # "MAIN-PROCESS UNKNOWN", "ANOTHER LOCATION", "LOCATION UNKNOWN", "Synchronization",
    # "ANOTHER ACTIVITY", "ACTIVITY UNKNOWN"
    # ]

    columns_to_delete =[
        "ANOTHER LOCATION","LOCATION UNKNOWN","ANOTHER ACTIVITY","ACTIVITY UNKNOWN","Cross aisle path","Aisle path","Synchronization","ANOTHER SUB-PROCESS",
         "SUB-PROCESS UNKNOWN", "Remove cardboard box/item from the cart", "Move to next position", "Placing items on a rack", "Retrieval of items", 
         "Move to a cart", "Place cardboard box/item in a cart", "Place cardboard box/item on a table", "Open cardboard box", 
         "Disposal of filling material or shipping label", "Sorting", "Fill cardboard box with filling material", "Print shipping label and return slip",
          "Prepare/add return label", "Attach shipping label", "Remove elastic band", "Seal cardboard box", "Place cardboard box/item in a cart",
           "Tie elastic band around cardboard", "Path"
    ]

    # Collecting order and hardware,Collecting cart,Collecting empty cardboard boxes,
    #Collecting packed cardboard boxes,Transport a cart to the base,Picking,Transport to the packing/sorting area,
    #Unpacking,Packing,Storing,Handing over packed cardboard boxes,Returning empty cardboard boxes,Returning cart,
    #Returning hardware,Waiting,Report and clarify the incident,Transition,Place cardboard box/item in a cart.1,Office,Cart area,
    #Cardboard box area,Base,Packing/sorting area,Issuing/receiving area,Path,Cross aisle path,Aisle path,Tick off / confirm,Scan,Pull,
    #Push,Handling upwards,Handling centred,Handling downwards,Walking,Standing,Sitting

    # Office,Cart area,Cardboard box area,Base,Packing/sorting area,Issuing/receiving area,
    # Path,Cross aisle path,Aisle path,Path (Office),Path (Cardboard box area),Path (Cart area),Path (Issuing area),1-2,2-3,3-4,4-5,1,2,3,4,5,
    # front,back,ANOTHER LOCATION,LOCATION UNKNOWN,Synchronization,Tick off / confirm,Scan,Pull,Push,Handling upwards,Handling centred,
    # Handling downwards,Walking,Standing,Sitting,ANOTHER ACTIVITY,ACTIVITY UNKNOWN,Collecting order and hardware,Collecting cart,
    # Collecting empty cardboard boxes,Collecting packed cardboard boxes,Transport a cart to the base,Picking,Transport to the packing/sorting area,
    # Unpacking,Packing,Storing,Handing over packed cardboard boxes,Returning empty cardboard boxes,Returning cart,Returning hardware,Waiting,
    # Report and clarify the incident,Transition,ANOTHER SUB-PROCESS,SUB-PROCESS UNKNOWN,Remove cardboard box/item from the cart,
    # Move to next position,Placing items on a rack,Retrieval of items,Move to a cart,Place cardboard box/item in a cart,
    # Place cardboard box/item on a table,Open cardboard box,Disposal of filling material or shipping label,Sorting,
    # Fill cardboard box with filling material,Print shipping label and return slip,Prepare/add return label,
    # Attach shipping label,Remove elastic band,Seal cardboard box,Place cardboard box/item in a cart,Tie elastic band around cardboard





    process_folder(input_folder, output_folder, columns_to_delete)


# Collecting order and hardware,Collecting cart,Collecting empty cardboard boxes,Collecting packed cardboard boxes,Transport a cart to the base,Picking,
# Transport to the packing/sorting area,Unpacking,Packing,Storing,Handing over packed cardboard boxes,Returning empty cardboard boxes,Returning cart,
# Returning hardware,Waiting,Report and clarify the incident,Transition,ANOTHER SUB-PROCESS,SUB-PROCESS UNKNOWN,Remove cardboard box/item from the cart,
# Move to next position,Placing items on a rack,Retrieval of items,Move to a cart,Place cardboard box/item in a cart,Place cardboard box/item on a table,
# Open cardboard box,Disposal of filling material or shipping label,Sorting,Fill cardboard box with filling material,Print shipping label and return slip,
# Prepare/add return label,Attach shipping label,Remove elastic band,Seal cardboard box,Place cardboard box/item in a cart,Tie elastic band around cardboard,
# Retrieval,Storage,ANOTHER MAIN-PROCESS,MAIN-PROCESS UNKNOWN,Office,Cart area,Cardboard box area,Base,Packing/sorting area,Issuing/receiving area,Path,
# Cross aisle path,Aisle path,ANOTHER LOCATION,LOCATION UNKNOWN,Synchronization,
# Tick off / confirm,Scan,Pull,Push,Handling upwards,Handling centred,Handling downwards,Walking,Standing,Sitting,ANOTHER ACTIVITY,ACTIVITY UNKNOWN

# Office,Cart area,Cardboard box area,Base,Packing/sorting area,Issuing/receiving area,
# Path,Cross aisle path,Aisle path,Path (Office),Path (Cardboard box area),Path (Cart area),Path (Issuing area),1-2,2-3,3-4,4-5,1,2,3,4,5,
# front,back,ANOTHER LOCATION,LOCATION UNKNOWN,Synchronization,Tick off / confirm,Scan,Pull,Push,Handling upwards,Handling centred,Handling downwards,
# Walking,Standing,Sitting,ANOTHER ACTIVITY,ACTIVITY UNKNOWN,Collecting order and hardware,Collecting cart,Collecting empty cardboard boxes,
# Collecting packed cardboard boxes,Transport a cart to the base,Picking,Transport to the packing/sorting area,Unpacking,
# Packing,Storing,Handing over packed cardboard boxes,Returning empty cardboard boxes,Returning cart,Returning hardware,
# Waiting,Report and clarify the incident,Transition,ANOTHER SUB-PROCESS,SUB-PROCESS UNKNOWN,Remove cardboard box/item from the cart,
# Move to next position,Placing items on a rack,Retrieval of items,Move to a cart,Place cardboard box/item in a cart,Place cardboard box/item on a table,
# Open cardboard box,Disposal of filling material or shipping label,Sorting,Fill cardboard box with filling material,Print shipping label and return slip,
# Prepare/add return label,Attach shipping label,Remove elastic band,Seal cardboard box,Place cardboard box/item in a cart,Tie elastic band around cardboard
