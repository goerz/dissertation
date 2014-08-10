## Prerequisites ##

*   Complete TeX installation (tested with TeXLive 2012-2014)
*   latexmk (should be part of your TeX distribution)
*   perl (tested with v5.16.2)
*   python 2.7, with scientific stack.
      *   IPython 2.0.0
      *   matplotlib 1.3.1
      *   scipy 0.14.0
      *   numpy 1.8.0
* Grace 5.1.22

## Compilation ##

Run `make` to assemble all figures in the `figures` subfolder, and to compile
`diss.pdf` from all `tex` files.

`make clean` removes all temporary files, but leaves `diss.pdf` and the contents
of the `figures` subdirectory intact.

`make distclean` removes `dissp.pdf` and the contents of `figures` as well.

Note that once all figures have been assembled in the `figures` subfolder,
`diss.pdf` can be compiled with minimal dependencies (i.e. only a simple TeX
installation). Running `make dist` will create a copy of the minimal files
(`tex` files, `template`, and `figures` folder) to the `dist` subfolder, for
archival purposes.
