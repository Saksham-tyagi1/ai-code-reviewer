import ast
import os
from transformers import pipeline
from prettytable import PrettyTable

# ✅ Step 1: Load a Smaller, Faster LLM (TinyLlama-1.1B)
print("✅ Loading Local LLM Model... (This may take a few minutes)")
local_llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device="cpu", torch_dtype="auto")

# ✅ Step 2: Define AST-based Code Analyzer
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.imports = set()

    def visit_FunctionDef(self, node):
        """Detects large functions that may need refactoring."""
        if len(node.body) > 10:  # If function has more than 10 lines
            self.issues.append((node.lineno, f"Function '{node.name}' is too long ({len(node.body)} lines). Consider refactoring.", node))
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Detects hardcoded numeric values (magic numbers)."""
        if isinstance(node.value, int) and node.value > 100:
            self.issues.append((node.lineno, f"Hardcoded large number {node.value}. Consider defining it as a constant variable.", node))
        self.generic_visit(node)

    def visit_Import(self, node):
        """Tracks all imported modules."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        """Removes used imports from tracking to find unused ones later."""
        if node.id in self.imports:
            self.imports.remove(node.id)

    def report_unused_imports(self):
        """Returns a list of unused imports detected in the script."""
        return [(0, f"⚠️ Unused import detected: `{imp}`", None) for imp in self.imports]


# ✅ Step 3: Function to Analyze Python Code
def analyze_code(code):
    try:
        tree = ast.parse(code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        # Collect detected issues
        issues = analyzer.issues
        issues.extend(analyzer.report_unused_imports())  # Add unused import warnings
        return issues
    except Exception as e:
        return [(0, f"Error parsing code: {e}", None)]


# ✅ Step 4: AI Fix System with Caching + 50 Token Limit
ai_fix_cache = {}  # Cache dictionary for faster AI fixes

def get_ai_fix_local(code_snippet, issue_description):
    """Returns AI-generated fixes, ensuring structured output."""
    cache_key = (code_snippet, issue_description)

    if cache_key in ai_fix_cache:
        return ai_fix_cache[cache_key]  # Use cached result

    prompt = f"""
    You are an AI code reviewer. Improve the following Python code based on the detected issue.
    
    Issue: {issue_description}

    Code:
    {code_snippet}

    Provide only the corrected code **inside a Python code block**.
    Do not include explanations or unnecessary comments.

    ```python
    # Corrected Code
    def optimized_function():
        ...
    ```
    """

    result = local_llm(prompt, max_new_tokens=50, num_return_sequences=1, truncation=True, return_full_text=False)
    ai_fix = result[0]["generated_text"].strip()

    # Ensure a proper Python block
    if "```python" not in ai_fix:
        ai_fix = f"```python\n{ai_fix}\n```"

    # Remove redundant text
    ai_fix = ai_fix.replace("Please ensure that the code block is indented properly", "").strip()

    ai_fix_cache[cache_key] = ai_fix  # Save fix to cache
    return ai_fix


# ✅ Step 5: Save AI Fixes to a Markdown Report (Avoid Duplicates & Format Properly)
def save_report(file_name, issues):
    """ Save AI-generated fixes to a Markdown report, ensuring unique issues. """
    seen_issues = set()  # Track unique issues
    with open("code_review_report.md", "a") as report:
        report.write(f"### 📝 Code Review for {file_name}\n\n")
        for line, issue, ai_fix in issues:
            if issue in seen_issues:
                continue  # Skip duplicate issues
            seen_issues.add(issue)

            # Ensure correct Python block formatting
            ai_fix = ai_fix.replace("```python```python", "```python")  # Remove nested markers
            ai_fix = ai_fix.strip("`")  # Remove extra backticks if needed

            report.write(f"- **Line {line}:** {issue}\n")
            report.write(f"  - **Suggested Fix:**\n```python\n{ai_fix}\n```\n\n")

        if not issues:
            report.write("✅ No issues found.\n\n")


# ✅ Step 6: Analyze All `.py` Files in a Directory
def analyze_directory(directory_path):
    """ Scan all Python files in a directory and analyze them. """
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

        # Save report for each file
        save_report(filename, issue_list)


# ✅ Step 7: Run the Batch Analysis (Ensure test files exist in `src/test_files`)
analyze_directory("src/test_files")
