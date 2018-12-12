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

import os
from os.path import expanduser
import whichcraft

import PyBenchmarkTarget_test
from PyBenchmarkTarget_test import PyBenchmarkTargetDeviceTest

if os.path.isfile(
        "%s/DeviceServers/CppBenchmarkTarget"
        % expanduser("~")) or \
        whichcraft.which("CppBenchmarkTarget") is not None:
    CPPSERVER = True
else:
    print("Warning: CppBenchmarkTarget cannot be found")
    CPPSERVER = False

if os.path.isfile(
        "../JavaBenchmarkTarget/target/JavaBenchmarkTarget-1.0.jar"):
    JAVASERVER = True
else:
    print("Warning: JavaBenchmarkTarget cannot be found")
    JAVASERVER = False


if CPPSERVER:
    import CppBenchmarkTarget_test
    from CppBenchmarkTarget_test import CppBenchmarkTargetDeviceTest

if JAVASERVER:
    import JavaBenchmarkTarget_test
    from JavaBenchmarkTarget_test import JavaBenchmarkTargetDeviceTest

__all__ = [PyBenchmarkTargetDeviceTest]

if CPPSERVER:
    __all__.append(CppBenchmarkTargetDeviceTest)

if JAVASERVER:
    __all__.append(JavaBenchmarkTargetDeviceTest)

PyBenchmarkTarget_test.main()
if CPPSERVER:
    CppBenchmarkTarget_test.main()
if JAVASERVER:
    JavaBenchmarkTarget_test.main()
