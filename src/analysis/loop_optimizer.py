import ast

class LoopOptimizer(ast.NodeVisitor):
    """Detects inefficient loop structures in Python code."""

    def __init__(self):
        self.issues = []

    def visit_For(self, node):
        """Detects inefficient for-loops."""
        self.check_unnecessary_range(node)
        self.check_modifying_list_while_iterating(node)
        self.check_nested_loops(node)
        self.generic_visit(node)

    def visit_While(self, node):
        """Detects inefficient while-loops."""
        self.check_nested_loops(node)
        self.generic_visit(node)

    def check_unnecessary_range(self, node):
        """Detects loops using range(len(x)) instead of direct iteration."""
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call):
                if isinstance(node.iter.args[0].func, ast.Name) and node.iter.args[0].func.id == "len":
                    self.issues.append(
                        (node.lineno, "⚠️ Inefficient loop: Consider iterating directly instead of using range(len(x)).")
                    )

    def check_modifying_list_while_iterating(self, node):
        """Detects modifying a list while iterating over it."""
        if isinstance(node.iter, ast.Name):
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["append", "remove", "pop"]:
                        self.issues.append(
                            (node.lineno, "⚠️ Modifying list while iterating. Consider using a copy or list comprehension.")
                        )

    def check_nested_loops(self, node):
        """Detects nested loops that may cause high time complexity."""
        for child in node.body:
            if isinstance(child, (ast.For, ast.While)):
                self.issues.append(
                    (child.lineno, "⚠️ Nested loop detected: Consider optimizing.")
                )

def analyze_loops(tree):
    """Runs loop optimization analysis on the AST."""
    analyzer = LoopOptimizer()
    analyzer.visit(tree)
    return analyzer.issues
