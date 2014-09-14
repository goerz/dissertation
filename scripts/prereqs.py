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
    You must create a Python virtual environment in the folder ./venv before
    continuing.

    If at all possible, use a binary python installation such as Enthought
    Canopy <https://www.enthought.com/products/canopy/>, and install the
    standard scientific stack (numpy, matplotlib, scipy, ipython) into the
    virtual environment before continuing.

    Assuming you have Enthought Canopy installed, you should be able to do the
    following:

        canopy_cli venv ./venv
        ./venv/bin/enpkg nose mock numpy matplotlib scipy ipython

    If you don't do this, we will attempt to install all packages, including
    the scientific stack, from source. This is likely to fail (since packages
    like scipy require tons of C++/Fortran compilations, and you might not have
    the right compilers)

    For general information about python virtual environment, consult
    <https://virtualenv.pypa.io/en/latest/>

    Press Enter to continue at your own risk (a virtual environment based on
    %s
    will be created and all packages will be installed from source).


    Press CTRL-C now to abort and to install the virtual environment by hand.
    """ % sys.executable)
    raw_input()
    print "\n"
    print dedent("""
    We will now create a virtual environment.

    You may give the virtual environment access to your site-packages. This may
    be a good idea if you have packages like numpy and sympy installed through
    your OS package manager, and don't want to install a Python distributation
    like Enthought Canopy in user space. However, you might run into trouble
    with incompatible versions. If your prefer to create the virtual
    environment manually, press CTRL-C now.

    """)
    print "Do you want to create the virtual environment with access to the"
    print "site packages? [no]/yes: ",
    answer=raw_input().lower()
    sys.path.insert(0, "./scripts/virtualenv")
    from virtualenv import main as venv
    if answer == 'yes':
        print "Virtual environment will have access to site packages"
        venv(argv=['--system-site-packages', './venv'])
    else:
        venv(argv=['./venv'])
