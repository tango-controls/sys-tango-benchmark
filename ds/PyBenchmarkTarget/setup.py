#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the PythonBenchmark project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

import os
import sys
from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.command.clean import clean
from distutils.util import get_platform
import shutil

setup_dir = os.path.dirname(os.path.abspath(__file__))

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

readme_filename = os.path.join(setup_dir, 'README.rst')
with open(readme_filename) as file:
    long_description = file.read()

release_filename = os.path.join(setup_dir, 'PythonBenchmark', 'release.py')
exec(open(release_filename).read())

pack = ['PythonBenchmark']

needs_pytest = set(['test']).intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(name=name,
      version=version,
      description='Benchmark device for counting attribute, command and pipe calls',
      packages=pack,
      include_package_data=True,
      zip_safe=False,
      setup_requires=pytest_runner,
      tests_require=['pytest'],
      # test_suite="test",
      entry_points={'console_scripts':['PythonBenchmark = PythonBenchmark:main']},
      author='jankotan',
      author_email='jankotan at gmail.com',
      license='GPL',
      long_description=long_description,
      url='www.tango-controls.org',
      platforms="All Platforms"
      )
