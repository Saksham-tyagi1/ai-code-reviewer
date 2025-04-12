import ast

DEFAULT_COMPLEXITY_THRESHOLD = 10  # Allow configurable threshold

class CyclomaticComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes the cyclomatic complexity of functions."""
    
    def __init__(self, threshold=DEFAULT_COMPLEXITY_THRESHOLD):
        self.complexities = {}
        self.issues = []
        self.threshold = threshold

    def visit_FunctionDef(self, node):
        self.calculate_complexity(node)

    def visit_AsyncFunctionDef(self, node):
        self.calculate_complexity(node)

    def calculate_complexity(self, node):
        """Calculates the complexity of functions/methods."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, 
                                  ast.ExceptHandler, ast.With, ast.Assert, ast.Try)):
                complexity += 1

        self.complexities[node.name] = (node.lineno, complexity)

        if complexity > self.threshold:
            self.issues.append(
                (node.lineno, f"⚠️ Function '{node.name}' has high cyclomatic complexity ({complexity}). Consider refactoring.")
            )

    def analyze(self, tree):
        """Runs complexity analysis on the AST."""
        self.visit(tree)
        return self.issues

def analyze_cyclomatic_complexity(tree, threshold=DEFAULT_COMPLEXITY_THRESHOLD):
    """Runs cyclomatic complexity analysis with a configurable threshold."""
    analyzer = CyclomaticComplexityAnalyzer(threshold)
    return analyzer.analyze(tree)
