import ast
import sys
import subprocess
import os
import re

def fix_print_statements(file_path):
    """
    Fix missing parentheses in Python 2-style print statements.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    try:
        ast.parse(source_code)
        return False  # No SyntaxError, no fix needed
    except SyntaxError as e:
        if "Missing parentheses in call to 'print'" in str(e):
            print(f"🔧 Fixing print statement in: {file_path}")
            fixed_code = re.sub(r"(?<=\bprint) (.+)", r"(\1)", source_code)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(fixed_code)
            return True
        return False


def fix_missing_colons(file_path):
    """
    Detects and adds missing colons (:) for control structures.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    updated_lines = []
    fixed = False
    pattern = r"^\s*(if|elif|else|for|while|def|class)\b.*(?!:)\s*$"

    for line in lines:
        if re.match(pattern, line):
            print(f"🔧 Adding missing colon in: {line.strip()}")
            line = line.rstrip() + ":\n"
            fixed = True
        updated_lines.append(line)

    if fixed:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)

    return fixed


def format_code_with_black(file_path):
    """
    Format the Python file using Black (PEP8 autoformatter).
    """
    print(f"🖋 Formatting {file_path} with Black...")
    subprocess.run(["black", file_path], check=True)


def run_security_check(file_path):
    """
    Run a security scan using Bandit.
    """
    print(f"🔍 Running security check on {file_path}...")
    result = subprocess.run(["bandit", "-r", file_path], capture_output=True, text=True)
    print(result.stdout)
    return "No issues" in result.stdout


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_print.py <file1.py> <file2.py> ...")
        sys.exit(1)

    files = sys.argv[1:]
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠ File not found: {file_path}")
            continue

        print(f"🚀 Processing {file_path}...")

        # Step 1: Fix print statements if needed
        fixed_prints = fix_print_statements(file_path)

        # Step 2: Fix missing colons
        fixed_colons = fix_missing_colons(file_path)

        # Step 3: Format code with Black
        format_code_with_black(file_path)

        # Step 4: Run security check
        security_passed = run_security_check(file_path)

        if fixed_prints:
            print(f"✅ {file_path}: Print statements fixed.")
        if fixed_colons:
            print(f"✅ {file_path}: Missing colons fixed.")
        if security_passed:
            print(f"✅ {file_path}: No security issues found.")
        else:
            print(f"⚠ {file_path}: Security issues detected! Please review.")

    print("🎯 Auto-fix process completed.")

if __name__ == "__main__":
    main()
