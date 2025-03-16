import ast
import os
from transformers import pipeline
from prettytable import PrettyTable

# ✅ Load Local AI Model (TinyLlama-1.1B)
print("✅ Loading Local LLM Model... (This may take a few minutes)")
local_llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device="cpu", torch_dtype="auto")

# ✅ Define AST-based Code Analyzer
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.reported_issues = set()  # ✅ Prevent duplicate issues

    def visit_FunctionDef(self, node):
        """Detects large functions that may need refactoring."""
        issue = f"⚠️ Function '{node.name}' is too long ({len(node.body)} lines). Consider refactoring."
        if len(node.body) > 10 and issue not in self.reported_issues:
            self.issues.append((node.lineno, issue, node))
            self.reported_issues.add(issue)
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Detects hardcoded numeric values (magic numbers)."""
        issue = f"⚠️ Hardcoded large number {node.value}. Consider defining it as a constant variable."
        if isinstance(node.value, int) and node.value > 100 and issue not in self.reported_issues:
            self.issues.append((node.lineno, issue, node))
            self.reported_issues.add(issue)
        self.generic_visit(node)


# ✅ Analyze Python Code Using AST
def analyze_code(code):
    try:
        tree = ast.parse(code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return analyzer.issues
    except Exception as e:
        return [(0, f"❌ Error parsing code: {e}", None)]


# ✅ AI Fix System with Caching + Correct Formatting
ai_fix_cache = {}

def clean_ai_fix(ai_fix):
    """Ensures AI fixes are properly formatted as Python code blocks."""
    ai_fix = ai_fix.strip()

    # ✅ Extract only the valid Python code block
    if "```python" in ai_fix:
        ai_fix = ai_fix.split("```python")[-1]  # Keep only the last code block
    if "```" in ai_fix:
        ai_fix = ai_fix.split("```")[0]  # Remove trailing text

    return f"```python\n{ai_fix.strip()}\n```"

def get_ai_fix_local(code_snippet, issue_description):
    """Generates AI-powered fixes, ensuring structured output."""
    cache_key = (code_snippet, issue_description)

    if cache_key in ai_fix_cache:
        return ai_fix_cache[cache_key]  # Use cached result

    prompt = f"""
    You are a Python code reviewer. Improve the following code based on the detected issue.

    Issue: {issue_description}

    Code:
    {code_snippet}

    Please provide an improved version **inside a Python code block**, like this:
    
    ```python
    # Fixed Code
    def optimized_function():
        ...
    ```

    Do **not** include unnecessary explanations—only the corrected code.
    """

    result = local_llm(prompt, max_new_tokens=50, num_return_sequences=1, truncation=True, return_full_text=False)
    ai_fix = result[0]["generated_text"].strip()

    # ✅ Clean up AI-generated fix
    ai_fix = clean_ai_fix(ai_fix)

    ai_fix_cache[cache_key] = ai_fix
    return ai_fix


# ✅ Save AI Fixes to Markdown Report (Ensuring Clean Reports)
def initialize_report():
    """Clears previous reports before generating new ones."""
    with open("code_review_report.md", "w") as report:
        report.write("# 📋 AI Code Review Report\n\n")

def save_report(file_name, issues):
    """Saves AI-generated fixes to `code_review_report.md`, ensuring formatting correctness."""
    with open("code_review_report.md", "a") as report:
        report.write(f"### 📝 Code Review for {file_name}\n\n")

        if issues:
            seen_issues = set()  # ✅ Prevent duplicate reporting
            for line, issue, ai_fix in issues:
                if issue not in seen_issues:
                    seen_issues.add(issue)
                    report.write(f"- **Line {line}:** {issue}\n\n")
                    report.write(f"  - **Suggested Fix:**\n\n{ai_fix}\n\n")
        else:
            report.write("✅ No issues found.\n\n")


# ✅ Analyze All Python Files in the Directory
def analyze_directory(directory_path):
    """Scans all Python files in a directory and ensures they are reviewed."""
    if not os.path.exists(directory_path):
        print(f"❌ Error: Directory '{directory_path}' does not exist!")
        return

    python_files = [f for f in os.listdir(directory_path) if f.endswith(".py")]

    if not python_files:
        print("⚠️ No Python files found in the directory.")
        return

    for filename in python_files:
        file_path = os.path.join(directory_path, filename)
        print(f"\n🔍 Analyzing: {filename}")

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        issues = analyze_code(code)
        issue_list = []

        if issues:
            table = PrettyTable(["Line No.", "Issue Detected", "AI Suggested Fix"])
            for line, issue, node in issues:
                code_snippet = ast.get_source_segment(code, node) if node else "N/A"
                ai_fix = get_ai_fix_local(code_snippet, issue) if node else "N/A"
                table.add_row([line, issue, ai_fix])
                issue_list.append((line, issue, ai_fix))

            print("\n🚨 **Code Issues Detected & AI Fixes:**\n")
            print(table)

        # ✅ Save review for each file
        save_report(filename, issue_list)


# ✅ Run the Analysis on All Test Files
initialize_report()  # ✅ Ensure old reports are cleared before analyzing
analyze_directory("src/test_files")
