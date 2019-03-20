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
import shutil
import unittest
import datetime
import docutils.parsers.rst
import docutils.utils
import dateutil.parser

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
        shutil.copy('test/assets/default.yml', './')

    def tearDown(self):
        print("tearing down ...")
        os.remove('default.yml')

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

    def runscript2(self, argv):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        mystdout = StringIO()
        mystderr = StringIO()
        # sys.stdout = mystdout = StringIO()
        # sys.stderr = mystderr = StringIO()

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

        vl, er = self.runscript(['tg_benchmarkrunner'])

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl)

    def test_BenchmarkRunnerDefaultJSON(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/python_test.json'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl)

    def test_BenchmarkRunnerDefaultJava(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/java_test.yml'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl, "java")

    def test_BenchmarkRunnerDefaultCPP(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/cpp_test.yml'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl, "cpp")

    def check_default(self, text, lang="python"):
        if lang == "python":
            dvname = 'test/pybenchmarktarget/01'
        else:
            dvname = 'test/%sbenchmarktarget/01' % lang
        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(
            components=components).get_default_values()
        document = docutils.utils.new_document(
            '<rst-doc>', settings=settings)
        parser.parse(text, document)

        self.assertEqual(len(document), 4)

        # python read benchmark
        section = document[0]
        self.assertEqual(section.tagname, 'section')
        self.assertEqual(len(section), 5)
        self.assertEqual(len(section[0]), 1)
        self.assertEqual(
            str(section[0]), '<title>%s read benchmark</title>' % lang)
        self.assertEqual(len(section[1]), 1)
        self.assertEqual(
            str(section[1]), '<paragraph>Speed test</paragraph>')
        self.assertEqual(len(section[2]), 2)
        self.assertEqual(len(section[2][0]), 1)
        self.assertEqual(
            str(section[2][0]), '<strong>Date:</strong>')
        self.assertTrue(isinstance(
            dateutil.parser.parse(str(section[2][1])),
            datetime.datetime))
        self.assertTrue(str(section[3][1]))
        self.assertEqual(len(section[3]), 2)
        self.assertEqual(len(section[3][0]), 1)
        self.assertEqual(
            str(section[3][0]), '<title>Benchmark setup</title>')
        self.assertEqual(
            str(section[3][1]),
            '<paragraph>'
            'attribute=BenchmarkScalarAttribute\n'
            'clients=4,6,8,10\ncsvfile=\n'
            'device=%s\n'
            'period=1'
            '</paragraph>' % dvname
        )
        self.assertEqual(len(section[4]), 2)
        self.assertEqual(len(section[4][0]), 1)
        self.assertEqual(
            str(section[4][0]),
            '<title>Results</title>')
        table = section[4][1]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [read]</paragraph></entry>'
            '<entry><paragraph>SD [read]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>SD [read/s]</paragraph></entry>'
            '<entry><paragraph>Counts [read]</paragraph></entry>'
            '<entry><paragraph>SD [read]</paragraph></entry>'
            '<entry><paragraph>Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>SD [read/s]</paragraph></entry>'
            '<entry><paragraph>No. clients</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>SD [s]</paragraph></entry>'
            '<entry><paragraph>Errors</paragraph></entry>'
            '</row></thead>'
        )
        tbody = table[0][14]
        self.assertEqual(tbody.tagname, 'tbody')
        self.assertEqual(len(tbody), 4)
        for i in range(4):
            self.assertEqual(int(tbody[i][0][0][0]), i)
        self.assertEqual(len(tbody[0]), 13)
        for i in range(4):
            self.assertEqual(tbody[i].tagname, 'row')
            for j in range(13):
                self.assertEqual(tbody[i][j].tagname, 'entry')
                self.assertEqual(tbody[i][j][0].tagname, 'paragraph')
                self.assertEqual(tbody[i][j][0][0].tagname, '#text')
                self.assertTrue(isinstance(float(tbody[i][j][0][0]), float))

        # python write benchmark
        section = document[1]
        self.assertEqual(section.tagname, 'section')
        self.assertEqual(len(section), 5)
        self.assertEqual(len(section[0]), 1)
        self.assertEqual(
            str(section[0]), '<title>%s write benchmark</title>' % lang)
        self.assertEqual(len(section[1]), 1)
        self.assertEqual(
            str(section[1]), '<paragraph>Speed test</paragraph>')
        self.assertEqual(len(section[2]), 2)
        self.assertEqual(len(section[2][0]), 1)
        self.assertEqual(
            str(section[2][0]), '<strong>Date:</strong>')
        self.assertTrue(isinstance(
            dateutil.parser.parse(str(section[2][1])),
            datetime.datetime))
        self.assertTrue(str(section[3][1]))
        self.assertEqual(len(section[3]), 3)
        self.assertEqual(len(section[3][0]), 1)
        self.assertEqual(
            str(section[3][0]), '<title>Benchmark setup</title>')
        self.assertEqual(section[3][1].tagname, 'system_message')
        self.assertEqual(
            str(section[3][1][0]),
            '<paragraph>'
            'Duplicate implicit target name: "benchmark setup".'
            '</paragraph>'
        )
        self.assertEqual(
            str(section[3][2]),
            '<paragraph>attribute=BenchmarkScalarAttribute\n'
            'clients=4,6,8,10\n'
            'csvfile=\n'
            'device=%s\n'
            'period=1\n'
            'shape=\n'
            'value=0'
            '</paragraph>' % dvname
        )
        self.assertEqual(len(section[4]), 3)
        self.assertEqual(len(section[4][0]), 1)
        self.assertEqual(
            str(section[4][0]),
            '<title>Results</title>')
        self.assertEqual(section[4][1].tagname, 'system_message')
        self.assertEqual(
            str(section[4][1][0]),
            '<paragraph>Duplicate implicit target name: "results".</paragraph>'
        )
        table = section[4][2]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [write]</paragraph></entry>'
            '<entry><paragraph>SD [write]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [write/s]</paragraph></entry>'
            '<entry><paragraph>SD [write/s]</paragraph></entry>'
            '<entry><paragraph>Counts [write]</paragraph></entry>'
            '<entry><paragraph>SD [write]</paragraph></entry>'
            '<entry><paragraph>Speed [write/s]</paragraph></entry>'
            '<entry><paragraph>SD [write/s]</paragraph></entry>'
            '<entry><paragraph>No. clients</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>SD [s]</paragraph></entry>'
            '<entry><paragraph>Errors</paragraph></entry>'
            '</row></thead>'
        )
        tbody = table[0][14]
        self.assertEqual(tbody.tagname, 'tbody')
        self.assertEqual(len(tbody), 4)
        for i in range(4):
            self.assertEqual(int(tbody[i][0][0][0]), i)
        self.assertEqual(len(tbody[0]), 13)
        for i in range(4):
            self.assertEqual(tbody[i].tagname, 'row')
            for j in range(13):
                self.assertEqual(tbody[i][j].tagname, 'entry')
                self.assertEqual(tbody[i][j][0].tagname, 'paragraph')
                self.assertEqual(tbody[i][j][0][0].tagname, '#text')
                self.assertTrue(
                    isinstance(float(tbody[i][j][0][0]), float))

        # python event benchmark
        section = document[2]
        self.assertEqual(section.tagname, 'section')
        self.assertEqual(len(section), 5)
        self.assertEqual(len(section[0]), 1)
        self.assertEqual(
            str(section[0]), '<title>%s event benchmark</title>' % lang)
        self.assertEqual(len(section[1]), 1)
        self.assertEqual(
            str(section[1]), '<paragraph>Speed test</paragraph>')
        self.assertEqual(len(section[2]), 2)
        self.assertEqual(len(section[2][0]), 1)
        self.assertEqual(
            str(section[2][0]), '<strong>Date:</strong>')
        self.assertTrue(isinstance(
            dateutil.parser.parse(str(section[2][1])),
            datetime.datetime))
        self.assertTrue(str(section[3][1]))
        self.assertEqual(len(section[3]), 3)
        self.assertEqual(len(section[3][0]), 1)
        self.assertEqual(
            str(section[3][0]), '<title>Benchmark setup</title>')
        self.assertEqual(section[3][1].tagname, 'system_message')
        self.assertEqual(
            str(section[3][1][0]),
            '<paragraph>'
            'Duplicate implicit target name: "benchmark setup".'
            '</paragraph>'
        )
        self.assertEqual(
            str(section[3][2]),
            '<paragraph>'
            'attribute=BenchmarkScalarAttribute\n'
            'clients=4,6,8,10\n'
            'csvfile=\n'
            'device=%s\n'
            'period=1'
            '</paragraph>' % dvname
        )
        self.assertEqual(len(section[4]), 3)
        self.assertEqual(len(section[4][0]), 1)
        self.assertEqual(
            str(section[4][0]),
            '<title>Results</title>')
        self.assertEqual(section[4][1].tagname, 'system_message')
        self.assertEqual(
            str(section[4][1][0]),
            '<paragraph>Duplicate implicit target name: "results".</paragraph>'
        )
        table = section[4][2]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [event]</paragraph></entry>'
            '<entry><paragraph>SD [event]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [event/s]</paragraph></entry>'
            '<entry><paragraph>SD [event/s]</paragraph></entry>'
            '<entry><paragraph>Counts [event]</paragraph></entry>'
            '<entry><paragraph>SD [event]</paragraph></entry>'
            '<entry><paragraph>Speed [event/s]</paragraph></entry>'
            '<entry><paragraph>SD [event/s]</paragraph></entry>'
            '<entry><paragraph>No. clients</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>SD [s]</paragraph></entry>'
            '<entry><paragraph>Errors</paragraph></entry>'
            '</row></thead>'
        )
        tbody = table[0][14]
        self.assertEqual(tbody.tagname, 'tbody')
        self.assertEqual(len(tbody), 4)
        for i in range(4):
            self.assertEqual(int(tbody[i][0][0][0]), i)
        self.assertEqual(len(tbody[0]), 13)
        for i in range(4):
            self.assertEqual(tbody[i].tagname, 'row')
            for j in range(13):
                self.assertEqual(tbody[i][j].tagname, 'entry')
                self.assertEqual(tbody[i][j][0].tagname, 'paragraph')
                self.assertEqual(tbody[i][j][0][0].tagname, '#text')
                self.assertTrue(
                    isinstance(float(tbody[i][j][0][0]), float))

        # python pipe benchmark
        section = document[3]
        self.assertEqual(section.tagname, 'section')
        self.assertEqual(len(section), 5)
        self.assertEqual(len(section[0]), 1)
        self.assertEqual(
            str(section[0]), '<title>%s pipe benchmark</title>' % lang)
        self.assertEqual(len(section[1]), 1)
        self.assertEqual(
            str(section[1]), '<paragraph>Speed test</paragraph>')
        self.assertEqual(len(section[2]), 2)
        self.assertEqual(len(section[2][0]), 1)
        self.assertEqual(
            str(section[2][0]), '<strong>Date:</strong>')
        self.assertTrue(isinstance(
            dateutil.parser.parse(str(section[2][1])),
            datetime.datetime))
        self.assertTrue(str(section[3][1]))
        self.assertEqual(len(section[3]), 3)
        self.assertEqual(len(section[3][0]), 1)
        self.assertEqual(
            str(section[3][0]), '<title>Benchmark setup</title>')
        self.assertEqual(section[3][1].tagname, 'system_message')
        self.assertEqual(
            str(section[3][1][0]),
            '<paragraph>'
            'Duplicate implicit target name: "benchmark setup".'
            '</paragraph>'
        )
        self.assertEqual(
            str(section[3][2]),
            '<paragraph>'
            'clients=4,6,8,10\n'
            'csvfile=\n'
            'device=%s\n'
            'period=1\n'
            'pipe=BenchmarkPipe\n'
            'size=1'
            '</paragraph>' % dvname
        )
        self.assertEqual(len(section[4]), 4)
        self.assertEqual(len(section[4][0]), 1)
        self.assertEqual(
            str(section[4][0]),
            '<title>Results</title>')
        self.assertEqual(section[4][1].tagname, 'system_message')
        self.assertEqual(
            str(section[4][1][0]),
            '<paragraph>Duplicate implicit target name: "results".</paragraph>'
        )
        table = section[4][2]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [write]</paragraph></entry>'
            '<entry><paragraph>SD [write]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [write/s]</paragraph></entry>'
            '<entry><paragraph>SD [write/s]</paragraph></entry>'
            '<entry><paragraph>Counts [write]</paragraph></entry>'
            '<entry><paragraph>SD [write]</paragraph></entry>'
            '<entry><paragraph>Speed [write/s]</paragraph></entry>'
            '<entry><paragraph>SD [write/s]</paragraph></entry>'
            '<entry><paragraph>No. clients</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>SD [s]</paragraph></entry>'
            '<entry><paragraph>Errors</paragraph></entry>'
            '</row></thead>'
        )
        tbody = table[0][14]
        self.assertEqual(tbody.tagname, 'tbody')
        self.assertEqual(len(tbody), 4)
        for i in range(4):
            self.assertEqual(int(tbody[i][0][0][0]), i)
        self.assertEqual(len(tbody[0]), 13)
        for i in range(4):
            self.assertEqual(tbody[i].tagname, 'row')
            for j in range(13):
                self.assertEqual(tbody[i][j].tagname, 'entry')
                self.assertEqual(tbody[i][j][0].tagname, 'paragraph')
                self.assertEqual(tbody[i][j][0][0].tagname, '#text')
                self.assertTrue(
                    isinstance(float(tbody[i][j][0][0]), float))

        table = section[4][3]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            '<thead><row>'
            '<entry><paragraph>Run no.</paragraph></entry>'
            '<entry><paragraph>Sum counts [read]</paragraph></entry>'
            '<entry><paragraph>SD [read]</paragraph></entry>'
            '<entry><paragraph>Sum Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>SD [read/s]</paragraph></entry>'
            '<entry><paragraph>Counts [read]</paragraph></entry>'
            '<entry><paragraph>SD [read]</paragraph></entry>'
            '<entry><paragraph>Speed [read/s]</paragraph></entry>'
            '<entry><paragraph>SD [read/s]</paragraph></entry>'
            '<entry><paragraph>No. clients</paragraph></entry>'
            '<entry><paragraph>Time [s]</paragraph></entry>'
            '<entry><paragraph>SD [s]</paragraph></entry>'
            '<entry><paragraph>Errors</paragraph></entry>'
            '</row></thead>'
        )
        tbody = table[0][14]
        self.assertEqual(tbody.tagname, 'tbody')
        self.assertEqual(len(tbody), 4)
        for i in range(4):
            self.assertEqual(int(tbody[i][0][0][0]), i)
        self.assertEqual(len(tbody[0]), 13)
        for i in range(4):
            self.assertEqual(tbody[i].tagname, 'row')
            for j in range(13):
                self.assertEqual(tbody[i][j].tagname, 'entry')
                self.assertEqual(tbody[i][j][0].tagname, 'paragraph')
                self.assertEqual(tbody[i][j][0][0].tagname, '#text')
                self.assertTrue(
                    isinstance(float(tbody[i][j][0][0]), float))


def main():
    """ main function"""
    unittest.main()


# Main execution
if __name__ == "__main__":
    main()
