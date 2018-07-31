LATEX = pdflatex
TEX_TARGET = main
BIBTEX = bibtex

all: $(TEX_TARGET).pdf

malloc.png: ~/data/comparing_malloc_performance.py ~/data/graph_2d.py
	cd ~/data && python3 comparing_malloc_performance.py
	mv ~/data/malloc.png ./

main.pdf: $(TEX_TARGET).tex *.tex
	$(LATEX) $(TEX_TARGET).tex

bib: 
	$(LATEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)
	$(BIBTEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)

clean:
	rm -f $(TEX_TARGET).pdf *.aux *.log *.out *.bbl *.blg

.PHONY: clean
	

