TEXFILES = $(shell find chapters frontmatter -regex ".*\.\(tex\)")
SUBDIRS = $(shell  find chapters -name "Makefile" | perl -pe 's/\/Makefile\n?/ /')

# We bootstrap the virtual environment with the system python. The Makefilels
# in the chapter subdirectory will then be passed the python executable from
# the virtual environment
PYTHON ?= python

PDFLATEXOPTS = -file-line-error -interaction=nonstopmode -halt-on-error -synctex=1

all: diss.pdf diss_letter.pdf diss_web_a4.pdf diss_web_letter.pdf

venv/bin/python: ./venv/bin/pip
	./venv/bin/pip install "numpy>=1.9.0"
	./venv/bin/pip install "matplotlib>=1.4.0"
	./venv/bin/pip install "ipython>=3.0.0"
	./venv/bin/pip install "scipy>=0.15.0"
	./venv/bin/pip install "sympy>=0.7.6"
	./venv/bin/pip install "QDYN==0.1.0"
	./venv/bin/pip install "mgplottools==1.0.0"
	./venv/bin/pip install "xmgrace_parser==1.0.1"
	./venv/bin/pip install -I git+git://github.com/goerz/QDYNTransmonLib@321aab5ebd2fc779fd3fa829703e9c76aeb27d68#egg=QDYNTransmonLib
	touch ./venv/bin/python

venv/bin/pip: ./scripts/prereqs.py
	@$(PYTHON) ./scripts/prereqs.py

update_venv:
	yes | ./venv/bin/pip uninstall mgplottools || true
	yes | ./venv/bin/pip uninstall xmgrace_parser || true
	yes | ./venv/bin/pip uninstall QDYN || true
	yes | ./venv/bin/pip uninstall QDYNTransmonLib || true
	./venv/bin/pip install "QDYN==0.1.0"
	./venv/bin/pip install "mgplottools==1.0.0"
	./venv/bin/pip install "xmgrace_parser==1.0.1"
	./venv/bin/pip install -I git+git://github.com/goerz/QDYNTransmonLib@321aab5ebd2fc779fd3fa829703e9c76aeb27d68#egg=QDYNTransmonLib

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

diss_letter.pdf: diss.pdf
	@make dist
	@rm -rf diss_letter
	@cp -r dist diss_letter
	@perl -p -i -e 's/210mm/8.5in/' diss_letter/diss.cls
	@perl -p -i -e 's/297mm/11in/' diss_letter/diss.cls
	@cd diss_letter && ./compile.sh && cp diss.pdf ../diss_letter.pdf
	@rm -rf diss_letter

diss_web_a4.pdf: diss_letter.pdf
	@rm -rf diss_web_a4
	@cp -r dist diss_web_a4
	@perl -p -i -e 's/\\bindingoffset\}\{0.8cm\}/\\bindingoffset}{0.0pt}/' diss_web_a4/diss.cls
	@perl -p -i -e 's/\\setlength\{\\innermargin\}\{\(\\paperwidth-\\textwidth-\\bindingoffset\)\/3\}/\\setlength{\\innermargin}{(\\paperwidth-\\textwidth-\\bindingoffset)\/2}/' diss_web_a4/diss.cls
	@cd diss_web_a4 && ./compile.sh && cp diss.pdf ../diss_web_a4.pdf
	@rm -rf diss_web_a4

diss_web_letter.pdf: diss_web_a4.pdf
	@rm -rf diss_web_letter
	@cp -r dist diss_web_letter
	@perl -p -i -e 's/210mm/8.5in/' diss_web_letter/diss.cls
	@perl -p -i -e 's/297mm/11in/' diss_web_letter/diss.cls
	@perl -p -i -e 's/\\bindingoffset\}\{0.8cm\}/\\bindingoffset}{0.0pt}/' diss_web_letter/diss.cls
	@perl -p -i -e 's/\\setlength\{\\innermargin\}\{\(\\paperwidth-\\textwidth-\\bindingoffset\)\/3\}/\\setlength{\\innermargin}{(\\paperwidth-\\textwidth-\\bindingoffset)\/2}/' diss_web_letter/diss.cls
	@cd diss_web_letter && ./compile.sh && cp diss.pdf ../diss_web_letter.pdf
	@rm -rf diss_web_letter

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

makedistmsg:
	@echo ""
	@echo "*** Creating distribution in ./dist ***"
	@echo ""

dist: diss.pdf makedistmsg
	@if [ ! -e diss.log ]; then pdflatex diss.tex;fi
	@rm  -rf dist
	@mkdir -p dist/figures
	cp `LC_ALL=C sed -n 's/^File:\(.*\)Graphic file.*/\1/p' diss.log` ./dist/figures/
	@mkdir -p dist/chapters
	cp diss.bib diss.bst diss.cls diss.tex dist/
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
	@rm -f *.synctex.*
	@rm -f .logged
	@rm -f *.preview.pdf
	@rm -f chapters/*.aux
	@rm -f chapters/*.lst
	@rm -f figures/*-eps-converted-to.pdf
	@rm -rf diss_letter
	@rm -rf diss_web_a4
	@rm -rf diss_web_letter
	@echo "Done"

distclean: clean $(CLEANSUBDIRS)
	@rm -f diss.pdf
	@rm -f diss_letter.pdf
	@rm -f diss_web_a4.pdf
	@rm -f diss_web_letter.pdf
	@rm -rf figures/*
	@rm -rf chapters/labels.lst
	@rm -rf chapters/bibkeys.lst
	@rm -rf dist
	@rm -rf venv
	@rm -rf build

.PHONY: all update update_venv clean dist distclean bibtex rubber subdirs \
$(SUBDIRS) $(CLEANSUBDIRS) $(DISTSUBDIRS) figclean \
makefigsmsg makedissmsg makedistmsg
