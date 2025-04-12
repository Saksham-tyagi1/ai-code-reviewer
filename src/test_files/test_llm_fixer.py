from src.llm.llm_fixer import get_ai_fix_local
from src.analysis.ast_analyzer import CodeAnalyzer

def test_fix_unused_import():
    code = "import math"
    issue = "Unused import detected: 'math'"
    fix = get_ai_fix_local(code, issue)
    assert "Removed unused import" in fix


def test_detect_unused_variable():
    code = "def func():\n    unused_var = 42\n    return True"
    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)
    assert any("defined but never used" in issue[1] for issue in issues)
