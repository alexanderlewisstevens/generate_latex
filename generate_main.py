import os
import random

BANK_DIR = "Bank1"
PROBLEM_PREFIX = "problem"
PROBLEM_SUFFIX = ".tex"

EXAM_TEMPLATE = r"""% main.tex - Auto-generated LaTeX file
\documentclass[addpoints]{{exam}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amssymb}}
\usepackage{{amsmath}}
\usepackage[margin=1in]{{geometry}}
\title{{Sample Exam}}
\author{{}}
\date{{}}

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
\usepackage[margin=1in]{{geometry}}
\title{{Sample Exam Solutions}}
\author{{}}
\date{{}}

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
    questions = "\n".join([f"    \\input{{{BANK_DIR}/{fname}}}" for fname in selected])
    tex_content = EXAM_TEMPLATE.format(questions=questions)
    sol_content = SOL_TEMPLATE.format(questions=questions)
    with open("main.tex", "w") as f:
        f.write(tex_content)
    with open("main_solutions.tex", "w") as f:
        f.write(sol_content)
    print(f"main.tex and main_solutions.tex generated with {n} problems.")

if __name__ == "__main__":
    main()
