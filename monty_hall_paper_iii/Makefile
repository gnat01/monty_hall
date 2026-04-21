.PHONY: all figures clean

all: monty_iii.pdf

figures:
	mkdir -p .mplconfig
	MPLCONFIGDIR=.mplconfig python generate_plots.py

monty_iii.pdf: monty_iii.tex figures
	pdflatex -interaction=nonstopmode monty_iii.tex
	pdflatex -interaction=nonstopmode monty_iii.tex

clean:
	rm -f monty_iii.aux monty_iii.log monty_iii.out monty_iii.pdf
