#!/usr/bin/env python
"""
Test the environment for compilation of the thesis, write requirements.txt with
missing python packages
"""
import os
import sys
from textwrap import dedent

def which(program):
    """ Return the absolute path of the given program, or None if the program
        is not available -- like Unix which utility)
    """
    def is_exe(fpath):
        """Is fpath an executable?"""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


required_execs = ['xmgrace', 'pdflatex', 'latexmk', 'perl']

for exe in required_execs:
    if which(exe) is None:
        print "%s is required for compilation" % exe
        sys.exit(1)


# Create virtual environment
if not os.path.isdir("venv"):
    print dedent("""
    We will install a virtual python environment in the venv folder based on
    %s.
    This environment will be used for generating graphics.

    It is strongly recommended that the base python includes the SciPy stack
    (such as Enthought Canopy <https://www.enthought.com/products/canopy/>),
    with recent versions of numpy, scipy, matplotlib and ipython. If those
    packages are not up to date, they will be installed from source in the
    virtual environment. This will involve long and tedious compilation and can
    easily fail, e.g. if you don't have gfortran installed.

    Press Enter to continue, CTRL-C to abort.
    """ % sys.executable)
    raw_input()
    import logging
    logging.basicConfig()
    try:
        from canopy.app.venv_cli import main as venv
        print "Using canopy venv"
        venv(args=['-s', './venv'])
    except ImportError:
        print "Using canopy venv"
        sys.path.insert(0, "./scripts/virtualenv")
        from virtualenv import main as venv
        venv(argv=['--system-site-packages', './venv'])
