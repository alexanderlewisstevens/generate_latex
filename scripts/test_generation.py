#!/usr/bin/env python3
"""
Test script for LaTeX exam/quiz generation workflow.
Checks:
- All expected .tex files are generated and non-empty
- All generated .tex files compile without errors (using pdflatex)
"""
import os
import subprocess
import sys

BUILD_ROOT = "build"
BANKS = ["Bank1", "Bank2"]

# List of expected generated files (relative to workspace root)
EXPECTED_FILES = [
    os.path.join(BUILD_ROOT, "all_problems.tex"),
    os.path.join(BUILD_ROOT, "all_problems_sol.tex"),
]
for bank in BANKS:
    bank_dir = os.path.join(BUILD_ROOT, "banks", bank)
    EXPECTED_FILES.append(os.path.join(bank_dir, f"{bank}_all.tex"))
    EXPECTED_FILES.append(os.path.join(bank_dir, f"{bank}_all_solutions.tex"))

def run_pdflatex(tex_path, workdir):
    """Run pdflatex in nonstopmode, return (success, output)"""
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", os.path.basename(tex_path)],
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
            encoding="utf-8"
        )
        success = (result.returncode == 0 and "! LaTeX Error" not in result.stdout)
        return success, result.stdout
    except Exception as e:
        return False, str(e)

def main():
    # 1. Run the generation script(s)
    print("[TEST] Running generate_all_banks_tex.py...")
    ret = subprocess.run(["python3", "scripts/generate_all_banks_tex.py"])
    if ret.returncode != 0:
        print("[FAIL] generate_all_banks_tex.py failed.")
        sys.exit(1)

    # 2. Check for expected files
    missing = [f for f in EXPECTED_FILES if not os.path.isfile(f)]
    if missing:
        print("[FAIL] Missing generated files:")
        for f in missing:
            print("   ", f)
        sys.exit(1)
    print("[TEST] All expected .tex files found.")

    # 3. Check files are non-empty
    empty = [f for f in EXPECTED_FILES if os.path.getsize(f) == 0]
    if empty:
        print("[FAIL] Empty generated files:")
        for f in empty:
            print("   ", f)
        sys.exit(1)
    print("[TEST] All generated .tex files are non-empty.")

    # 4. Try to compile each .tex file
    failed = []
    for texfile in EXPECTED_FILES:
        workdir = os.path.dirname(os.path.abspath(texfile))
        print(f"[TEST] Compiling {texfile} ...", end=" ")
        success, output = run_pdflatex(texfile, workdir)
        if not success:
            print("FAIL")
            failed.append((texfile, output))
        else:
            print("OK")
    if failed:
        print("[FAIL] Some .tex files failed to compile:")
        for texfile, output in failed:
            print(f"--- {texfile} ---\n{output}\n--- END ---\n")
        sys.exit(1)
    print("[PASS] All generated .tex files compile successfully.")

if __name__ == "__main__":
    main()
