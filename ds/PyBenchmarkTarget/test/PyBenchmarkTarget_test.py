#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018  Jan Kotanski <jankotan@gmail.com> / S2Innovation
#
# lavue is an image viewing program for photon science imaging detectors.
# Its usual application is as a live viewer using hidra as data source.
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

"""Contain the tests for the Benchmark device."""

import sys
import os
import subprocess
import numpy as np
import time
import unittest
import PyTango


# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))


# Device test case
class PyBenchmarkTargetDeviceTest(unittest.TestCase):
    """Test case for packet generation."""

    def __init__(self, methodName):
        """ constructor
        :param methodName: name of the test method
        """
        unittest.TestCase.__init__(self, methodName)
        self.instance = 'TEST'
        self.device = 'test/pybenchmarktarget/000'
        self.new_device_info_benchmark = PyTango.DbDevInfo()
        self.new_device_info_benchmark._class = "PyBenchmarkTarget"
        self.new_device_info_benchmark.server = "PyBenchmarkTarget/%s" % \
                                                self.instance
        self.new_device_info_benchmark.name = self.device
        self.proxy = None

    def setUp(self):
        print("\nsetting up ...")
        db = PyTango.Database()
        db.add_device(self.new_device_info_benchmark)
        db.add_server(
            self.new_device_info_benchmark.server,
            self.new_device_info_benchmark)

        if sys.version_info > (3,):
            if os.path.isfile("../PyBenchmarkTarget"):
                self._psub = subprocess.call(
                    "cd ..; python3 ./PyBenchmarkTarget %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
            else:
                self._psub = subprocess.call(
                    "python3 PyBenchmarkTarget %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
        else:
            if os.path.isfile("../PyBenchmarkTarget"):
                self._psub = subprocess.call(
                    "cd ..; python ./PyBenchmarkTarget %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
            else:
                self._psub = subprocess.call(
                    "python PyBenchmarkTarget %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
        sys.stdout.write("waiting for server ")

        found = False
        cnt = 0
        while not found and cnt < 1000:
            try:
                sys.stdout.write(".")
                dp = PyTango.DeviceProxy(self.new_device_info_benchmark.name)
                time.sleep(0.1)
                if dp.state() == PyTango.DevState.ON:
                    found = True
            except Exception as e:
                # sys.stderr.write("%s\n" % e)
                # if cnt > 100:
                #     raise
                found = False
            cnt += 1
        print("")
        self.proxy = dp

    def tearDown(self):
        print("tearing down ...")
        db = PyTango.Database()
        db.delete_server(self.new_device_info_benchmark.server)

        pipe = subprocess.Popen(
            "ps -ef | grep 'PyBenchmarkTarget %s'" % self.instance,
            stdout=subprocess.PIPE, shell=True).stdout

        res = str(pipe.read()).split("\n")
        for r in res:
            sr = r.split()
            if len(sr) > 2:
                subprocess.call("kill -9 %s" %
                                sr[1], stderr=subprocess.PIPE, shell=True)
        pipe.close()
        self.proxy = None

    def test_State(self):
        """Test for State"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.assertEqual(self.proxy.State(), PyTango.DevState.ON)

    def test_Status(self):
        """Test for Status"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.assertEqual(self.proxy.Status(), 'State is ON')

    def test_BenchmarkCommand(self):
        """Test for BenchmarkCommand"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.CommandCallsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkCommand()
            self.assertEqual(self.proxy.CommandCallsCount, i + 1)

    def test_SetSpectrumSize(self):
        """Test for SetSpectrumSize"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.SetSpectrumSize(123)
        self.assertEqual(len(self.proxy.BenchmarkSpectrumAttribute), 123)
        self.proxy.SetSpectrumSize(1024)
        self.assertEqual(len(self.proxy.BenchmarkSpectrumAttribute), 1024)

    def test_SetImageSize(self):
        """Test for SetImageSize"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.SetImageSize([123, 456])
        value = self.proxy.BenchmarkImageAttribute
        if isinstance(value, np.ndarray):
            self.assertEqual(value.shape, (123, 456))
            self.proxy.SetImageSize([1024, 2096])
            self.assertEqual(
                self.proxy.BenchmarkImageAttribute.shape, (1024, 2096))
        else:
            self.assertEqual(len(value), 123)
            self.assertEqual(len(value[0]), 456)
            self.proxy.SetImageSize([1024, 2096])
            value2 = self.proxy.BenchmarkImageAttribute
            self.assertEqual(len(value2), 1024)
            self.assertEqual(len(value2[0]), 2096)

    def test_ResetCounters(self):
        """Test for ResetCounters"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        t1 = self.proxy.TimeSinceReset

        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 2)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 3)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 12)
        for i in range(3):
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.proxy.BenchmarkScalarAttribute
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.proxy.BenchmarkSpectrumAttribute
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)
            self.proxy.BenchmarkImageAttribute
            self.proxy.BenchmarkCommand()
        t2 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t1)
        self.proxy.ResetCounters()
        t3 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t3)

        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 2)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 3)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 12)

    def test_BenchmarkScalarAttribute(self):
        """Test for BenchmarkScalarAttribute"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)

        for i in range(10):
            wvl = i*12.24
            self.proxy.BenchmarkScalarAttribute = wvl
            self.assertEqual(self.proxy.ScalarWritesCount, i + 1)
            rvl = self.proxy.BenchmarkScalarAttribute
            self.assertEqual(self.proxy.ScalarReadsCount, i + 1)
            self.assertEqual(wvl, rvl)

    def test_AlwaysExecutedHookCount(self):
        """Test for AlwaysExecutedHookCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        t1 = self.proxy.TimeSinceReset

        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 2)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 3)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 11)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 13)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 14)
        for i in range(3):
            self.assertEqual(
                self.proxy.AlwaysExecutedHookCount, 15 + 9 * i)
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.proxy.BenchmarkScalarAttribute
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.proxy.BenchmarkSpectrumAttribute
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)
            self.proxy.BenchmarkImageAttribute
            self.proxy.BenchmarkCommand()
        t2 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t1)
        self.proxy.ResetCounters()
        t3 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t3)

        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 2)

    def test_ReadAttributeHardwareCount(self):
        """Test for ReadAttributeHardwareCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        t1 = self.proxy.TimeSinceReset

        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 2)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 3)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 8)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 13)
        for i in range(3):
            self.assertEqual(
                self.proxy.ReadAttributeHardwareCount, 14 + i * 5)
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.proxy.BenchmarkScalarAttribute
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.proxy.BenchmarkSpectrumAttribute
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)
            self.proxy.BenchmarkImageAttribute
            self.proxy.BenchmarkCommand()
        t2 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t1)
        self.proxy.ResetCounters()
        t3 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t3)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 2)

    def test_WriteAttributeCounterCount(self):
        """Test for WriteAttributeCounterCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))

        self.proxy.ResetCounters()
        t1 = self.proxy.TimeSinceReset

        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 3)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 4)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)

        for i in range(3):
            self.assertEqual(
                self.proxy.WriteAttributeCounterCount, 0 + i * 3)
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.proxy.BenchmarkScalarAttribute
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.proxy.BenchmarkSpectrumAttribute
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.proxy.BenchmarkImageAttribute
            self.proxy.BenchmarkCommand()

        t2 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t1)
        self.proxy.ResetCounters()
        t3 = self.proxy.TimeSinceReset
        self.assertTrue(t2 > t3)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)

    def test_ScalarReadsCount(self):
        """Test for ScalarReadsCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ScalarReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkScalarAttribute
            self.assertEqual(self.proxy.ScalarReadsCount, i + 1)

    def test_SpectrumReadsCount(self):
        """Test for SpectrumReadsCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkSpectrumAttribute
            self.assertEqual(self.proxy.SpectrumReadsCount, i + 1)

    def test_ImageReadsCount(self):
        """Test for ImageReadsCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ImageReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkImageAttribute
            self.assertEqual(self.proxy.ImageReadsCount, i + 1)

    def test_ScalarWritesCount(self):
        """Test for ScalarWritesCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ScalarWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.assertEqual(self.proxy.ScalarWritesCount, i + 1)

    def test_SpectrumWritesCount(self):
        """Test for SpectrumWritesCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkSpectrumAttribute = np.zeros(
                shape=[i * 10 + 1], dtype=float)
            self.assertEqual(self.proxy.SpectrumWritesCount, i + 1)

    def test_ImageWritesCount(self):
        """Test for ImageWritesCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ImageWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkImageAttribute = np.zeros(
                shape=[i * 10 + 1, i * 20 + 1], dtype=float)
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)

    def test_CommandCallsCount(self):
        """Test for CommandCallsCount"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.CommandCallsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkCommand()
            self.assertEqual(self.proxy.CommandCallsCount, i + 1)

    def test_TimeSinceReset(self):
        """Test for TimeSinceReset"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        tbr1 = time.time()
        self.proxy.ResetCounters()
        tar1 = time.time()

        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)
        self.assertEqual(self.proxy.ReadAttributeHardwareCount, 2)
        self.assertEqual(self.proxy.AlwaysExecutedHookCount, 3)
        self.assertEqual(self.proxy.ScalarReadsCount, 0)
        self.assertEqual(self.proxy.ScalarWritesCount, 0)
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)
        self.assertEqual(self.proxy.CommandCallsCount, 0)
        self.assertEqual(self.proxy.WriteAttributeCounterCount, 0)

        for i in range(3):
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.proxy.BenchmarkScalarAttribute
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.proxy.BenchmarkSpectrumAttribute
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.proxy.BenchmarkImageAttribute
            self.proxy.BenchmarkCommand()

        tbr2 = time.time()
        tsr = self.proxy.TimeSinceReset
        tar2 = time.time()
        self.assertTrue(tbr2 - tar1 < tsr)
        self.assertTrue(tar2 - tbr1 > tsr)

    def test_BenchmarkSpectrumAttribute(self):
        """Test for BenchmarkSpectrumAttribute"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)

        for i in range(10):
            wvl = np.ones(
                shape=[1 + i * 10], dtype=float)
            self.proxy.BenchmarkSpectrumAttribute = wvl
            self.assertEqual(self.proxy.SpectrumWritesCount, i + 1)
            rvl = self.proxy.BenchmarkSpectrumAttribute
            self.assertEqual(self.proxy.SpectrumReadsCount, i + 1)
            self.assertEqual(list(wvl), list(rvl))

    def test_BenchmarkImageAttribute(self):
        """Test for BenchmarkImageAttribute"""
        print("Run: %s.%s() " % (
            self.__class__.__name__, sys._getframe().f_code.co_name))
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ImageReadsCount, 0)
        self.assertEqual(self.proxy.ImageWritesCount, 0)

        for i in range(10):
            wvl = np.ones(
                shape=[1 + i * 10, 1 + i * 20], dtype=float)
            self.proxy.BenchmarkImageAttribute = wvl
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)
            rvl = self.proxy.BenchmarkImageAttribute
            self.assertEqual(self.proxy.ImageReadsCount, i + 1)
            if isinstance(rvl, np.ndarray):
                self.assertEqual(wvl.shape, rvl.shape)
                for i in range(wvl.shape[0]):
                    self.assertEqual(list(wvl[i, :]), list(rvl[i, :]))
            else:
                # workaround for pytango without numpy
                self.assertEqual(wvl.shape[0], len(rvl))
                self.assertEqual(wvl.shape[1], len(rvl[0]))
                for i in range(wvl.shape[0]):
                    self.assertEqual(list(wvl[i, :]), list(rvl[i]))


def main():
    """ main function"""
    unittest.main()


# Main execution
if __name__ == "__main__":
    main()
