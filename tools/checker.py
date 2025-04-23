from pathlib import Path
from typing import List, Dict, Any

class TestChecker:
    """
    Checks for existing test files corresponding to each source file.
    """

    def __init__(
        self,
        project_root: Path,
        test_dir_name: str = "tests",
        test_patterns: List[str] = None
    ):
        self.project_root = project_root
        self.tests_root = project_root / test_dir_name
        # Patterns to identify test files by name
        self.test_patterns = test_patterns or [
            "test_", "_test", "spec_", "_spec", ".test.", ".spec."
        ]

    def annotate(self, file_metas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        For each meta dict (must include "path": Path or str), check if a corresponding
        test file exists. Adds a boolean "needs_test" key to each dict.
        
        Returns the updated list of metas.
        """
        updated = []
        for meta in file_metas:
            # Ensure we have a Path object
            src = Path(meta["path"])
            base = src.stem
            parent = src.parent

            test_found = False

            # 1. Look for test files in the same directory
            for candidate in parent.glob(f"*{base}*"):
                if any(pat in candidate.name for pat in self.test_patterns):
                    test_found = True
                    break

            # 2. Look in a sibling `tests/` folder
            if not test_found:
                tests_dir = parent / "tests"
                if tests_dir.exists():
                    for candidate in tests_dir.glob(f"*{base}*"):
                        if any(pat in candidate.name for pat in self.test_patterns):
                            test_found = True
                            break

            # 3. Look in the global tests directory at project root
            if not test_found and self.tests_root.exists():
                for candidate in self.tests_root.rglob(f"*{base}*"):
                    if any(pat in candidate.name for pat in self.test_patterns):
                        test_found = True
                        break

            # Annotate whether we need to generate a test stub
            meta["needs_test"] = not test_found
            updated.append(meta)

        return updated
