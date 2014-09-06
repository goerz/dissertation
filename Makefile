TEXFILES = $(shell find chapters frontmatter -regex ".*\.\(tex\)")
SUBDIRS = $(shell  find chapters -name "Makefile" | perl -pe 's/\/Makefile\n?/ /')

# We bootstrap the virtual environment with the system python. The Makefilels
# in the chapter subdirectory will then be passed the python executable from
# the virtual environment
PYTHON ?= python

all: diss.pdf

venv/bin/python: requirements.txt ./venv/bin/pip
	./venv/bin/pip install -r requirements.txt
	touch ./venv/bin/python

venv/bin/pip: ./scripts/prereqs.py
	@$(PYTHON) ./scripts/prereqs.py

update_venv:
	./venv/bin/pip uninstall GoerzDiss
	./venv/bin/pip uninstall QDYN
	./venv/bin/pip install -r requirements.txt

diss.pdf: diss.tex diss.bib mymacros.sty $(TEXFILES) $(SUBDIRS)
	@echo "Compiling Main File (via pdflatex)..."
	@latexmk -pdf -pdflatex="pdflatex -file-line-error -interaction=nonstopmode -halt-on-error" -use-make -silent diss.tex
	@echo ""
	@echo "LateX Warnings and Errors (check log file for details):"
	@echo ""
	@./scripts/ack "LaTeX Warning" *.log
	@echo ""
	@echo "Done"

update:
	@latexmk -pdf -pdflatex="pdflatex -file-line-error -interaction=nonstopmode -halt-on-error" -g -use-make -silent diss.tex

pdflatex:
	@pdflatex -file-line-error -interaction=nonstopmode -halt-on-error diss.tex

bibtex:
	@bibtex diss.aux

nodeps:
	pdflatex diss.tex
	bibtex diss.aux
	pdflatex diss.tex
	pdflatex diss.tex

dist: diss.pdf
	@make clean
	@mkdir -p dist/chapters
	@cp diss.* dist/
	@cp *.sty dist/
	@cp chapters/*.tex dist/chapters/
	@cp -r figures dist/
	@cp -r frontmatter dist/
	@echo "#!/bin/sh" > dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@echo "bibtex diss.aux"   >> dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@chmod a+x dist/compile.sh

rubber:
	@rm -f diss.pdf
	rubber --pdf -s diss.tex

$(SUBDIRS): ./venv/bin/python
	@echo "make $@"
	$(MAKE) PYTHON=$(shell [ -f `pwd`/venv/bin/python ] && echo `pwd`/venv/bin/python || echo python) -C $@
	@echo ""

figures: $(SUBDIRS)

CLEANSUBDIRS = $(SUBDIRS:%=clean-%)

$(CLEANSUBDIRS):
	@echo "$@"
	@$(MAKE) -C $(@:clean-%=%) clean
	@echo ""

figclean: $(CLEANSUBDIRS)

clean:
	@echo "Cleaning up files from LaTeX compilation ..."
	@latexmk -c -silent
	@rm -f .DS_Store
	@rm -f *.end *.aux *.log *.toc *.bbl *.brf *.blg *.out *.bak *.lof
	@rm -f *~
	@rm -f *.dvi
	@rm -f *.ps
	@rm -f .logged
	@rm -f *.preview.pdf
	@rm -f chapters/*.aux
	@rm -f figures/*-eps-converted-to.pdf
	@echo "Done"

distclean: clean $(CLEANSUBDIRS)
	@rm -f diss.pdf
	@rm -rf figures/*
	@rm -rf dist
	@rm -rf venv
	@rm -rf build

.PHONY: all update update_venv clean dist distclean bibtex rubber subdirs \
        $(SUBDIRS) $(CLEANSUBDIRS)
