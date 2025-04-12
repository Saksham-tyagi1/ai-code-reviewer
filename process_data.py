import pandas as pd
import re

# File paths
train_finetune_path = "src/data/buggy_dataset/train_finetune.json"
valid_finetune_path = "src/data/buggy_dataset/valid_finetune.json"

# Load data
train_df = pd.read_json(train_finetune_path)
valid_df = pd.read_json(valid_finetune_path)

# Function to clean "instruction" column
def clean_instruction(text):
    """Removes headers and extracts relevant traceback/error messages."""
    text = re.sub(r"### Buggy Code:\n?", "", text)  # Remove "### Buggy Code:"
    text = re.sub(r"### Traceback:\n?", "", text)   # Remove "### Traceback:"
    text = re.sub(r"### Bug Description:\n?", "", text)  # Remove "### Bug Description:"
    text = re.sub(r"### Fix:\n?", "", text)  # Remove "### Fix:"
    return text.strip()

# Function to extract Python error types (e.g., TypeError, KeyError, etc.)
def extract_error_type(text):
    match = re.search(r"(\w+Error):", text)
    return match.group(1) if match else "UnknownError"

# Apply transformations
for df in [train_df, valid_df]:
    df["clean_instruction"] = df["instruction"].apply(clean_instruction)
    df["error_type"] = df["instruction"].apply(extract_error_type)
    df["response_length"] = df["response"].apply(lambda x: len(str(x)))  # Measure response length

# Save preprocessed data
train_output_file = "src/data/buggy_dataset/preprocessed_train_finetune.csv"
valid_output_file = "src/data/buggy_dataset/preprocessed_valid_finetune.csv"

train_df.to_csv(train_output_file, index=False)
valid_df.to_csv(valid_output_file, index=False)

print(f"Preprocessing complete! Train data saved to {train_output_file}")
print(f"Preprocessing complete! Validation data saved to {valid_output_file}")

# --- Basic Analysis ---
print("\n🔹 Missing Values:")
print(train_df.isnull().sum())

print("\n🔹 Most Common Error Types in Training Data:")
print(train_df["error_type"].value_counts().head(10))

print("\n🔹 Response Length Statistics:")
print(train_df["response_length"].describe())

# Check for duplicate responses
duplicate_responses = train_df.duplicated(subset=["response"]).sum()
print(f"\n🔹 Duplicate Responses: {duplicate_responses} (out of {len(train_df)})")

