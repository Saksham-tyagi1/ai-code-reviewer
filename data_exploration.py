import json
import pandas as pd

# Load the dataset
file_path = "src/data/buggy_dataset/train_finetune.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Display basic info
print("Dataset Structure:")
print(df.info())

# Display first few rows
print("\nSample Data:")
print(df.head())

# Check for missing values
missing_values = df.isnull().sum()
print("\nMissing Values:")
print(missing_values[missing_values > 0])

# Count occurrences of different instruction types
if "instruction" in df.columns:
    print("\nInstruction Type Distribution:")
    print(df["instruction"].value_counts())

# Check lengths of code snippets (if applicable)
if "buggy_code" in df.columns:
    df["buggy_code_length"] = df["buggy_code"].apply(lambda x: len(x.split("\n")))
    print("\nBuggy Code Length Statistics:")
    print(df["buggy_code_length"].describe())

if "response" in df.columns:
    df["response_length"] = df["response"].apply(lambda x: len(x.split("\n")))
    print("\nResponse Code Length Statistics:")
    print(df["response_length"].describe())
