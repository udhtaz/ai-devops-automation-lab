import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class VSCodeLauncher:
    """
    Helper to open files in Visual Studio Code via the `code` CLI,
    optionally navigating to a specific line and column.
    """

    def __init__(self, code_cmd: str = "code"):
        """
        :param code_cmd: Name or path of the VS Code CLI executable (default: "code").
        """
        self.code_cmd = code_cmd

    def open(
        self,
        file_path: Path,
        line: Optional[int] = None,
        column: Optional[int] = None
    ) -> bool:
        """
        Open a single file in VS Code.

        :param file_path: Path to the file to open.
        :param line: (Optional) Line number to navigate to.
        :param column: (Optional) Column number to navigate to.
        :return: True if VS Code was launched successfully, False otherwise.
        """
        if not file_path.exists():
            logger.error(f"[VSCodeLauncher] File not found: {file_path}")
            return False

        cmd: List[str] = [self.code_cmd]
        if line is not None:
            # Format: code --goto file:line:column
            loc = f"{file_path}"
            if column is not None:
                loc = f"{loc}:{line}:{column}"
            else:
                loc = f"{loc}:{line}"
            cmd += ["--goto", loc]
        else:
            # Just open the file
            cmd.append(str(file_path))

        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[VSCodeLauncher] Failed to launch VS Code: {e}")
            return False

    def open_many(
        self,
        file_paths: List[Path],
        line: Optional[int] = None,
        column: Optional[int] = None
    ) -> List[bool]:
        """
        Open multiple files in VS Code sequentially.

        :param file_paths: List of Paths to open.
        :param line: (Optional) Line number to navigate to in each file.
        :param column: (Optional) Column number to navigate to in each file.
        :return: List of booleans indicating success/failure for each file.
        """
        results: List[bool] = []
        for fp in file_paths:
            result = self.open(fp, line=line, column=column)
            results.append(result)
        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Open one or more files in VS Code via the `code` CLI."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="File path(s) to open in VS Code"
    )
    parser.add_argument(
        "--line",
        type=int,
        default=None,
        help="Line number to navigate to"
    )
    parser.add_argument(
        "--column",
        type=int,
        default=None,
        help="Column number to navigate to"
    )
    args = parser.parse_args()

    launcher = VSCodeLauncher()
    statuses = launcher.open_many(args.files, line=args.line, column=args.column)
    for path, ok in zip(args.files, statuses):
        status = "✓" if ok else "✗"
        print(f"{status} {path}")
