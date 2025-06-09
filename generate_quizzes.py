import os
import random

# === CONFIGURABLE CONSTANTS ===
BANK_DIRS = ["Bank1", "Bank2"]  # List of problem bank directories
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

def main():
    # Interactive random quiz generation
    print("Available banks:")
    for idx, bank_dir in enumerate(BANK_DIRS, 1):
        print(f"  {idx}: {bank_dir}")
    bank_choice = int(input(f"Select a bank by number (1-{len(BANK_DIRS)}): "))
    if not (1 <= bank_choice <= len(BANK_DIRS)):
        print("Invalid bank selection.")
        return
    bank_dir = BANK_DIRS[bank_choice - 1]
    files = get_problem_files(bank_dir)
    if not files:
        print(f"No problems found in {bank_dir}.")
        return
    n = int(input(f"How many problems to select (1-{len(files)})? "))
    if n > len(files) or n < 1:
        print(f"Please select a number between 1 and {len(files)}.")
        return
    selected = random.sample(files, n)
    questions = "\n\\vfill\n".join([f"    \\input{{{os.path.basename(fname)}}}" for fname in selected]) + "\n\\vfill\n"
    sol_questions = "\n".join([f"    \\input{{{os.path.basename(fname)}}}" for fname in selected])
    write_tex("random_quiz.tex", EXAM_TEMPLATE, questions, f"Random Quiz from {bank_dir}", AUTHOR, DATE, MARGIN, directory=bank_dir)
    write_tex("random_quiz_sol.tex", SOL_TEMPLATE, sol_questions, f"Random Quiz with Solutions from {bank_dir}", AUTHOR, DATE, MARGIN, directory=bank_dir)
    print(f"random_quiz.tex and random_quiz_sol.tex generated with {n} problems from {bank_dir} in {bank_dir}/.")

    # Per-bank generation
    for bank_dir in BANK_DIRS:
        files = get_problem_files(bank_dir)
        if not files:
            continue
        # Use only the filename for \input in per-bank .tex files
        questions = "\n\\vfill\n".join([f"    \\input{{{os.path.basename(fname)}}}" for fname in files]) + "\n\\vfill\n"
        sol_questions = "\n".join([f"    \\input{{{os.path.basename(fname)}}}" for fname in files])
        write_tex(f"{bank_dir}_all.tex", EXAM_TEMPLATE, questions, f"{bank_dir} Problems", AUTHOR, DATE, MARGIN, directory=bank_dir)
        write_tex(f"{bank_dir}_all_solutions.tex", SOL_TEMPLATE, sol_questions, f"{bank_dir} Problems with Solutions", AUTHOR, DATE, MARGIN, directory=bank_dir)
    # All banks combined
    all_files = []
    for bank_dir in BANK_DIRS:
        all_files.extend(get_problem_files(bank_dir))
    all_questions = "\n\\vfill\n".join([f"    \\input{{{os.path.dirname(fname)}/{os.path.basename(fname)}}}" for fname in all_files]) + "\n\\vfill\n"
    all_sol_questions = "\n".join([f"    \\input{{{os.path.dirname(fname)}/{os.path.basename(fname)}}}" for fname in all_files])
    write_tex("all_problems.tex", EXAM_TEMPLATE, all_questions, ALL_TITLE, AUTHOR, DATE, MARGIN)
    write_tex("all_problems_sol.tex", SOL_TEMPLATE, all_sol_questions, ALL_SOL_TITLE, AUTHOR, DATE, MARGIN)
    print("Generated .tex files for each bank (in their directory) and for all problems (in root).")

if __name__ == "__main__":
    main()
