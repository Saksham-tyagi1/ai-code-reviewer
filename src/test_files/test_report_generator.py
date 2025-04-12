import os
from src.analysis.report_generator import save_report

def test_save_report_creates_file(tmp_path):
    filename = "example.py"
    results = [
        {"line": 2, "issue": "Unused import", "fix": "Remove it"},
        {"line": 5, "issue": "Unused variable", "fix": "Delete it"}
    ]
    os.makedirs("reports", exist_ok=True)
    save_report(filename, results)
    assert os.path.exists("reports/code_review_report.md")
