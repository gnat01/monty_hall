.PHONY: all clean

all: monty_iv.pdf

monty_iv.pdf: monty_iv.tex
	pdflatex -interaction=nonstopmode monty_iv.tex
	pdflatex -interaction=nonstopmode monty_iv.tex

clean:
	rm -f monty_iv.aux monty_iv.log monty_iv.out monty_iv.pdf
