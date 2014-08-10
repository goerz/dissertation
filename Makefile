TEXFILES = $(shell find chapters frontmatter -regex ".*\.\(tex\)")
SUBDIRS = $(shell  find chapters -name "Makefile" | perl -pe 's/\/Makefile\n?/ /')

all: diss.pdf

diss.pdf: diss.tex diss.bib mymacros.sty $(TEXFILES) $(SUBDIRS)
	@echo "Compiling Main File (via pdflatex)..."
	@latexmk -pdf -pdflatex="pdflatex -file-line-error -interaction=nonstopmode -halt-on-error" -use-make -silent diss.tex
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
	@cp -r packages dist/
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

$(SUBDIRS):
	@echo "make $@"
	@$(MAKE) -C $@
	@echo ""

CLEANSUBDIRS = $(SUBDIRS:%=clean-%)

$(CLEANSUBDIRS):
	@echo "$@"
	@$(MAKE) -C $(@:clean-%=%) clean
	@echo ""

clean: $(CLEANSUBDIRS)
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

distclean: clean
	@rm -f diss.pdf
	@rm -rf figures/*
	@rm -rf dist

.PHONY: all update clean dist distclean bibtex rubber subdirs $(SUBDIRS) $(CLEANSUBDIRS)
