.PHONY: all figures clean

all: monty_ii.pdf

figures:
	mkdir -p .mplconfig
	MPLCONFIGDIR=.mplconfig python generate_plots.py

monty_ii.pdf: monty_ii.tex figures
	pdflatex -interaction=nonstopmode monty_ii.tex
	pdflatex -interaction=nonstopmode monty_ii.tex

clean:
	rm -f monty_ii.aux monty_ii.log monty_ii.out monty_ii.pdf
