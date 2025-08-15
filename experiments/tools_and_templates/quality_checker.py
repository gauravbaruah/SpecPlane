#!/usr/bin/env python3
"""Basic quality checks for generated code"""

import os
import subprocess
from pathlib import Path

def check_python_syntax():
    """Check if Python files have valid syntax"""
    python_files = list(Path("specplane").glob("**/*.py"))
    
    print("🐍 Checking Python syntax...")
    for file in python_files:
        try:
            with open(file) as f:
                compile(f.read(), file, 'exec')
            print(f"  ✅ {file}")
        except SyntaxError as e:
            print(f"  ❌ {file}: {e}")

def check_imports():
    """Check if imports work"""
    print("\n📦 Checking imports...")
    try:
        result = subprocess.run(
            ["python", "-c", "import specplane"],
            cwd=".",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  ✅ Main package imports successfully")
        else:
            print(f"  ❌ Import error: {result.stderr}")
    except Exception as e:
        print(f"  ❌ Import check failed: {e}")

def count_files():
    """Count generated files"""
    py_files = len(list(Path("specplane").glob("**/*.py")))
    test_files = len(list(Path("tests").glob("**/*.py")))
    yaml_files = len(list(Path(".").glob("**/*.yaml")))
    
    print(f"\n📊 Files generated:")
    print(f"  Python files: {py_files}")
    print(f"  Test files: {test_files}")
    print(f"  YAML files: {yaml_files}")

if __name__ == "__main__":
    check_python_syntax()
    check_imports()
    count_files()