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

pdf:                          # Generate PDF from LaTeX
	pdflatex -interaction=nonstopmode $(TEX_SRC)

md:                           # Generate Markdown from LaTeX
	pandoc $(TEX_SRC) -o $(MD_OUT)

clean:                        # Remove generated files
	rm -f *.aux *.log *.out *.pdf *.md
