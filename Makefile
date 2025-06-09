# Makefile for generating PDF and Markdown from LaTeX

TEX_SRC ?= main.tex
PDF_OUT ?= $(TEX_SRC:.tex=.pdf)
MD_OUT ?= $(TEX_SRC:.tex=.md)

all: pdf md

pdf:
	pdflatex -interaction=nonstopmode $(TEX_SRC)

md:
	pandoc $(TEX_SRC) -o $(MD_OUT)

clean:
	rm -f *.aux *.log *.out *.pdf *.md
