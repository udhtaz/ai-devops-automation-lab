from pathlib import Path
from typing import List, Dict

LANG_TEMPLATES = {
    "Python": """\
import pytest
from {module_import} import {func_names}

{tests}
""",
    "JavaScript": """\
const {{ describe, it, expect }} = require('jest');
const {{ {func_names} }} = require('{module_path}');

describe('{module_name}', () => {{
{tests}
}});
""",
    # You can add more templates (TypeScript, Java, Go…) here
}


COMMENT_MARKERS = {
    "Python": "# copilot: write tests for this function\n\n",
    "JavaScript": "// copilot: write tests for this function\n\n",
    # Fallback for other C‑style langs:
    "default": "// copilot: write tests for this function\n\n"
}


class TestGenerator:
    def __init__(self, tests_root: Path = None, project_root: Path = None):
    # def __init__(self, tests_root: Path = None):
        # By default, put all tests under a top-level "tests/" folder
        # self.tests_root = tests_root or Path("tests")
        self.tests_root = tests_root or Path("tests")
        # make this the repo you scanned
        self.project_root = project_root or Path.cwd()

    def create_stubs(self, metas: List[Dict]) -> List[Path]:
        """
        For each meta dict with keys: path, language, needs_test, func_names…
        Generate a stub test file (with a Copilot marker) and return its Path.
        """
        created = []

        for m in metas:
            src: Path = m["path"]
            lang: str = m["language"]
            funcs: List[str] = m["func_names"]

            # 1. Decide on test file location & name
            # rel = src.relative_to(Path.cwd())
            rel = src.relative_to(self.project_root)
            test_dir = self.tests_root / rel.parent           
            test_dir.mkdir(parents=True, exist_ok=True)

            if lang == "Python":
                test_name = f"test_{src.stem}.py"
            elif lang.startswith("JavaScript"):
                test_name = f"{src.stem}.test.js"
            else:
                # simple fallback
                test_name = f"test_{src.stem}.txt"

            test_path = test_dir / test_name

            # 2. Render boilerplate
            tmpl = LANG_TEMPLATES.get(lang)
            if tmpl:
                module_import = ".".join(rel.with_suffix("").parts)
                func_names = ", ".join(funcs)
                # Build per-function test stubs
                if lang == "Python":
                    tests_block = "\n".join(
                        f"def test_{fn}():\n    # TODO: test {fn}\n    assert False\n"
                        for fn in funcs
                    )
                else:  # JavaScript
                    tests_block = "\n".join(
                        f"  it('should test {fn}', () => {{\n"
                        f"    // TODO: test {fn}\n"
                        f"    expect(false).toBe(true);\n"
                        f"  }});\n"
                        for fn in funcs
                    )

                content = tmpl.format(
                    module_import=module_import,
                    func_names=func_names,
                    module_name=src.stem,
                    module_path=str(src.with_suffix("")).replace("\\\\", "/"),
                    tests=tests_block
                )
            else:
                # fallback minimal placeholder
                content = f"# TODO: write tests for {src}\n"

            # 3. Prepend Copilot marker
            marker = COMMENT_MARKERS.get(lang, COMMENT_MARKERS["default"])
            final_content = marker + content

            # 4. Write the file
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            created.append(test_path)

        return created
