TEXFILES = $(shell find chapters frontmatter -regex ".*\.\(tex\)")
SUBDIRS = $(shell  find chapters -name "Makefile" | perl -pe 's/\/Makefile\n?/ /')

# We bootstrap the virtual environment with the system python. The Makefilels
# in the chapter subdirectory will then be passed the python executable from
# the virtual environment
PYTHON ?= python

PDFLATEXOPTS = -file-line-error -interaction=nonstopmode -halt-on-error

all: diss.pdf

venv/bin/python: ./venv/bin/pip
	./venv/bin/pip install "numpy>=1.8.0"
	./venv/bin/pip install "matplotlib>=1.3.1"
	./venv/bin/pip install "ipython>=2.0.0"
	./venv/bin/pip install "scipy>=0.14.0"
	./venv/bin/pip install -I git+https://github.com/goerz/qdynpylib.git#egg=QDYN
	./venv/bin/pip install -I git+https://github.com/goerz/mgplottools.git#egg=mgplottools
	./venv/bin/pip install -I xmgrace_parser
	touch ./venv/bin/python

venv/bin/pip: ./scripts/prereqs.py
	@$(PYTHON) ./scripts/prereqs.py

update_venv:
	yes | ./venv/bin/pip uninstall mgplottools || true
	yes | ./venv/bin/pip uninstall xmgrace_parser || true
	yes | ./venv/bin/pip uninstall QDYN || true
	./venv/bin/pip install git+https://github.com/goerz/qdynpylib.git#egg=QDYN
	./venv/bin/pip install git+https://github.com/goerz/mgplottools.git#egg=mgplottools
	./venv/bin/pip install xmgrace_parser

labels.lst: $(TEXFILES)
	./scripts/extract_labels.pl $(TEXFILES) > labels.lst
	@rm -f chapters/labels.lst
	ln -s labels.lst chapters/labels.lst

bibkeys.lst: diss.bib
	./scripts/extract_bibkeys.pl diss.bib > bibkeys.lst
	@rm -f chapters/bikeys.lst
	ln -s bibkeys.lst chapters/bikeys.lst

makefigsmsg:
	@echo "Compiling all figures"
	@echo ""

makedissmsg:
	@echo ""
	@echo "*** make diss.pdf ***"
	@echo ""

diss.pdf: makedissmsg \
diss.tex diss.bib diss.cls mymacros.sty bibkeys.lst labels.lst $(TEXFILES) \
makefigsmsg $(SUBDIRS)
	@echo "Done with figures"
	@echo ""
	@echo "** Compiling diss.pdf (via latexmk)..."
	@latexmk -pdf -pdflatex="pdflatex $(PDFLATEXOPTS)" -use-make -silent diss.tex
	@echo "** Done with latexmk"
	@echo ""
	@echo "*******************************************************"
	@echo "LateX Warnings and Errors (check log file for details):"
	@echo "*******************************************************"
	@echo ""
	@./scripts/ack --nocolor "^(\(\./chapters/\w+\.tex|.* Warning:)" diss.log
	@echo ""
	@echo "*** Done with diss.pdf ***"
	@echo ""

update:
	@echo "** Compiling diss.pdf (via latexmk)..."
	@latexmk -pdf -pdflatex="pdflatex $(PDFLATEXOPTS)" -g -use-make -silent diss.tex
	@echo "** Done with latexmk"

pdflatex:
	@echo "** Compiling diss.pdf (via pdflatex)..."
	@pdflatex $(PDFLATEXOPTS) diss.tex
	@echo "** Done with pdflatex"

bibtex:
	@bibtex diss.aux

nodeps:
	pdflatex diss.tex
	bibtex diss.aux
	pdflatex diss.tex
	pdflatex diss.tex
	makeindex -s iso.ist diss
	pdflatex diss.tex


$(SUBDIRS): ./venv/bin/python
	$(MAKE) PYTHON=$(shell [ -f `pwd`/venv/bin/python ] && echo `pwd`/venv/bin/python || echo python) -C $@ all
	@echo ""

figures: $(SUBDIRS)


DISTSUBDIRS = $(SUBDIRS:%=dist-%)

$(DISTSUBDIRS): $(SUBDIRS)
	$(MAKE) -C $(@:dist-%=%) dist
	@echo ""

makedistmsg:
	@echo ""
	@echo "*** Creating distribution in ./dist ***"
	@echo ""

dist: diss.pdf makedistmsg $(DISTSUBDIRS)
	make clean
	@mkdir -p dist/chapters
	cp diss.* dist/
	cp *.sty dist/
	cp *.ist dist/
	cp chapters/*.tex dist/chapters/
	cp -r frontmatter dist/
	@echo "#!/bin/sh" > dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@echo "bibtex diss.aux"   >> dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@echo "makeindex -s iso.ist diss" >> dist/compile.sh
	@echo "pdflatex diss.tex" >> dist/compile.sh
	@chmod a+x dist/compile.sh
	@echo ""
	@echo "*** Done ***"
	@echo ""

rubber:
	@echo "** Compiling diss.pdf (via rubber)..."
	rubber --pdf -s diss.tex
	@echo "** Done with rubber"


CLEANSUBDIRS = $(SUBDIRS:%=clean-%)

$(CLEANSUBDIRS):
	$(MAKE) -C $(@:clean-%=%) clean
	@echo ""

figclean: $(CLEANSUBDIRS)

clean:
	@echo "Cleaning up files from LaTeX compilation ..."
	@latexmk -c -silent
	@rm -f .DS_Store
	@rm -f *.end *.aux *.log *.toc *.bbl *.brf *.blg *.out *.bak *.lof
	@rm -f *~
	@rm -f *.fls
	@rm -f *.dvi
	@rm -f *.ps
	@rm -f *.lst
	@rm -f .logged
	@rm -f *.preview.pdf
	@rm -f chapters/*.aux
	@rm -f chapters/*.lst
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
$(SUBDIRS) $(CLEANSUBDIRS) $(DISTSUBDIRS) figclean \
makefigsmsg makedissmsg makedistmsg
