import os
import shutil

# Define the new project structure
PROJECT_STRUCTURE = {
    "src": [
        "analysis", 
        "llm", 
        "api", 
        "data"
    ],
    "models": [],
    "tests": [],
    "notebooks": []
}

# Define file migrations (existing -> new location)
FILE_MAPPINGS = {
    "src/analysis/ast_analyzer.py": "src/analysis/ast_analyzer.py",
    "src/analysis/ai_fixer.py": "src/llm/llm_fixer.py",
    "src/analysis/report_generator.py": "src/analysis/report_generator.py",
    "src/api/main.py": "src/api/main.py"
}

# Placeholder files to create if they don't exist
PLACEHOLDER_FILES = {
    "src/analysis/complexity.py": "# Detects function complexity\n",
    "src/analysis/dead_code.py": "# Finds unreachable code\n",
    "src/analysis/loop_optimizer.py": "# Detects inefficient loops\n",
    "src/llm/prompt_engine.py": "# Implements Chain-of-Thought prompting\n",
    "src/llm/fine_tune.py": "# Fine-tuning script for TinyLlama\n",
    "src/api/endpoints.py": "# API routes for code analysis & AI fixes\n",
    "src/data/github_fixes.json": "[]",
    "src/data/finetune_bug_fixes.json": "[]",
    "models/.gitkeep": "",
    "tests/.gitkeep": "",
    "notebooks/.gitkeep": "",
    ".gitignore": "models/\n*.json\n*.parquet\n__pycache__/\n",
    "README.md": "# AI Code Reviewer\n"
}

def create_directories():
    """Create required directories."""
    for folder, subfolders in PROJECT_STRUCTURE.items():
        os.makedirs(folder, exist_ok=True)
        for subfolder in subfolders:
            os.makedirs(os.path.join(folder, subfolder), exist_ok=True)
            # Add README placeholders for clarity
            with open(os.path.join(folder, subfolder, "README.md"), "w") as f:
                f.write(f"# {subfolder.capitalize()} Module\n")

def move_existing_files():
    """Move existing files to their new locations."""
    for old_path, new_path in FILE_MAPPINGS.items():
        if os.path.exists(old_path):
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(old_path, new_path)
            print(f"✅ Moved {old_path} → {new_path}")
        else:
            print(f"⚠️ Skipped {old_path} (not found)")

def create_placeholder_files():
    """Create empty placeholder files if they don't already exist."""
    for file_path, content in PLACEHOLDER_FILES.items():
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Created {file_path}")
        else:
            print(f"⚠️ Skipped {file_path} (already exists)")

if __name__ == "__main__":
    print("🔄 Migrating AI Code Reviewer project structure...")
    create_directories()
    move_existing_files()
    create_placeholder_files()
    print("✅ Migration complete! Your project is now structured properly.")
