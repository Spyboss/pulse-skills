import ast
import os
from git import Repo
from pulse.utils import log

class ReactLinterSkill:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.logger = log.get_logger("ReactLinter")

    def analyze_code(self, file_path):
        """Analyze a React JS file for common issues."""
        if not file_path.endswith(".jsx") and not file_path.endswith(".js"):
            return []
        with open(file_path, "r") as f:
            code = f.read()
        issues = []
        # Check for missing React keys in lists
        if "map(" in code and "key=" not in code:
            issues.append("Missing 'key' prop in list rendering.")
        # Check for unused imports
        tree = ast.parse(code)
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        for imp in imports:
            if code.count(imp) == 1:
                issues.append(f"Unused import: {imp}")
        return issues

    def lint_portfolio(self):
        """Lint all JS/JSX files in the portfolio repo."""
        repo = Repo(self.repo_path)
        issues = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith((".jsx", ".js")):
                    file_issues = self.analyze_code(os.path.join(root, file))
                    if file_issues:
                        issues.append({"file": file, "issues": file_issues})
                        self.logger.info(f"Found issues in {file}: {file_issues}")
        return issues

    def apply_fixes(self, issues):
        """Apply automated fixes (e.g., add keys) and commit changes."""
        repo = Repo(self.repo_path)
        for issue in issues:
            file_path = os.path.join(self.repo_path, issue["file"])
            # Example: Add key prop (simplified)
            with open(file_path, "r+") as f:
                code = f.read()
                if "Missing 'key'" in str(issue["issues"]):
                    code = code.replace("map((item)", "map((item, index) => <div key={index}>")
                    f.seek(0)
                    f.write(code)
                    f.truncate()
            repo.index.add([file_path])
        repo.index.commit("ReactLinter: Auto-fix code issues")
        self.logger.info("Applied fixes and committed changes")

if __name__ == "__main__":
    linter = ReactLinterSkill("/path/to/portfolio/repo")
    issues = linter.lint_portfolio()
    if issues:
        linter.apply_fixes(issues)
