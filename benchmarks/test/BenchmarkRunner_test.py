#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018  Jan Kotanski <jankotan@gmail.com> / S2Innovation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
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

"""Contain the tests for the Benchmark runner."""

import sys
import os
import unittest
# import subprocess
# import numpy as np
# import time
# import PyTango
import docutils.nodes
import docutils.parsers.rst
import docutils.utils

from benchmarks import runner

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

#: python3 running
PY3 = (sys.version_info > (3,))


# Device test case
class BenchmarkRunnerTest(unittest.TestCase):
    """Test case for packet generation."""

    def __init__(self, methodName):
        """ constructor

        :param methodName: name of the test method
        """
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        print("\nsetting up ...")

    def tearDown(self):
        print("tearing down ...")

    def runscript(self, argv):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = mystdout = StringIO()
        sys.stderr = mystderr = StringIO()

        old_argv = sys.argv
        sys.argv = argv
        runner.main()

        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        vl = mystdout.getvalue()
        er = mystderr.getvalue()
        return vl, er

    def test_BenchmarkRunnerDefault(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(['benchmarkrunner'])

        self.assertEqual('', er)
        self.assertTrue(vl)
        # print(vl)

        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(
            components=components).get_default_values()
        document = docutils.utils.new_document(
            '<rst-doc>', settings=settings)
        parser.parse(vl, document)

        self.assertEqual(len(document), 4)
        self.assertEqual(len(document[0]), 5)

        # python read benchmark
        self.assertEqual(len(document[0][0]), 1)
        self.assertEqual(
            str(document[0][0]),
            '<title>python read benchmark</title>')
        self.assertEqual(len(document[0][1]), 1)
        self.assertEqual(
            str(document[0][1]),
            '<paragraph>Speed test</paragraph>')
        self.assertEqual(len(document[0][2]), 2)
        self.assertEqual(len(document[0][2][0]), 1)
        self.assertEqual(
            str(document[0][2][0]),
            '<strong>Date:</strong>')
        self.assertTrue(str(document[0][3][1]))
        self.assertEqual(len(document[0][3]), 2)
        self.assertEqual(len(document[0][3][0]), 1)
        self.assertEqual(
            str(document[0][3][0]),
            '<title>Benchmark setup</title>')
        self.assertEqual(
            str(document[0][3][1]),
            '<paragraph>'
            'attribute=BenchmarkScalarAttribute\n'
            'clients=4,6,8,10\ncsvfile=\n'
            'device=test/pybenchmarktarget/01\n'
            'period=10'
            '</paragraph>'
        )
        self.assertEqual(len(document[0][4]), 2)
        self.assertEqual(len(document[0][4][0]), 1)
        self.assertEqual(
            str(document[0][4][0]),
            '<title>Results</title>')
        self.assertEqual(
            document[0][4][1].tagname, 'table'
        )
        self.assertEqual(len(document[0][4][1]), 1)
        self.assertEqual(
            document[0][4][1][0].tagname, 'tgroup'
        )
        self.assertEqual(len(document[0][4][1][0]), 14)
        for i in range(12):
            self.assertEqual(
                document[0][4][1][0][i].tagname, 'colspec'
            )
        self.assertEqual(
            document[0][4][1][0][12].tagname, 'thead'
        )
        self.assertEqual(
            str(document[0][4][1][0][12]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [read]</paragraph></entry>'
            '<entry><paragraph>error [read]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>error [read/s]</paragraph></entry>'
            '<entry><paragraph>Counts [read]</paragraph></entry>'
            '<entry><paragraph>error [read]</paragraph></entry>'
            '<entry><paragraph>Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>error [read/s]</paragraph></entry>'
            '<entry><paragraph>No.</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>error [s]</paragraph></entry>'
            '</row></thead>'
        )
        self.assertEqual(
            document[0][4][1][0][13].tagname, 'tbody'
        )
        self.assertEqual(len(document[0][4][1][0][13]), 4)
        for i in range(4):
            self.assertEqual(len(document[0][4][1][0][13][i][0][0][0]), i)
        self.assertEqual(len(document[0][4][1][0][13][0]), 12)
        for i in range(4):
            for j in range(14):
                self.assertTrue(isinstance(
                    float(document[0][4][1][0][13][i][j][0][0]),
                    float))


def main():
    """ main function"""
    unittest.main()


# Main execution
if __name__ == "__main__":
    main()
