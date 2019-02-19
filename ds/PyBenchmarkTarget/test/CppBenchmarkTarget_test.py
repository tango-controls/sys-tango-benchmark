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

"""Contain the tests for the Benchmark device."""

import sys
import os
import unittest
import tango
from os.path import expanduser
from PyBenchmarkTarget_test import PyBenchmarkTargetDeviceTest

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

#: python3 running
PY3 = (sys.version_info > (3,))


# Device test case
class CppBenchmarkTargetDeviceTest(PyBenchmarkTargetDeviceTest):
    """Test case for packet generation."""

    def __init__(self, methodName):
        """ constructor

        :param methodName: name of the test method
        """

        PyBenchmarkTargetDeviceTest.__init__(self, methodName)
        self.instance = 'TEST'
        self.device = 'test/cppbenchmarktarget/000'
        self.new_device_info_benchmark = tango.DbDevInfo()
        self.new_device_info_benchmark._class = "CppBenchmarkTarget"
        self.new_device_info_benchmark.server = "CppBenchmarkTarget/%s" % \
                                                self.instance
        self.new_device_info_benchmark.name = self.device
        self.proxy = None

        home = expanduser("~")
        serverfile = "%s/DeviceServers/CppBenchmarkTarget" % home
        if os.path.isfile(serverfile):
            self._startserver = "%s %s &" % (serverfile, self.instance)
        else:
            self._startserver = "CppBenchmarkTarget %s &" % self.instance
        self._grepserver = \
            "ps -ef | grep 'CppBenchmarkTarget %s' | grep -v grep" % \
            self.instance


def main():
    """ main function"""
    unittest.main()


# Main execution
if __name__ == "__main__":
    main()
