import os
import re
from typing import List, Dict

# 🧼 Normalize issue descriptions by removing trailing [tags]
def normalize_description(desc: str) -> str:
    return re.sub(r"\[.*?\]$", "", desc.strip())

# 🧾 Ensure the fix is wrapped in proper Markdown code block
def format_fix(fix: str) -> str:
    fix = fix.strip()
    if not fix.startswith("```"):
        return f"```python\n{fix}\n```"
    return fix

def save_report(file_name: str, issues: List[Dict], report_dir: str = "reports"):
    """Save full Markdown report for a file with all issues."""
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "code_review_report.md")

    with open(report_path, "a") as report:
        report.write(f"\n---\n\n### 📝 Code Review for `{file_name}`\n\n")

        if issues:
            for issue in issues:
                line = issue.get("line", "?")
                raw_desc = issue.get("issue", "No issue description.")
                description = normalize_description(raw_desc)
                fix = format_fix(issue.get("fix", "No fix available."))
                issue_type = issue.get("issue_type", None)

                report.write(f"- **Line {line}:** {description}\n")
                if issue_type:
                    report.write(f"  _(Type: {issue_type})_\n")
                report.write(f"\n  **Suggested Fix:**\n\n{fix}\n\n")
        else:
            report.write("✅ No issues found.\n")

def save_individual_issues(file_name: str, issues: List[Dict], report_dir: str = "reports/issues"):
    """Create a separate Markdown file for each issue."""
    os.makedirs(report_dir, exist_ok=True)

    for idx, issue in enumerate(issues):
        line = issue.get("line", "?")
        raw_desc = issue.get("issue", "No issue description.")
        description = normalize_description(raw_desc)
        fix = format_fix(issue.get("fix", "No fix available."))
        issue_type = issue.get("issue_type", None)

        base_name = os.path.splitext(os.path.basename(file_name))[0]
        out_path = os.path.join(report_dir, f"{base_name}_issue_{idx + 1}.md")

        with open(out_path, "w") as f:
            f.write(f"# 🧠 AI Code Review Suggestion\n\n")
            f.write(f"- **Filename:** `{file_name}`\n")
            f.write(f"- **Line:** {line}\n")
            f.write(f"- **Issue:** {description}\n")
            if issue_type:
                f.write(f"- **Type:** `{issue_type}`\n")
            f.write(f"\n## 🔧 Suggested Fix\n\n{fix}\n")
