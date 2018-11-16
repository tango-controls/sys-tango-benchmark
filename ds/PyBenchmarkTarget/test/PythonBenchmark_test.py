#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the PythonBenchmark project
#
#
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
class PythonBenchmarkDeviceTest(unittest.TestCase):
    """Test case for packet generation."""

    def __init__(self, methodName):
        """ constructor
        :param methodName: name of the test method
        """
        unittest.TestCase.__init__(self, methodName)
        self.instance = 'TEST'
        self.device = 'test/pythonbenchmark/000'
        self.new_device_info_benchmark = PyTango.DbDevInfo()
        self.new_device_info_benchmark._class = "PythonBenchmark"
        self.new_device_info_benchmark.server = "PythonBenchmark/%s" % \
                                                self.instance
        self.new_device_info_benchmark.name = self.device
        self.proxy = None

    def setUp(self):
        print("tearing down ...")
        db = PyTango.Database()
        db.add_device(self.new_device_info_benchmark)
        db.add_server(
            self.new_device_info_benchmark.server,
            self.new_device_info_benchmark)

        if sys.version_info > (3,):
            if os.path.isfile("../PythonBenchmark"):
                self._psub = subprocess.call(
                    "cd ..; python3 ./PythonBenchmark %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
            else:
                self._psub = subprocess.call(
                    "python3 PythonBenchmark %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
        else:
            if os.path.isfile("../PythonBenchmark"):
                self._psub = subprocess.call(
                    "cd ..; ./PythonBenchmark %s &" % self.instance,
                    stdout=None,
                    stderr=None, shell=True)
            else:
                self._psub = subprocess.call(
                    "PythonBenchmark %s &" % self.instance, stdout=None,
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
                # print(e)
                found = False
            cnt += 1
        print("")
        self.proxy = dp

    def tearDown(self):
        print("tearing down ...")
        db = PyTango.Database()
        db.delete_server(self.new_device_info_benchmark.server)

        pipe = subprocess.Popen(
            "ps -ef | grep 'PythonBenchmark %s'" % self.instance,
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
        self.assertEqual(self.proxy.State(), PyTango.DevState.ON)

    def test_Status(self):
        """Test for Status"""
        self.assertEqual(self.proxy.Status(), 'State is ON')

    def test_BenchmarkCommand(self):
        """Test for BenchmarkCommand"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.CommandCallsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkCommand()
            self.assertEqual(self.proxy.CommandCallsCount, i + 1)

    def test_SetSpectrumSize(self):
        """Test for SetSpectrumSize"""
        self.proxy.SetSpectrumSize(123)
        self.assertEqual(len(self.proxy.BenchmarkSpectrumAttribute), 123)
        self.proxy.SetSpectrumSize(1024)
        self.assertEqual(len(self.proxy.BenchmarkSpectrumAttribute), 1024)

    def test_SetImageSize(self):
        """Test for SetImageSize"""
        self.proxy.SetImageSize([123, 456])
        self.assertEqual(self.proxy.BenchmarkImageAttribute.shape,
                         (123, 456))
        self.proxy.SetImageSize([1024, 2096])
        self.assertEqual(self.proxy.BenchmarkImageAttribute.shape,
                         (1024, 2096))

    def test_ResetCounters(self):
        """Test for ResetCounters"""
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
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ScalarReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkScalarAttribute
            self.assertEqual(self.proxy.ScalarReadsCount, i + 1)

    def test_SpectrumReadsCount(self):
        """Test for SpectrumReadsCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.SpectrumReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkSpectrumAttribute
            self.assertEqual(self.proxy.SpectrumReadsCount, i + 1)

    def test_ImageReadsCount(self):
        """Test for ImageReadsCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ImageReadsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkImageAttribute
            self.assertEqual(self.proxy.ImageReadsCount, i + 1)

    def test_ScalarWritesCount(self):
        """Test for ScalarWritesCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ScalarWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkScalarAttribute = float(i)
            self.assertEqual(self.proxy.ScalarWritesCount, i + 1)

    def test_SpectrumWritesCount(self):
        """Test for SpectrumWritesCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.SpectrumWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkSpectrumAttribute = np.zeros(
                shape=[i*10], dtype=float)
            self.assertEqual(self.proxy.SpectrumWritesCount, i + 1)

    def test_ImageWritesCount(self):
        """Test for ImageWritesCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.ImageWritesCount, 0)

        for i in range(10):
            self.proxy.BenchmarkImageAttribute = np.zeros(
                shape=[i * 10, i * 20], dtype=float)
            self.assertEqual(self.proxy.ImageWritesCount, i + 1)

    def test_CommandCallsCount(self):
        """Test for CommandCallsCount"""
        self.proxy.ResetCounters()
        self.assertEqual(self.proxy.CommandCallsCount, 0)

        for i in range(10):
            self.proxy.BenchmarkCommand()
            self.assertEqual(self.proxy.CommandCallsCount, i + 1)

    def test_TimeSinceReset(self):
        """Test for TimeSinceReset"""
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
            self.assertEqual(wvl.shape, rvl.shape)
            for i in range(wvl.shape[0]):
                self.assertEqual(list(wvl[i, :]), list(rvl[i, :]))


# Main execution
if __name__ == "__main__":
    unittest.main()
