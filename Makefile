LATEX = pdflatex
TEX_TARGET = main
BIBTEX = bibtex
FIGURES = plots/malloc.png

all: $(TEX_TARGET).pdf

plots/malloc.png: ./plots/comparing_malloc_performance.py
	python3 $<

main.pdf: $(TEX_TARGET).tex *.tex $(FIGURES)
	$(LATEX) $(TEX_TARGET).tex

bib: 
	$(LATEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)
	$(BIBTEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)

clean:
	rm -f $(TEX_TARGET).pdf *.aux *.log *.out *.bbl *.blg

clean_figures:
	rm -f $(FIGURES)

.PHONY: clean clean_figures
	

