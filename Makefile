# Makefile for generating PDF and Markdown from LaTeX
#
# Usage:
#   make pdf      # Generate PDF from main.tex using pdflatex
#   make md       # Generate Markdown from main.tex using pandoc
#   make all      # Generate both PDF and Markdown
#   make clean    # Remove all generated files
#
# Variables:
#   TEX_SRC:   Source LaTeX file (default: main.tex)
#   PDF_OUT:   Output PDF file (default: main.pdf)
#   MD_OUT:    Output Markdown file (default: main.md)

TEX_SRC ?= main.tex           # LaTeX source file
PDF_OUT ?= $(TEX_SRC:.tex=.pdf) # PDF output file
MD_OUT ?= $(TEX_SRC:.tex=.md)   # Markdown output file

all: pdf md                   # Build both PDF and Markdown

gen:                          # Generate main.tex from Bank1 using Python script
	python3 generate_main.py

pdf: gen                      # Generate PDF from LaTeX (after generating main.tex)
	pdflatex -interaction=nonstopmode $(TEX_SRC)

md: gen                       # Generate Markdown from LaTeX (after generating main.tex)
	pandoc $(TEX_SRC) -o $(MD_OUT)

clean:                        # Remove generated files
	find . -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.pdf' -o -name '*.md' -o -name '*.toc' -o -name '*.synctex.gz' -o -name 'random_quiz.tex' -o -name 'random_quiz_sol.tex' -o -name '*_all.tex' -o -name '*_all_solutions.tex' -o -name 'all_problems.tex' -o -name 'all_problems_sol.tex' -o -name 'main.tex' -o -name 'main_solutions.tex' \) -delete
