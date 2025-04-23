from pathlib import Path
from typing import Iterator, List, Optional


class FileScanner:
    """
    Recursively scan a directory for files matching a given set of extensions,
    while excluding specified directories.
    """

    def __init__(
        self,
        root: Path,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
    ):
        self.root = root
        # default to common code file extensions
        self.extensions = extensions or [
            ".py", ".js", ".ts", ".java", ".cpp", ".cs", ".go", ".rb", ".php", ".rs"
        ]
        # default to skip VCS, dependencies, caches
        self.exclude_dirs = set(exclude_dirs or [
            ".git", "node_modules", "venv", "__pycache__", "dist", "build"
        ])

    def scan(self) -> Iterator[Path]:
        """
        Yield every file under `root` whose extension is in `self.extensions`,
        excluding any path that contains one of `self.exclude_dirs`.
        """
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if self._is_excluded(path):
                continue
            if self._has_valid_ext(path):
                yield path

    def _has_valid_ext(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def _is_excluded(self, path: Path) -> bool:
        # if any part of the path is in exclude_dirs, skip it
        return any(part in self.exclude_dirs for part in path.parts)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan a directory tree for code files by extension"
    )
    parser.add_argument(
        "root",
        type=Path,
        help="Root directory to scan"
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        help="List of extensions to include (e.g. .py .js .ts)"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="List of directory names to skip (e.g. .git node_modules)"
    )
    args = parser.parse_args()

    scanner = FileScanner(
        root=args.root,
        extensions=args.ext,
        exclude_dirs=args.exclude
    )

    for file_path in scanner.scan():
        print(file_path)


if __name__ == "__main__":
    main()
