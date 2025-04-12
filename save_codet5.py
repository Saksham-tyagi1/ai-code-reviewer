import os
import shutil
from transformers import T5ForConditionalGeneration, RobertaTokenizer

# Define paths
best_checkpoint = "codet5_finetuned/checkpoint-1056"  # Update with the best/latest checkpoint
final_model_path = "codet5_finetuned_final"

# Option 1: Create a symbolic link (fastest, saves space)
if not os.path.exists(final_model_path):
    os.symlink(best_checkpoint, final_model_path)
    print(f"✅ Created a symlink: {final_model_path} → {best_checkpoint}")
else:
    print(f"⚠️ Symlink already exists: {final_model_path}")

# Option 2: If you want an actual copy (useful for portability)
if not os.path.exists(final_model_path):
    shutil.copytree(best_checkpoint, final_model_path)
    print(f"✅ Copied best checkpoint to: {final_model_path}")

# Load model & tokenizer to confirm everything is working
model = T5ForConditionalGeneration.from_pretrained(final_model_path)
tokenizer = RobertaTokenizer.from_pretrained(final_model_path)

print("✅ Fine-tuned model is ready for use!")
