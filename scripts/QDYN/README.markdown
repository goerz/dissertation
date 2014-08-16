---
Title: The QDYN Python Package
CSS: ./style.css
---

# The QDYN Python Package

The QDYN library contains a Python package for extending functionality of the
core Fortran code.  The package will read and write some of the files generated
by the Fortran QDYN routines, and provides additional tools (such as signal
processing for pulses) that are easier to implement in Python and that will
greatly benefit from (i)Python's interactiveness.

You will find the library in the subfolder `scripts/python`.


## Prerequisites ##

The way packages work in Python is a bit of a mess. Basically, the package is
made available system-wide to a Python installation by copying its files into a
special folder (one of the folders that are listed when you type
`import sys; print sys.path` in python. This gets complicated by the fact that
(a) you can have several Python installations on your system in parallel and (b)
the "system" Python (the one installed through the operating systems' package
manager) will usually not have the folders in `sys.path` writable to the user,
making it impossible to install packages without being root. Even if you are
root, however, it is generally not recommended to install too many packages into
your system Python.

Instead, there are two approaches:

*   Install one of the Scientific Python Distributions like
    [Enthought Canopy][EPD] in your home directory. This has the huge benefit
    that all the scientific packages that can be tricky to install because they
    contain compiled extensions will be there out of the box. Also, this is the
    easiest way to always have the bleeding-edge version of all packages. You
    can use the `enpgk` utility to install additional packages if they are
    publicly available. Only use "manual" installation with `python setup.py
    install` for packages that are not publicly available (such as this QDYN
    package)

*   Create a Python virtual environment. This creates a lightweight copy of your
    system Python in your home directory, where you can easily install
    additional packages. However, installation of the big scientific
    packages can be tricky. Before creating the virtual environment, you should
    ask the administrator to install things like `numpy`, `scipy` and
    `matplotlib` through the OS package manager. This will make them available
    to the system Python, and to your virtual environment by extension. You may
    not get bleeding edge versions this way. In your virtual environment,
    install further publicly available packages using the `pip` utility.

In any case, you should have the `pip`, `setuptools`, and `virtualenv`
utilities. If you are using Canopy, they'll be there. In most other situtation
(unless you're on a very out-of-date system), they'll also be there by default.
Worst case, you'll have to follow the instructions from the [Python Packaging
User Guide][PPUG] (a very recommended read in any case).

The QDYN library is written for Python 2.7. It will not run on Python 3.x
(Python 3 is a not backwards-compatible with Python 2)

It depends on the most recent versions of `matplotlib`, `numpy`, and `scipy`,
aka the [standard Python scientific stack](Scipy).


## Install ##

Assuming that you have either a scientific Python distribution installed in your
home directory (recommended), or created a virtual environment, you can install
the QDYN package by going to the `scripts/python` subfolder and running

    python setup.py install

You can also do this from the main `qdyn` folder via `make`:

    make install-python

A quick complete rundown if you're using `virtual_env`, including the creation
of the virtual environment:

*   Download the [`virtual_env.py`][VE] script into your `$PATH` (unless
    `virtualenv` is already installed or you can install it via some other
    method such as `pip`)
*   Create a virtual environment and install the QDYN package into it (ensure
    that your system Python contains a recent version of `numpy`, `scipy`, and
    `matplotlib`):

        mkdir ~/.virtualenvs
        cd ~/.virtualenvs
        virtual_env.py qdyn
        source ~/.virtualenvs/qdyn/bin/activate
        # if you didn't have numpy, scipy, matplotlib in the system Python
        # before creating the virtual environment, you may try to install them
        # now
        # pip install numpy scipy matplotlib
        cd ~/qdyn
        make install-python
        deactivate
        # if you're going to work with the virtual environment again, you'll
        # have to re-activate it (source ~/.virtualenvs/qdyn/bin/activate)

## Usage ##

Load the package with `import QDYN` in your python script.

There are a lof parts that can be used interactively in
[IPython](IPython) (either the shell or the notebook interface).
For example:

    >>> import QDYN
    >>> from QDYN.pulse import Pulse
    >>> p = Pulse('pulse.dat')
    >>> p.amplitude *= QDYN.pulse.flattop(p.tgrid, p.t0(), p.T(), t_rise=5)
    >>> p.show()
    >>> p.resample(upsample=2)
    >>> p.write('pulse_doublesampled.dat')


[VE]: http://bitbucket.org/ianb/virtualenv/raw/tip/virtualenv.py
[PPUG]: https://packaging.python.org/en/latest/tutorial.html#installing-the-tools
[EPD]: https://www.enthought.com/products/canopy/
[Scipy]: http://www.scipy.org
[IPython]: http://ipython.org
