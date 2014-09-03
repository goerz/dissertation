#!/usr/bin/env python
from distutils.core import setup
from GoerzDiss import __version__


setup(name='GoerzDiss',
      version=__version__,
      description='Package providing extra Tools for generating graphics for disseration',
      author='Michael Goerz',
      author_email='goerz@physik.uni-kassel.de',
      license='GPL',
      packages=['GoerzDiss',],
      scripts=[],
     )
