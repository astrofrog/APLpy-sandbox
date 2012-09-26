#!/usr/bin/env python

import os
import sys
import subprocess

from distutils.core import setup, Command

try:  # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:  # Python 2.x
    from distutils.command.build_py import build_py


class PyTest(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, 'runtests.py', '-q'])
        raise SystemExit(errno)

setup(name='APLpy2',
      version='0.1.0',
      license='BSD',
      packages=['aplpy2'],
      provides=['aplpy2'],
      cmdclass={'build_py': build_py, 'test': PyTest},
     )
