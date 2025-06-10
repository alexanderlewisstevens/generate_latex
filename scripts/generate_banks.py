import os
import random
import sys

# === CONFIGURABLE CONSTANTS ===
SRC_ROOT = "src"
BUILD_ROOT = "build"
BANKS_ROOT = os.path.join(SRC_ROOT, "banks")
BANK_DIRS = [os.path.join(BANKS_ROOT, "Bank1"), os.path.join(BANKS_ROOT, "Bank2")]
PROBLEM_PREFIX = "problem"
PROBLEM_SUFFIX = ".tex"
EXAM_TITLE = "Sample Exam"
SOL_TITLE = "Sample Exam Solutions"
ALL_TITLE = "All Problems"
ALL_SOL_TITLE = "All Problems with Solutions"
AUTHOR = ""
DATE = ""
MARGIN = "1in"

EXAM_TEMPLATE = r"""% main.tex - Auto-generated LaTeX file
\documentclass[addpoints]{{exam}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amssymb}}
\usepackage{{amsmath}}
\usepackage[margin={margin}]{{geometry}}
\title{{{exam_title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}
\maketitle

\section*{{Questions}}
\begin{{questions}}
{questions}
\end{{questions}}
\end{{document}}
"""

SOL_TEMPLATE = r"""% main_solutions.tex - Auto-generated LaTeX file
\documentclass[addpoints,answers]{{exam}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amssymb}}
\usepackage{{amsmath}}
\usepackage[margin={margin}]{{geometry}}
\title{{{sol_title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}
\maketitle

\section*{{Questions and Solutions}}
\begin{{questions}}
{questions}
\end{{questions}}
\end{{document}}
"""

def get_problem_files(bank_dir):
    files = [f for f in os.listdir(bank_dir) if f.startswith(PROBLEM_PREFIX) and f.endswith(PROBLEM_SUFFIX)]
    files.sort(key=lambda x: int(x[len(PROBLEM_PREFIX):-len(PROBLEM_SUFFIX)]))
    return [os.path.join(bank_dir, f) for f in files]

def write_tex(filename, template, questions, title, author, date, margin, directory=None):
    tex_content = template.format(
        exam_title=title,
        sol_title=title,
        author=author,
        date=date,
        margin=margin,
        questions=questions
    )
    if directory:
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, filename)
    with open(filename, "w") as f:
        f.write(tex_content)

def check_generated_files():
    """Check that all expected .tex files exist and are non-empty."""
    success = True
    missing = []
    empty = []
    # Per-bank files
    for bank_dir in BANK_DIRS:
        build_bank_dir = os.path.join(BUILD_ROOT, os.path.relpath(bank_dir, SRC_ROOT))
        for suffix in ["_all.tex", "_all_solutions.tex"]:
            fname = os.path.join(build_bank_dir, os.path.basename(bank_dir) + suffix)
            if not os.path.exists(fname):
                missing.append(fname)
                success = False
            elif os.path.getsize(fname) == 0:
                empty.append(fname)
                success = False
    # Combined files
    for fname in [os.path.join(BUILD_ROOT, "all_problems.tex"), os.path.join(BUILD_ROOT, "all_problems_sol.tex")]:
        if not os.path.exists(fname):
            missing.append(fname)
            success = False
        elif os.path.getsize(fname) == 0:
            empty.append(fname)
            success = False
    return success, missing, empty

def main():
    # Per-bank generation
    for bank_dir in BANK_DIRS:
        files = get_problem_files(bank_dir)
        if not files:
            continue
        build_bank_dir = os.path.join(BUILD_ROOT, os.path.relpath(bank_dir, SRC_ROOT))
        # Use correct relative path for \input in per-bank .tex files
        questions = "\n\\vfill\n".join([
            f"    \\input{{{os.path.relpath(fname, build_bank_dir)}}}" for fname in files
        ]) + "\n\\vfill\n"
        sol_questions = "\n".join([
            f"    \\input{{{os.path.relpath(fname, build_bank_dir)}}}" for fname in files
        ])
        write_tex(f"{os.path.basename(bank_dir)}_all.tex", EXAM_TEMPLATE, questions, f"{os.path.basename(bank_dir)} Problems", AUTHOR, DATE, MARGIN, directory=build_bank_dir)
        write_tex(f"{os.path.basename(bank_dir)}_all_solutions.tex", SOL_TEMPLATE, sol_questions, f"{os.path.basename(bank_dir)} Problems with Solutions", AUTHOR, DATE, MARGIN, directory=build_bank_dir)
    # All banks combined
    all_files = []
    for bank_dir in BANK_DIRS:
        all_files.extend(get_problem_files(bank_dir))
    # Use correct relative path for \input in combined .tex files
    build_dir = BUILD_ROOT
    all_questions = "\n\\vfill\n".join([
        f"    \\input{{{os.path.relpath(fname, build_dir)}}}" for fname in all_files
    ]) + "\n\\vfill\n"
    all_sol_questions = "\n".join([
        f"    \\input{{{os.path.relpath(fname, build_dir)}}}" for fname in all_files
    ])
    write_tex(os.path.join(BUILD_ROOT, "all_problems.tex"), EXAM_TEMPLATE, all_questions, ALL_TITLE, AUTHOR, DATE, MARGIN)
    write_tex(os.path.join(BUILD_ROOT, "all_problems_sol.tex"), SOL_TEMPLATE, all_sol_questions, ALL_SOL_TITLE, AUTHOR, DATE, MARGIN)
    print("Generated .tex files for each bank (in build/) and for all problems (in build/).")

    # If --test flag is present, run checks
    if "--test" in sys.argv:
        success, missing, empty = check_generated_files()
        if success:
            print("[TEST] All expected .tex files exist and are non-empty.")
            sys.exit(0)
        else:
            if missing:
                print("[TEST] Missing files:", *missing, sep="\n  ")
            if empty:
                print("[TEST] Empty files:", *empty, sep="\n  ")
            sys.exit(1)

if __name__ == "__main__":
    main()
