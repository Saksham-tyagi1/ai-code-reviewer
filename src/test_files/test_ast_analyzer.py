from src.analysis.ast_analyzer import CodeAnalyzer

def test_detect_unused_import():
    code = "import os\n"
    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)
    assert any("Unused import" in issue[1] for issue in issues)

def test_detect_unreachable_code():
    code = "def foo():\n    return\n    print('This is unreachable')"
    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)
    assert any("Unreachable code" in issue[1] for issue in issues)

def test_detect_unused_variable():
    code = "x = 5"
    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)
    assert any("defined but never used" in issue[1] for issue in issues)

