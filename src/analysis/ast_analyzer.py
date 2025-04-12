import ast
from src.analysis.complexity import analyze_cyclomatic_complexity
from src.analysis.dead_code import detect_dead_code
from src.analysis.loop_optimizer import analyze_loops

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

        self.defined_variables = set()
        self.used_variables = set()
        self.variable_lines = {}  # variable → line number

        self.imported_modules = set()
        self.used_imports = set()
        self.import_lines = {}  # import → line number

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_modules.add(name)
            self.import_lines[name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_modules.add(name)
            self.import_lines[name] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_variables.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
            if node.id in self.imported_modules:
                self.used_imports.add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_variables.add(target.id)
                self.variable_lines[target.id] = node.lineno
        self.generic_visit(node)

    def report_unused_imports(self):
        unused = self.imported_modules - self.used_imports
        for imp in unused:
            line = self.import_lines.get(imp, 1)
            self.issues.append((line, f"⚠️ Unused import detected: '{imp}'. Consider removing it.", "unused_import"))

    def report_unused_variables(self):
        unused = self.defined_variables - self.used_variables
        for var in unused:
            line = self.variable_lines.get(var, 1)
            self.issues.append((line, f"⚠️ Variable '{var}' is assigned but never used.", "unused_variable"))

    def analyze_code(self, code: str):
        """Parses and analyzes Python code."""
        try:
            tree = ast.parse(code)
            self.visit(tree)

            # Modular analyzers
            self.issues.extend(analyze_cyclomatic_complexity(tree))
            self.issues.extend(detect_dead_code(tree))
            self.issues.extend(analyze_loops(tree))

            self.report_unused_imports()
            self.report_unused_variables()

            # ✅ Deduplicate by (line, tag or description)
            seen = set()
            unique_issues = []
            for issue in self.issues:
                line = issue[0]
                desc = issue[1]
                tag = issue[2] if len(issue) >= 3 else None
                key = (line, tag or desc)
                if key not in seen:
                    seen.add(key)
                    unique_issues.append(issue)

            return unique_issues

        except Exception as e:
            return [(0, f"❌ Error parsing code: {e}", None)]
