import pickle
import json
import os
import pandas as pd  # Add this import

def load_pickle(file_path):
    """Loads the pickle file."""
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data

def save_json(data, output_path):
    """Saves the data as a JSON file."""
    # Ensure that the directory exists before creating the file
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it doesn't exist
    
    # Convert DataFrame to JSON-serializable format
    if isinstance(data, pd.DataFrame):
        data = data.to_dict(orient="records")  # Convert DataFrame to list of records
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

def process_pickle_to_json(pickle_file_path, json_file_path):
    """Loads pickle file, processes, and saves as JSON."""
    print(f"🔄 Loading pickle file: {pickle_file_path}")
    data = load_pickle(pickle_file_path)
    print(f"✅ Pickle file loaded! Entries: {len(data)}")
    
    print(f"💾 Saving data to JSON: {json_file_path}")
    save_json(data, json_file_path)
    print("✅ Data saved as JSON!")

# Paths to the pickle files and output JSON files
pickle_file_path_train = "/Users/sakshamtyagi/ai_code_reviewer/src/data/buggy_dataset/bugfixes_train.pickle"
pickle_file_path_valid = "/Users/sakshamtyagi/ai_code_reviewer/src/data/buggy_dataset/bugfixes_valid.pickle"

json_file_path_train = "/Users/sakshamtyagi/ai_code_reviewer/src/data/buggy_dataset/bugfixes_train.json"
json_file_path_valid = "/Users/sakshamtyagi/ai_code_reviewer/src/data/buggy_dataset/bugfixes_valid.json"

# Process the pickle files to JSON
process_pickle_to_json(pickle_file_path_train, json_file_path_train)
process_pickle_to_json(pickle_file_path_valid, json_file_path_valid)
