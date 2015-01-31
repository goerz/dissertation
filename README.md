## Prerequisites ##

*   Complete TeX installation (tested with TeXLive 2014).
    Note: TeXLive 2013 does *not* work (bug in TOC font).
*   latexmk, dvipng (should be part of your TeX distribution)
*   Perl (tested with v5.16.2)
*   Python 2.7, with scientific stack (IPython, numpy, scipy, sympy, matplotib;
    see Makefile for details)
    Using a Python distribution such as Enthought Canopy or Anaconda is strongly
    recommended.
*   Ghostscript 7.07 or later
*   Grace 5.1.22.
    Your version of grace must have support for generating PDF files. If it
    doesn't, you can try to modify the rule in `chapters/figures.mk` to get PDF
    files via EPS

A virtual Python environment will be created in the `venv` subfolder, containing
the above packages, as well as some of the additional Python packages from the
`scripts` folder that are necessary for generating the figures.

## Compilation ##

Run `make` to compile all figures from source, and to compile
`diss.pdf` from all `tex` files.

`make clean` removes all temporary files, but leaves `diss.pdf` and any
generated figures, as well as the `venv` subdirectory intact.

`make distclean` restores to a clean checkout. It deletes all generated figures,
and the `venv` subfolder.

Note that once all figures have been generated, `diss.pdf` can be compiled with
minimal dependencies (i.e. only a simple TeX installation). Running `make dist`
will create a copy of the minimal files (`tex` files, `template`, and `figures`
folder) to the `dist` subfolder, for archival purposes.
