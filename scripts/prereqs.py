#!/usr/bin/env python
"""
Test the environment for compilation of the thesis, write requirements.txt with
missing python packages
"""
import os
import sys
import subprocess
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

def checkdep_dvipng():
    # taken from matplotlib
    try:
        s = subprocess.Popen(['dvipng','-version'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = s.communicate()
        line = stdout.decode('ascii').split('\n')[1]
        v = line.split()[-1]
        return v
    except (IndexError, ValueError, OSError):
        return None

if checkdep_dvipng() is None:
    print "%s is required for compilation" % 'dvipng'
    sys.exit(1)

def checkdep_ghostscript():
    # taken from matplotlib
    if sys.platform == 'win32':
        gs_execs = ['gswin32c', 'gswin64c', 'gs']
    else:
        gs_execs = ['gs']
    for gs_exec in gs_execs:
        try:
            s = subprocess.Popen(
                [gs_exec, '--version'], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = s.communicate()
            if s.returncode == 0:
                v = stdout[:-1].decode('ascii')
                return gs_exec, v
        except (IndexError, ValueError, OSError):
            pass
    return None, None

gs, __ = checkdep_ghostscript()
if gs is None:
    print "%s is required for compilation" % 'ghostscript'
    sys.exit(1)


# Create virtual environment
if not os.path.isdir("venv"):
    print dedent("""
    You must create a Python virtual environment in the folder ./venv before
    continuing.

    If at all possible, use a binary python installation such as Enthought
    Canopy <https://www.enthought.com/products/canopy/>, or
    Anaconda <https://store.continuum.io/cshop/anaconda/>
    and install the standard scientific stack (numpy, matplotlib, scipy, sympy,
    ipython) into the virtual environment before continuing.

    Assuming you have Enthought Canopy installed, you should be able to do the
    following:

        canopy_cli venv ./venv
        ./venv/bin/enpkg nose mock numpy matplotlib scipy sympy ipython

    With Anaconda, the appropriate command is:

        conda create -m -p ./venv --yes pip nose mock numpy matplotlib scipy sympy ipython

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

if os.path.isdir("venv"):
    os.chdir("venv")
    if os.path.isdir("bin"):
        os.chdir("bin")
        if not os.path.isfile("pip"):
            if os.path.isfile("pip2"):
                print "Creating symlink pip -> pip2"
                os.symlink("pip2", "pip")
            else:
                print "neither pip nor pip2 is available. Please make sure " \
                "pip is installed in venv"
                sys.exit(1)
    else:
        print "venv/bin does not exist"
        sys.exit(1)
