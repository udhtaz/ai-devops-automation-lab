import os
from pathlib import Path
import sys
from typing import List, Dict
import pandas as pd
import ast
import re

def analyze_test_coverage(directory_path: str) -> Dict[str, List[Dict]]:
    """
    Analyze directory for code files and check which ones need unit tests.
    Returns dict with files needing tests and files that already have tests.
    """
    supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go', '.rb', '.php', '.rs'}
    files_info = []
    
    def is_test_file(filename: str) -> bool:
        """Check if file is a test file based on common test naming patterns."""
        test_patterns = ['test_', '_test', 'spec_', '_spec', '.test.', '.spec.']
        return any(pattern in filename.lower() for pattern in test_patterns)

    def count_code_lines(file_path: Path) -> int:
        """Count actual lines of code in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                code_lines = [line.strip() for line in content.splitlines() 
                            if line.strip() and not line.strip().startswith(('#', '//', '/*', '*', '--'))]
                return len(code_lines)
        except Exception:
            return 0

    def is_code_file(file_path: Path) -> bool:
        """Check if file is a valid code file to process."""
        if not file_path.suffix.lower() in supported_extensions:
            return False
            
        try:
            if file_path.stat().st_size < 100:  # Skip files under 100 bytes
                return False
                
            lines = count_code_lines(file_path)
            return lines >= 10
                
        except Exception:
            return False

    def count_functions(file_path: Path) -> int:
        """Count number of function definitions based on file type."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Python files - use ast
                if file_path.suffix == '.py':
                    tree = ast.parse(content)
                    return len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                
                # JavaScript/TypeScript
                elif file_path.suffix in ['.js', '.ts']:
                    # Match function declarations and expressions
                    funcs = re.findall(r'function\s+\w+\s*\(|function\s*\(|\)\s*=>\s*{|\w+\s*:\s*function\s*\(', content)
                    return len(funcs)
                
                # Java
                elif file_path.suffix == '.java':
                    # Match method declarations
                    methods = re.findall(r'(public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])', content)
                    return len(methods)
                
                # C++
                elif file_path.suffix == '.cpp':
                    # Match function declarations
                    funcs = re.findall(r'[\w\*]+\s+[\w\*]+\s*\([^\)]*\)\s*{', content)
                    return len(funcs)
                
                # C#
                elif file_path.suffix == '.cs':
                    # Match method declarations
                    methods = re.findall(r'(public|private|protected|internal|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])', content)
                    return len(methods)
                
                # Go
                elif file_path.suffix == '.go':
                    # Match func declarations
                    funcs = re.findall(r'func\s+\w+\s*\([^\)]*\)', content)
                    return len(funcs)
                
                # Ruby
                elif file_path.suffix == '.rb':
                    # Match def declarations
                    funcs = re.findall(r'def\s+\w+', content)
                    return len(funcs)
                
                # PHP
                elif file_path.suffix == '.php':
                    # Match function declarations
                    funcs = re.findall(r'function\s+\w+\s*\([^\)]*\)', content)
                    return len(funcs)
                
                # Rust
                elif file_path.suffix == '.rs':
                    # Match fn declarations
                    funcs = re.findall(r'fn\s+\w+\s*\([^\)]*\)', content)
                    return len(funcs)
                    
                return 0
                
        except Exception:
            return 0
    
    directory = Path(directory_path)
    
    # Walk through directory recursively
    for root, _, files in os.walk(directory):
        root_path = Path(root)
        
        for file in files:
            file_path = root_path / file
            
            # Skip if not a supported code file
            if not is_code_file(file_path):
                continue
                
            # Check if corresponding test file exists
            base_name = file_path.stem
            parent_dir = file_path.parent
            
            # Look for test file in same directory and tests directory
            test_exists = False
            for test_file in parent_dir.glob(f'*{base_name}*'):
                if is_test_file(test_file.name):
                    test_exists = True
                    break
            
            tests_dir = parent_dir / 'tests'
            if tests_dir.exists():
                for test_file in tests_dir.glob(f'*{base_name}*'):
                    if is_test_file(test_file.name):
                        test_exists = True
                        break

            files_info.append({
                'filename': file_path.name,
                'lines_of_code': count_code_lines(file_path),
                'needs_tests': not test_exists,
                'num_functions': count_functions(file_path)
            })
                
    # Convert to pandas DataFrame
    df = pd.DataFrame(files_info)
    
    return {
        'files': files_info,
        'dataframe': df
    }

if __name__ == "__main__":
    # Get directory path from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python code_unittest.py <directory_path>")
        sys.exit(1)
        
    directory_path = sys.argv[1]
    
    # Analyze test coverage
    results = analyze_test_coverage(directory_path)
    
    # Print pandas table
    print("\nTabulated Results:")
    print(results['dataframe'].to_string())