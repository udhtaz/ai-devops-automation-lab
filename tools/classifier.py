from pathlib import Path
from typing import List, Dict, Optional
import ast
import re

class CodeClassifier:
    """
    Given a list of file paths, decide which ones are code files worth testing,
    detect their language, count non-comment lines, and extract top‐level function names.
    """

    DEFAULT_EXTENSIONS = {
        ".py", ".js", ".ts", ".java", ".cpp", ".cs", ".go", ".rb", ".php", ".rs"
    }

    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".cs": "C#",
        ".go": "Go",
        ".rb": "Ruby",
        ".php": "PHP",
        ".rs": "Rust",
    }

    def __init__(
        self,
        min_bytes: int = 100,
        min_loc: int = 10,
        extensions: Optional[set] = None
    ):
        self.min_bytes = min_bytes
        self.min_loc = min_loc
        self.extensions = extensions or self.DEFAULT_EXTENSIONS

    def classify(self, paths: List[Path]) -> List[Dict]:
        """
        Inspect each path and return a list of metadata dicts for files that:
         - Have a supported extension
         - Exceed size and LOC thresholds

        Each dict contains:
         - path: Path
         - language: str
         - lines_of_code: int
         - func_names: List[str]
        """
        metas = []
        for path in paths:
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.extensions:
                continue
            try:
                if path.stat().st_size < self.min_bytes:
                    continue
            except OSError:
                continue

            content = self._read_file(path)
            if content is None:
                continue

            loc = self._count_code_lines(content)
            if loc < self.min_loc:
                continue

            lang = self.LANGUAGE_MAP.get(path.suffix.lower(), "Unknown")
            funcs = self._extract_function_names(content, lang)

            metas.append({
                "path": path,
                "language": lang,
                "lines_of_code": loc,
                "func_names": funcs
            })
        return metas

    def _read_file(self, path: Path) -> Optional[str]:
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return None

    def _count_code_lines(self, content: str) -> int:
        lines = 0
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            # skip single-line comments for common langs
            if stripped.startswith(("#", "//")):
                continue
            # skip block-comment markers
            if stripped.startswith(("/*", "*", "--")):
                continue
            lines += 1
        return lines

    def _extract_function_names(self, content: str, language: str) -> List[str]:
        """
        Return a list of top-level function or method names detected in the file.
        """
        names: List[str] = []

        if language == "Python":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        names.append(node.name)
            except SyntaxError:
                pass

        elif language in ("JavaScript", "TypeScript"):
            # function foo(...) or foo = (...) => { ... }
            func_defs = re.findall(r'function\s+(\w+)\s*\(', content)
            arrow_defs = re.findall(r'(\w+)\s*=\s*\([^)]*\)\s*=>', content)
            names.extend(func_defs)
            names.extend(arrow_defs)

        elif language == "Java":
            # match returnType name(args) { ...
            method_defs = re.findall(
                r'(?:public|private|protected|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{',
                content
            )
            names.extend(method_defs)

        elif language == "C++":
            cpp_defs = re.findall(r'[\w\*\&]+\s+(\w+)\s*\([^)]*\)\s*\{', content)
            names.extend(cpp_defs)

        elif language == "C#":
            cs_defs = re.findall(
                r'(?:public|private|protected|internal|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{',
                content
            )
            names.extend(cs_defs)

        elif language == "Go":
            go_defs = re.findall(r'func\s+(\w+)\s*\(', content)
            names.extend(go_defs)

        elif language == "Ruby":
            rb_defs = re.findall(r'def\s+(\w+)', content)
            names.extend(rb_defs)

        elif language == "PHP":
            php_defs = re.findall(r'function\s+(\w+)\s*\(', content)
            names.extend(php_defs)

        elif language == "Rust":
            rs_defs = re.findall(r'fn\s+(\w+)\s*\(', content)
            names.extend(rs_defs)

        # Deduplicate
        return list(dict.fromkeys(names))
