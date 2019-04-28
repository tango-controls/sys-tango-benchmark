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

from tangobenchmarks import runner

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

#: python3 running
PY3 = (sys.version_info > (3,))

BENCHMARK_RST_SETUP_READ = (
    'attribute=BenchmarkScalarAttribute\n'
    'clients=4,6,8,10\n'
    'csvfile=\n'
    'device=%s\n'
    'period=1'
)

BENCHMARK_RST_SETUP_WRITE = (
    'attribute=BenchmarkScalarAttribute\n'
    'clients=4,6,8,10\n'
    'csvfile=\n'
    'device=%s\n'
    'period=1\n'
    'shape=\n'
    'value=0'
)

BENCHMARK_RST_SETUP_EVENT = (
    'attribute=BenchmarkScalarAttribute\n'
    'clients=4,6,8,10\n'
    'csvfile=\n'
    'device=%s\n'
    'period=1'
)

BENCHMARK_RST_SETUP_PIPE_WRITE = (
    'clients=4,6,8,10\n'
    'csvfile=\n'
    'device=%s\n'
    'period=1\n'
    'pipe=BenchmarkPipe\n'
    'size=1'
)

BENCHMARK_RST_SETUP_PIPE_READ = BENCHMARK_RST_SETUP_PIPE_WRITE

