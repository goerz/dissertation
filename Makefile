TEXFILES = $(shell find chapters frontmatter -regex ".*\.\(tex\)")
SUBDIRS = $(shell  find chapters -name "Makefile" | perl -pe 's/\/Makefile\n?/ /')

# We bootstrap the virtual environment with the system python. The Makefilels
# in the chapter subdirectory will then be passed the python executable from
# the virtual environment
PYTHON ?= python

all: diss.pdf

venv/bin/python: ./venv/bin/pip
	./venv/bin/pip install "numpy>=1.8.0"
	./venv/bin/pip install "matplotlib>=1.3.1"
	./venv/bin/pip install "ipython>=2.0.0"
	./venv/bin/pip install "scipy>=0.14.0"
	./venv/bin/pip install -I git+https://github.com/goerz/qdynpylib.git#egg=QDYN
	./venv/bin/pip install -I mgplottools
	./venv/bin/pip install -I xmgrace_parser
	touch ./venv/bin/python

venv/bin/pip: ./scripts/prereqs.py
	@$(PYTHON) ./scripts/prereqs.py

update_venv:
	yes | ./venv/bin/pip uninstall mgplottools || true
	yes | ./venv/bin/pip uninstall xmgrace_parser || true
	yes | ./venv/bin/pip uninstall QDYN || true
	./venv/bin/pip install git+https://github.com/goerz/qdynpylib.git#egg=QDYN
	./venv/bin/pip install mgplottools
	./venv/bin/pip install xmgrace_parser

chapters/labels.lst: $(TEXFILES)
	./scripts/extract_labels.pl $(TEXFILES) > chapters/labels.lst

chapters/bibkeys.lst: diss.bib
	./scripts/extract_bibkeys.pl diss.bib > chapters/bibkeys.lst

diss.pdf: diss.tex diss.bib diss.cls mymacros.sty chapters/bibkeys.lst chapters/labels.lst $(TEXFILES) $(SUBDIRS)
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

dist: diss.pdf $(DISTSUBDIRS)
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

DISTSUBDIRS = $(SUBDIRS:%=dist-%)

$(DISTSUBDIRS): $(SUBDIRS)
	@echo "$@"
	@$(MAKE) -C $(@:dist-%=%) clean
	@echo ""

clean:
	@echo "Cleaning up files from LaTeX compilation ..."
	@latexmk -c -silent
	@rm -f .DS_Store
	@rm -f *.end *.aux *.log *.toc *.bbl *.brf *.blg *.out *.bak *.lof
	@rm -f *~
	@rm -f *.fls
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
	@rm -rf chapters/labels.lst
	@rm -rf chapters/bibkeys.lst
	@rm -rf dist
	@rm -rf venv
	@rm -rf build

.PHONY: all update update_venv clean dist distclean bibtex rubber subdirs \
        $(SUBDIRS) $(CLEANSUBDIRS)
