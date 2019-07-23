#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018  Jan Kotanski <jankotan@gmail.com> / S2Innovation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 3
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

import os
import sys
import subprocess
from setuptools import setup
from distutils.core import Command
cmd_class = {}
try:
    from sphinx.setup_command import BuildDoc
    cmd_class['build_sphinx'] = BuildDoc
except ImportError:
    print("WARNING: sphinx not available, not adding 'build_sphinx' command.")

setup_dir = os.path.dirname(os.path.abspath(__file__))

release_info = {}
exec(open(os.path.join('PyBenchmarkTarget', 'release.py')).read(),
     release_info)

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

readme_filename = os.path.join(setup_dir, 'README.rst')
with open(readme_filename) as file:
    long_description = file.read()

release_filename = os.path.join(setup_dir, 'PyBenchmarkTarget', 'release.py')
exec(open(release_filename).read())

pack = ['PyBenchmarkTarget']


class TestCommand(Command):
    """ test command class
    """

    #: user options
    user_options = []

    #: initializes options
    def initialize_options(self):
        pass

    #: finalizes options
    def finalize_options(self):
        pass

    #: runs command
    def run(self):
        errno = subprocess.call([sys.executable, 'test'])
        raise SystemExit(errno)


cmd_class['test'] = TestCommand


#: metadata for distutils
SETUPDATA = dict(
    name=release_info['name'],
    version=release_info['version'],
    description='Benchmark device for counting attribute, '
    'command and pipe calls',
    packages=pack,
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['PyBenchmarkTarget = PyBenchmarkTarget:main']},
    author='Jan Kotanski, Piotr Goryl',
    author_email='jankotan at gmail.com, piotr.goryl at s2innovation.com',
    license='GPL',
    long_description=long_description,
    url='www.tango-controls.org',
    platforms="All Platforms",
    install_requires=['sphinx', 'numpy'],
    cmdclass=cmd_class
)


def main():
    """ the main function """
    setup(**SETUPDATA)


if __name__ == '__main__':
    main()
