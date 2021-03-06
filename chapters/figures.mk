# Rules to be used by the image makefiles in chapter subfolders
#
# The IMG variable must be defined before including this file, and contain the
# names of images that are generated by MAKE
#
# The IMG2 variable may further list files that are are not generated from
# other files but should be copied directly

# PYTHON will be exported from the main Makefile, and generally be the python
# executable set up in the 'venv' virtual environment
PYTHON ?= $(shell [ -f ../../venv/bin/python ] && echo ../../venv/bin/python || echo python)

.DEFAULT_GOAL = all
all: $(IMG)

diss.cls: ../../diss.cls
	@cp ../../diss.cls diss.cls

mymacros.sty: ../../mymacros.sty
	@cp ../../mymacros.sty mymacros.sty

matplotlibrc: ../../matplotlibrc
	@cp ../../matplotlibrc matplotlibrc

%.pdf: %.tex diss.cls mymacros.sty
	@echo "\n** generate figure: $< -> $@"
	@latexmk -pdf -pdflatex="pdflatex -file-line-error -interaction=nonstopmode -halt-on-error" -use-make -silent $<

# Rule for agr -> pdf if xmgrace supports PDF output
%.pdf: %.agr
	@echo "\n** generate figure: $< -> $@"
	@$(PYTHON) ../../venv/bin/xmgrace_parser --hardcopy $@ $<

# In case your xmgrace version does not have support of PDF output, use this
# alternative rule
#%.pdf: %.agr
#	@echo "\n** generate figure: $< -> $@"
#	@$(PYTHON) ../../venv/bin/xmgrace_parser --hardcopy $*.eps $< && epstopdf $*.eps
#	@rm -f $*.eps


# Rule for matplotlib py -> pdf
%.pdf: %.py matplotlibrc
	@echo "\n** generate figure: $< -> $@"
	@$(PYTHON) $<


# Rule for matplotlib py -> png
%.png: %.py matplotlibrc
	@echo "** generate figure: $< -> $@"
	@$(PYTHON) $<


clean-auto:
	@rm -f *.end
	@rm -f *.aux
	@rm -f *.log
	@rm -f *.toc
	@rm -f *.bbl
	@rm -f *.blg
	@rm -f *.out
	@rm -f *.bak
	@rm -f *.lof
	@rm -f *.fdb_latexmk
	@rm -f *.fls
	@rm -f *~
	@rm -f *.dvi
	@rm -f *.ps
	@rm -f *.preview.pdf
	rm -f $(IMG)
	@rm -f diss.cls mymacros.sty
	@rm -f matplotlibrc
