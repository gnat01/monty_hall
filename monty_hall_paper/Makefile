.PHONY: all figures clean

all: monty.pdf

figures:
	mkdir -p .mplconfig
	MPLCONFIGDIR=.mplconfig python generate_plots_with_multik.py

monty.pdf: monty.tex figures
	pdflatex -interaction=nonstopmode monty.tex
	pdflatex -interaction=nonstopmode monty.tex

clean:
	rm -f monty.aux monty.log monty.out monty.pdf
