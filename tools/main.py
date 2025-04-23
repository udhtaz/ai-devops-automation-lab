"""
tools/main.py

Orchestrator for the automated unit‐test stub generation pipeline:
1. Scan for code files
2. Classify them (language, LOC, function names)
3. Check for existing tests
4. Report coverage gaps (CSV/JSON) — includes both True/False
5. Generate stub tests with Copilot hints
6. (Optional) Open stubs in VS Code
"""

import argparse
from pathlib import Path

from scanner import FileScanner
from classifier import CodeClassifier
from checker import TestChecker
from reporter import Reporter
from generator import TestGenerator
from vscode_integration import VSCodeLauncher


def main():
    parser = argparse.ArgumentParser(
        description="Generate unit‐test stubs for a codebase"
    )

    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the repository to scan (default: current directory)"
    )

    parser.add_argument(
        "--report",
        "-r",
        type=Path,
        default=None,
        help=(
            "Output path for the coverage report (CSV or JSON). "
            "Defaults to <root>/code_checker_report.csv"
        )
    )
    parser.add_argument(
        "--test-dir",
        default="tests",
        help="Name of the directory (relative to root) in which to place test stubs"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Immediately open newly created stubs in VS Code"
    )
    args = parser.parse_args()

    root_dir = args.root.resolve()

    # determine report path
    if args.report:
        report_path = args.report
    else:
        report_path = root_dir / "code_checker_report.csv"

    # 1. Discover files
    scanner = FileScanner(root=root_dir)
    all_files = list(scanner.scan())

    # 2. Classify code files
    classifier = CodeClassifier()
    metas = classifier.classify(all_files)

    # 3. Check for existing tests
    checker = TestChecker(project_root=root_dir, test_dir_name=args.test_dir)
    results = checker.annotate(metas)

    # 4. Write coverage report (includes both needs_test=True/False)
    reporter = Reporter(output_path=report_path, index=False, print_preview=True)
    reporter.save(results)
    print(f"\n[main] Coverage report saved to: {report_path}")

    # 5. Generate missing test stubs
    to_generate = [m for m in results if m.get("needs_test")]
    if to_generate:
        # generator = TestGenerator(tests_root=root_dir / args.test_dir)
        generator = TestGenerator(
            tests_root=root_dir / args.test_dir,
            project_root=root_dir
        )
        stubs = generator.create_stubs(to_generate)
        print(f"[main] Created {len(stubs)} test stubs under “{args.test_dir}/”")
    else:
        print("[main] No missing tests detected; no stubs created.")
        stubs = []

    # 6. Optionally open in VS Code
    if args.open and stubs:
        launcher = VSCodeLauncher()
        statuses = launcher.open_many(stubs)
        for path, ok in zip(stubs, statuses):
            marker = "✓" if ok else "✗"
            print(f"{marker} {path}")


if __name__ == "__main__":
    main()
