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


# ✅ Step 3: Function to Analyze Python Code
def analyze_code(code):
    try:
        tree = ast.parse(code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return analyzer.issues
    except Exception as e:
        return [(0, f"Error parsing code: {e}", None)]


# ✅ Step 4: AI Fix System with Caching + Proper Formatting
ai_fix_cache = {}  # Cache dictionary for AI fixes

def get_ai_fix_local(code_snippet, issue_description):
    """Returns AI-generated fixes, ensuring structured output."""
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

    # ✅ Ensure correct formatting
    ai_fix = ai_fix.replace("```python\n```python", "```python")  # Fix nested issues
    if "```python" not in ai_fix:
        ai_fix = f"```python\n{ai_fix}\n```"

    ai_fix_cache[cache_key] = ai_fix  # Save fix to cache
    return ai_fix


# ✅ Step 5: Save AI Fixes to a Markdown Report
def save_report(file_name, issues):
    """ Save AI-generated fixes to a Markdown report, ensuring clean formatting and avoiding duplicates. """
    
    # ✅ Clear report before writing new issues
    if os.path.exists("code_review_report.md"):
        os.remove("code_review_report.md")

    with open("code_review_report.md", "a") as report:
        report.write(f"### 📝 Code Review for {file_name}\n\n")

        seen_issues = set()  # ✅ Prevent duplicate issues
        if issues:
            for line, issue, ai_fix in issues:
                if issue not in seen_issues:  # ✅ Ensure each issue is reported only once
                    seen_issues.add(issue)
                    report.write(f"- **Line {line}:** {issue}\n\n")

                    # ✅ Fix AI-generated code block formatting
                    ai_fix_cleaned = ai_fix.replace("```python\n```python", "```python").strip()

                    # ✅ Ensure proper indentation & formatting
                    if not ai_fix_cleaned.startswith("```python"):
                        ai_fix_cleaned = f"```python\n{ai_fix_cleaned}\n```"

                    report.write(f"  - **Suggested Fix:**\n\n{ai_fix_cleaned}\n\n")
        else:
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
