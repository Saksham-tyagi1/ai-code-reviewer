import ast

class DeadCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        """Detects dead code inside functions."""
        self.detect_unreachable_code(node)
        self.generic_visit(node)

    def detect_unreachable_code(self, node):
        """Identifies code that is unreachable due to early return, break, or continue."""
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                for unreachable in node.body[i + 1:]:
                    if not isinstance(unreachable, ast.FunctionDef):
                        self.issues.append(
                            (unreachable.lineno, "⚠️ Unreachable code detected after return/break/continue.")
                        )
                break

    def analyze(self, tree):
        """Runs dead code analysis (only unreachable code now)."""
        self.visit(tree)
        return self.issues

def detect_dead_code(tree):
    """Runs dead code analysis on the AST."""
    analyzer = DeadCodeAnalyzer()
    return analyzer.analyze(tree)
