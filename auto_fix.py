import ast
import sys

def fix_print_statements(code):
    """Fix missing parentheses in print statements for Python 2 → 3 compatibility."""
    lines = code.split("\n")
    fixed_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("print ") and "(" not in stripped:  # Fix `print 'Hello'`
            line = line.replace("print ", "print(", 1) + ")"
        fixed_lines.append(line)
    return "\n".join(fixed_lines)

def fix_missing_colons(code):
    """Detect missing colons in if, elif, else, for, while, and function/class definitions."""
    lines = code.split("\n")
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        if (
            (stripped.startswith(("if ", "elif ", "else", "for ", "while ", "def ", "class "))) 
            and not stripped.endswith(":")
        ):
            line += ":"  # Add missing colon
        fixed_lines.append(line)

    return "\n".join(fixed_lines)

def fix_code(code):
    """Apply all fixes (print statements + missing colons)."""
    code = fix_print_statements(code)
    code = fix_missing_colons(code)
    return code

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_fix.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r") as f:
            code = f.read()

        fixed_code = fix_code(code)

        with open(filename, "w") as f:  # Overwrite with fixed version
            f.write(fixed_code)

        print(f"✅ Fixed issues in {filename}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
