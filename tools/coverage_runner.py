"""
tools/coverage_runner.py

Run pytest with coverage on a Python‐based subrepo, auto-detecting source & tests.
Usage:
    python tools/coverage_runner.py <repo_root> [--html]
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def find_tests_dir(root: Path) -> Path:
    """
    Prefer a top-level 'tests/' folder under root.
    If none exists, fall back to any subfolder named 'tests'.
    """
    t = root / "tests"
    if t.is_dir():
        return t
    # fallback: first subdir named 'tests'
    for sub in root.iterdir():
        if sub.is_dir() and sub.name.lower() == "tests":
            return sub
    raise FileNotFoundError(f"No tests/ directory found under {root}")


def find_source_dir(root: Path) -> str:
    """
    Find the subdirectory (under root) with the largest number of .py files,
    and return its path relative to root (as a string).
    This becomes our '--cov=<source>' target.
    """
    counts = {}
    # include root itself
    counts[root] = len(list(root.rglob("*.py")))
    # every subdirectory
    for d in root.rglob("*"):
        if d.is_dir():
            counts[d] = len(list(d.rglob("*.py")))

    # pick the directory with the max .py count
    best = max(counts, key=lambda d: counts[d])
    rel = best.relative_to(root)
    # if it's the root itself, use '.' as cov target
    return "." if rel == Path() else str(rel)


def main():
    parser = argparse.ArgumentParser(
        description="Run pytest with coverage on a Python repo (auto-detect src & tests)"
    )
    parser.add_argument(
        "repo",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the Python repo (default: current directory)"
    )
    parser.add_argument(
        "--html",
        "-H",
        action="store_true",
        help="Also generate an HTML coverage report"
    )
    args = parser.parse_args()

    repo_root = args.repo.resolve()
    if not repo_root.is_dir():
        print(f"❌ Error: directory not found: {repo_root}")
        sys.exit(1)

    try:
        tests_dir = find_tests_dir(repo_root)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    cov_target = find_source_dir(repo_root)
    xml_report = repo_root / "coverage.xml"

    # run from inside the repo
    prev_cwd = os.getcwd()
    os.chdir(repo_root)

    print(f"🧪 Running pytest with coverage on '{cov_target}' using tests in '{tests_dir.name}'…")
    cmd = [
        "pytest",
        f"--cov={cov_target}",
        str(tests_dir),
        "--cov-report=term-missing",
        f"--cov-report=xml:{xml_report.name}"
    ]
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Tests completed successfully!")
        print(f"📊 Coverage XML report: {xml_report}")
        if args.html:
            html_cmd = [
                "pytest",
                f"--cov={cov_target}",
                str(tests_dir),
                "--cov-report=html"
            ]
            subprocess.run(html_cmd, check=True)
            print("🌐 HTML coverage report generated in htmlcov/")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ pytest failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    finally:
        os.chdir(prev_cwd)


if __name__ == "__main__":
    main()
