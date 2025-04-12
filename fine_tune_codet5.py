import os
import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset

# Set environment variables to prevent memory crashes
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"  # Prevent system crashes
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU if necessary

# Define model name and dataset paths
model_name = "Salesforce/codet5-small"
train_data_path = "src/data/buggy_dataset/preprocessed_train_finetune.csv"
valid_data_path = "src/data/buggy_dataset/preprocessed_valid_finetune.csv"

# Load tokenizer
tokenizer = RobertaTokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Move model to CPU (or GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)

# Load dataset
dataset = load_dataset("csv", data_files={"train": train_data_path, "validation": valid_data_path})


train_size = int(0.2 * len(dataset["train"]))
valid_size = int(0.2 * len(dataset["validation"]))
dataset["train"] = dataset["train"].shuffle(seed=42).select(range(train_size))
dataset["validation"] = dataset["validation"].shuffle(seed=42).select(range(valid_size))

# Tokenize function
def tokenize_function(examples):
    inputs = ["Fix the following code:\n" + code for code in examples["clean_instruction"]]
    targets = [fix for fix in examples["response"]]
    
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")
    labels = tokenizer(targets, max_length=512, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Tokenize dataset
tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["instruction", "response", "clean_instruction", "error_type", "response_length"])

# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Training arguments with smaller batch size and gradient accumulation
training_args = TrainingArguments(
    output_dir="./codet5_finetuned",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    per_device_train_batch_size=1,  # Reduce batch size to avoid memory issues
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,  # Accumulate gradients to mimic a larger batch
    save_total_limit=3,
    num_train_epochs=3,
    fp16=True if torch.cuda.is_available() else False,  # Enable mixed precision for GPU
    load_best_model_at_end=True,
    report_to="none",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train
trainer.train()