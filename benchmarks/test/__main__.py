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

if os.path.isfile(
        "%s/DeviceServers/CppBenchmarkTarget"
        % expanduser("~")) or \
        whichcraft.which("CppBenchmarkTarget") is not None:
    CPPSERVER = True
else:
    print("Warning: CppBenchmarkTarget cannot be found")
    CPPSERVER = False

if os.path.isfile(
        "../ds/JavaBenchmarkTarget/target/JavaBenchmarkTarget-1.0.jar"):
    JAVASERVER = True
else:
    print("Warning: JavaBenchmarkTarget cannot be found")
    JAVASERVER = False


if CPPSERVER and JAVASERVER:
    import BenchmarkRunner_test
    from BenchmarkRunner_test import BenchmarkRunnerTest


__all__ = []

if CPPSERVER and JAVASERVER:
    __all__.append(BenchmarkRunnerTest)


if CPPSERVER and JAVASERVER:
    BenchmarkRunner_test.main()
