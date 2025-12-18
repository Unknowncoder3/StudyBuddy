import ast
import re
from typing import Dict, List

import asttokens
from tree_sitter import Parser
from tree_sitter_languages import get_language


# =====================================================
# SUPPORTED LANGUAGES
# =====================================================

LANGUAGES = {
    "python": "python",
    "javascript": "javascript",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "sql": "sql",
}


# =====================================================
# DATA MODEL
# =====================================================

class Suggestion:
    def __init__(self, line, category, message):
        self.line = line
        self.category = category
        self.message = message

    def to_dict(self):
        return {
            "line": self.line,
            "category": self.category,
            "message": self.message,
        }


# =====================================================
# PYTHON ANALYZER (ROBUST)
# =====================================================

def analyze_python(source: str) -> Dict:
    suggestions: List[Suggestion] = []
    explanation: List[str] = []

    try:
        atok = asttokens.ASTTokens(source, parse=True)
        tree = atok.tree
    except SyntaxError as e:
        return {
            "error": f"Syntax Error: {e}",
            "explanation": "",
            "suggestions": [],
        }

    # Walk AST
    for node in ast.walk(tree):

        # ❌ input misuse
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "input":
            suggestions.append(
                Suggestion(
                    node.lineno,
                    "logic",
                    "input() returns a string. Convert it using int() if numeric input is expected.",
                )
            )

        # ❌ range(len())
        if isinstance(node, ast.For):
            if (
                isinstance(node.iter, ast.Call)
                and getattr(node.iter.func, "id", "") == "range"
            ):
                suggestions.append(
                    Suggestion(
                        node.lineno,
                        "performance",
                        "Prefer enumerate() instead of range(len()).",
                    )
                )

        # ❌ open() without with
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
            suggestions.append(
                Suggestion(
                    node.lineno,
                    "resource",
                    "Use 'with open(...)' to ensure file closure.",
                )
            )

    # Top-level structure
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            explanation.append(f"Function `{node.name}` defined at line {node.lineno}.")
        if isinstance(node, ast.ClassDef):
            explanation.append(f"Class `{node.name}` defined at line {node.lineno}.")

    if not suggestions:
        suggestions.append(
            Suggestion(
                0,
                "clean",
                "No critical issues detected. Code structure looks fine.",
            )
        )

    return {
        "explanation": "\n".join(explanation),
        "suggestions": [s.to_dict() for s in suggestions],
    }


# =====================================================
# GENERIC ANALYZER (TREE-SITTER SAFE)
# =====================================================

def analyze_generic(source: str, language: str) -> Dict:
    suggestions: List[Suggestion] = []

    try:
        parser = Parser()
        parser.language = get_language(language)
        parser.parse(bytes(source, "utf-8"))
    except Exception:
        return {
            "explanation": f"{language.upper()} parsed using fallback rules.",
            "suggestions": [
                Suggestion(
                    0,
                    "info",
                    f"Deep AST analysis not available for {language.upper()}.",
                ).to_dict()
            ],
        }

    if language == "javascript" and "var " in source:
        suggestions.append(
            Suggestion(1, "modern-js", "Avoid var. Use let or const.")
        )

    if language in {"c", "cpp"} and "gets(" in source:
        suggestions.append(
            Suggestion(1, "security", "Avoid unsafe function gets().")
        )

    if language == "sql" and re.search(r"select\s+\*", source, re.I):
        suggestions.append(
            Suggestion(1, "sql", "Avoid SELECT * in production queries.")
        )

    if not suggestions:
        suggestions.append(
            Suggestion(0, "clean", "No major issues detected.")
        )

    return {
        "explanation": f"{language.upper()} code analyzed successfully.",
        "suggestions": [s.to_dict() for s in suggestions],
    }


# =====================================================
# FLASK API ENTRY POINT
# =====================================================

def analyze_code_api(source: str, language: str) -> Dict:
    if not source or not source.strip():
        return {
            "error": "No source code provided",
            "explanation": "",
            "suggestions": [],
        }

    if language not in LANGUAGES:
        return {
            "error": f"Unsupported language: {language}",
            "explanation": "",
            "suggestions": [],
        }

    if language == "python":
        return analyze_python(source)

    return analyze_generic(source, language)
