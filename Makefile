LATEX = pdflatex -interaction=nonstopmode -halt-on-error
TEX_TARGET = main
BIBTEX = bibtex
FIGURES = $(addprefix plots/,malloc.png array_malloc.png array_copy_memcpy.png array_copy_individually.png array_set.png array_get.png array_reverse.png array_free.png)

all: $(TEX_TARGET).pdf

plots/array_*.png: ./plots/array_plots.py
	python3 $<

plots/malloc.png: ./plots/comparing_malloc_performance.py
	python3 $<

main.pdf: $(TEX_TARGET).tex *.tex $(FIGURES)
	$(LATEX) $(TEX_TARGET)
	$(BIBTEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)
	$(LATEX) $(TEX_TARGET)

summary/summary.pdf: summary/summary.tex
	$(LATEX) $<
	$(BIBTEX) $<
	$(LATEX) $<
	$(LATEX) $<

clean:
	rm -f $(TEX_TARGET).pdf *.aux *.log *.out *.bbl *.blg

clean_figures:
	rm -f $(FIGURES)

.PHONY: clean clean_figures
	
