import os
import random

# === CONFIGURABLE CONSTANTS ===
BANK_DIR = "Bank1"  # Directory containing problem .tex files
PROBLEM_PREFIX = "problem"  # Prefix for problem files
PROBLEM_SUFFIX = ".tex"  # Suffix for problem files
EXAM_TITLE = "Sample Exam"  # Title for main.tex
SOL_TITLE = "Sample Exam Solutions"  # Title for main_solutions.tex
AUTHOR = ""  # Author name (leave blank for none)
DATE = ""  # Date (leave blank for none)
MARGIN = "1in"  # Margin size for geometry package
HEADER = False  # If True, include author/date in header

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

def get_problem_files():
    files = [f for f in os.listdir(BANK_DIR) if f.startswith(PROBLEM_PREFIX) and f.endswith(PROBLEM_SUFFIX)]
    files.sort(key=lambda x: int(x[len(PROBLEM_PREFIX):-len(PROBLEM_SUFFIX)]))
    return files

def main():
    files = get_problem_files()
    n = int(input(f"How many problems to select (1-{len(files)})? "))
    if n > len(files) or n < 1:
        print(f"Please select a number between 1 and {len(files)}.")
        return
    selected = random.sample(files, n)
    # Add \vfill between problems for main.tex (questions only), including after the last
    questions = "\n\\vfill\n".join([f"    \\input{{{BANK_DIR}/{fname}}}" for fname in selected]) + "\n\\vfill\n"
    sol_questions = "\n".join([f"    \\input{{{BANK_DIR}/{fname}}}" for fname in selected])
    tex_content = EXAM_TEMPLATE.format(
        exam_title=EXAM_TITLE,
        author=AUTHOR,
        date=DATE,
        margin=MARGIN,
        questions=questions
    )
    sol_content = SOL_TEMPLATE.format(
        sol_title=SOL_TITLE,
        author=AUTHOR,
        date=DATE,
        margin=MARGIN,
        questions=sol_questions
    )
    with open("main.tex", "w") as f:
        f.write(tex_content)
    with open("main_solutions.tex", "w") as f:
        f.write(sol_content)
    print(f"main.tex and main_solutions.tex generated with {n} problems.")

if __name__ == "__main__":
    main()
