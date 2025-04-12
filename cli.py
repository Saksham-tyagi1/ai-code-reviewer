import typer
from src.analysis.ast_analyzer import CodeAnalyzer
from src.llm.llm_fixer import get_ai_fix_local
from src.analysis.report_generator import save_report

app = typer.Typer()

@app.command()
def analyze(file_path: str):
    """Analyze a Python file for code issues and show AI suggestions."""
    with open(file_path, 'r') as f:
        code = f.read()

    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)

    for line, issue, *_ in issues:
        fix = get_ai_fix_local(code, issue)
        typer.echo(f"\n[Line {line}] {issue}")
        typer.echo(f"  🔧 Suggested Fix:\n{fix}\n")

    save_report(file_path, issues)
    typer.echo("✅ Report saved as Markdown.")

@app.command()
def fix(file_path: str, out: str = typer.Option(None, help="Path to save fixed code with inline comments")):
    """Suggest AI fixes and optionally write fixed code to a new file."""
    with open(file_path, 'r') as f:
        code = f.read()

    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_code(code)
    lines = code.splitlines()

    for line, issue, *_ in issues:
        fix = get_ai_fix_local(code, issue)
        typer.echo(f"\n[Line {line}] {issue}")
        typer.echo(f"  🔧 Suggested Fix:\n{fix}\n")

        # Add AI suggestion as inline comment above the issue
        if out and 0 <= line - 1 < len(lines):
            comment = f"# AI Suggestion for Line {line}: {issue}"
            lines.insert(line - 1, comment)

    if out:
        with open(out, 'w') as fout:
            fout.write('\n'.join(lines))
        typer.echo(f"💾 Fixed version (with suggestions) saved to: {out}")

if __name__ == "__main__":
    app()