BENCHMARK_RST_TABLE_HEADERS = (
    '<thead><row>'
    '<entry><paragraph>Run no.</paragraph></entry>'
    '<entry><paragraph>No. clients</paragraph></entry>'
    '<entry><paragraph>Sum counts [{0}]</paragraph></entry>'
    '<entry><paragraph>SD [{0}]</paragraph></entry>'
    '<entry><paragraph>Sum Speed [{0}/s]</paragraph></entry>'
    '<entry><paragraph>SD [{0}/s]</paragraph></entry>'
    '<entry><paragraph>Counts [{0}]</paragraph></entry>'
    '<entry><paragraph>SD [{0}]</paragraph></entry>'
    '<entry><paragraph>Speed [{0}/s]</paragraph></entry>'
    '<entry><paragraph>SD [{0}/s]</paragraph></entry>'
    '<entry><paragraph>Time [s]</paragraph></entry>'
    '<entry><paragraph>SD [s]</paragraph></entry>'
    '<entry><paragraph>Errors</paragraph></entry>'
    '</row></thead>'
)


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

    def ttest_BenchmarkRunnerDefault(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(['tg_benchmarkrunner'])

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl, 'python')

    def test_BenchmarkRunnerDefaultJSON(self):
        """Test for BenchmarkRunner default"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/python_test.json'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)
        self.check_default(vl, 'python')

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

    def test_external_dummy_client(self):
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/external_dummy.yml'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)

        lang = 'python'
        dvname = self.get_target_device_name(lang)
        document = self.parse_rst(vl)
        self.assertEqual(len(document), 2)

        self.check_benchmark_rst_output(
            document[0],
            has_duplicate_targets=False,
            title=('%s read benchmark' % lang),
            operation='read',
            setup=(BENCHMARK_RST_SETUP_READ % dvname))

        self.check_benchmark_rst_output(
            document[1],
            has_duplicate_targets=True,
            title=('%s write benchmark' % lang),
            operation='write',
            setup=(BENCHMARK_RST_SETUP_WRITE % dvname))

    def test_external_cpp_client(self):
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        vl, er = self.runscript(
            'benchmarkrunner -c test/assets/external_cpp.yml'.split())

        self.assertEqual('', er)
        self.assertTrue(vl)
        print(vl)

        lang = 'python'
        dvname = self.get_target_device_name(lang)
        document = self.parse_rst(vl)
        self.assertEqual(len(document), 1)

        self.check_benchmark_rst_output(
            document[0],
            has_duplicate_targets=False,
            title=('%s read benchmark' % lang),
            operation='read',
            setup=(BENCHMARK_RST_SETUP_READ % dvname))

    def get_target_device_name(self, lang):
        if lang == "python":
            return 'test/pybenchmarktarget/01'
        else:
            return 'test/%sbenchmarktarget/01' % lang

    def parse_rst(self, text):
        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(
            components=components).get_default_values()
        document = docutils.utils.new_document(
            '<rst-doc>', settings=settings)
        parser.parse(text, document)
        return document

    def check_benchmark_rst_output(
            self,
            section,
            has_duplicate_targets,
            title,
            operation,
            setup):
        self.assertEqual(section.tagname, 'section')

        self.assertEqual(len(section), 5)

        self.assertEqual(len(section[0]), 1)
        self.assertEqual(str(section[0]), '<title>%s</title>' % title)

        self.assertEqual(len(section[1]), 1)
        self.assertEqual(str(section[1]), '<paragraph>Speed test</paragraph>')

        self.assertEqual(len(section[2]), 2)
        self.assertEqual(len(section[2][0]), 1)
        self.assertEqual(str(section[2][0]), '<strong>Date:</strong>')
        date = dateutil.parser.parse(str(section[2][1]))
        self.assertIsInstance(date, datetime.datetime)

        self.assertEqual(len(section[3]), 3 if has_duplicate_targets else 2)
        self.assertEqual(len(section[3][0]), 1)
        self.assertEqual(str(section[3][0]), '<title>Benchmark setup</title>')
        self.assertTrue(str(section[3][1]))

        if has_duplicate_targets:
            self.assertEqual(section[3][1].tagname, 'system_message')
            self.assertEqual(
                str(section[3][1][0]),
                '<paragraph>'
                'Duplicate implicit target name: "benchmark setup".'
                '</paragraph>'
            )

        self.assertEqual(
            str(section[3][2 if has_duplicate_targets else 1]),
            '<paragraph>%s</paragraph>' % setup)

        self.assertEqual(len(section[4]), 3 if has_duplicate_targets else 2)
        self.assertEqual(len(section[4][0]), 1)
        self.assertEqual(str(section[4][0]), '<title>Results</title>')

        if has_duplicate_targets:
            self.assertEqual(section[4][1].tagname, 'system_message')
            self.assertEqual(
                str(section[4][1][0]),
                '<paragraph>'
                'Duplicate implicit target name: "results".'
                '</paragraph>'
            )

        table = section[4][2 if has_duplicate_targets else 1]
        self.assertEqual(table.tagname, 'table')
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0].tagname, 'tgroup')
        self.assertEqual(len(table[0]), 15)
        for i in range(13):
            self.assertEqual(table[0][i].tagname, 'colspec')
        self.assertEqual(table[0][13].tagname, 'thead')
        self.assertEqual(
            str(table[0][13]),
            BENCHMARK_RST_TABLE_HEADERS.format(operation)
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

    def check_default(self, text, lang):
        dvname = self.get_target_device_name(lang)
        document = self.parse_rst(text)

        self.assertEqual(len(document), 5)

        self.check_benchmark_rst_output(
            document[0],
            has_duplicate_targets=False,
            title=('%s read benchmark' % lang),
            operation='read',
            setup=(BENCHMARK_RST_SETUP_READ % dvname)
        )

        self.check_benchmark_rst_output(
            document[1],
            has_duplicate_targets=True,
            title=('%s write benchmark' % lang),
            operation='write',
            setup=(BENCHMARK_RST_SETUP_WRITE % dvname)
        )

        self.check_benchmark_rst_output(
            document[2],
            has_duplicate_targets=True,
            title=('%s event benchmark' % lang),
            operation='event',
            setup=(BENCHMARK_RST_SETUP_EVENT % dvname)
        )

        self.check_benchmark_rst_output(
            document[3],
            has_duplicate_targets=True,
            title=('%s pipe write benchmark' % lang),
            operation='write',
            setup=(BENCHMARK_RST_SETUP_PIPE_WRITE % dvname)
        )

        self.check_benchmark_rst_output(
            document[4],
            has_duplicate_targets=True,
            title=('%s pipe read benchmark' % lang),
            operation='read',
            setup=(BENCHMARK_RST_SETUP_PIPE_READ % dvname)
        )


def main():
    """ main function"""
    unittest.main()


# Main execution
if __name__ == "__main__":
    main()
