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

""" Benchmark device

Benchmark device for counting attribute, command and pipe calls
"""

import tango
from tango import DebugIt, DevState
from tango.server import run
from tango.server import Device, DeviceMeta
from tango.server import attribute, command, pipe
from tango import AttrWriteType, PipeWriteType
import numpy as np
import time
from threading import Thread


__all__ = ["PyBenchmarkTarget", "main"]


class EventThread(Thread):

    """ thread which pushes events
    """

    def __init__(self, dvname, speriod):
        Thread.__init__(self)

        self.__speriod = speriod
        self.__dp = tango.DeviceProxy(dvname)
        self.errors = []
        self.running = True
        self.counter = 0
        self.finished = False

    def run(self):
        while self.running:
            try:
                self.__dp.PushScalarEvent()
                self.counter += 1
            except (tango.DevFailed, BaseException) as e:
                self.errors.append(str(e))
                # print(self.errors[-1])
            except Exception as e:
                self.errors.append(str(e))
                # print(self.errors[-1])
            if self.running:
                time.sleep(self.__speriod * 0.001)
        self.finished = True


class PyBenchmarkTarget(Device):

    """
    Benchmark device for counting attribute, command and pipe calls
    """
    __metaclass__ = DeviceMeta

    # ----------
    # Attributes
    # ----------

    BenchmarkScalarAttribute = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        doc="benchmark scalar attribute",
    )

    AlwaysExecutedHookCount = attribute(
        dtype='int',
        doc="always executed hook count",
    )

    ReadAttributeHardwareCount = attribute(
        dtype='int',
        doc="read attribute hardware count",
    )

    WriteAttributeCounterCount = attribute(
        dtype='int',
        doc="write attribute counter count",
    )

    ScalarReadsCount = attribute(
        dtype='int',
        doc="scalar reads count",
    )

    SpectrumReadsCount = attribute(
        dtype='int',
        doc="spectrum reads count",
    )

    ImageReadsCount = attribute(
        dtype='int',
        doc="image reads count",
    )

    ScalarWritesCount = attribute(
        dtype='int',
        doc="scalar writes count",
    )

    SpectrumWritesCount = attribute(
        dtype='int',
        doc="spectrum writes count",
    )

    ImageWritesCount = attribute(
        dtype='int',
        doc="image writes count",
    )

    CommandCallsCount = attribute(
        dtype='int',
        doc="command calls count",
    )

    TimeSinceReset = attribute(
        dtype='double',
        label="time since reset",
        unit="s",
        doc="time since reset",
    )

    PipeReadsCount = attribute(
        dtype='int',
        doc="pipe reads count",
    )

    PipeWritesCount = attribute(
        dtype='int',
        doc="pipe writes count",
    )

    EventSleepPeriod = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        unit="ms",
        doc="sleep period of the event thread in milliseconds",
    )

    ScalarEventsCount = attribute(
        dtype='int',
        doc="scalar events count",
    )

    BenchmarkSpectrumAttribute = attribute(
        dtype=('double',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096,
        doc="benchmark spectrum attribute",
    )

    BenchmarkImageAttribute = attribute(
        dtype=(('double',),),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4096, max_dim_y=4096,
        doc="benchmark image attribute",
    )

    # -----
    # Pipes
    # -----

    BenchmarkPipe = pipe(
        doc="benchmark pipe",
        access=PipeWriteType.PIPE_READ_WRITE
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.__always_executed_hook_count = 0
        self.__read_attribute_hardware_count = 0
        self.__write_attribute_counter_count = 0

        self.__scalar_reads_count = 0
        self.__spectrum_reads_count = 0
        self.__image_reads_count = 0
        self.__pipe_reads_count = 0

        self.__scalar_writes_count = 0
        self.__spectrum_writes_count = 0
        self.__image_writes_count = 0
        self.__pipe_writes_count = 0

        self.__command_calls_count = 0

        self.__event_sleep_period = 10.
        self.__scalar_events_count = 0

        self.__state = "ON"

        self.__reset_time = time.time()

        self.__benchmark_scalar_attribute = 0.0
        self.__benchmark_spectrum_attribute = np.zeros(
            shape=[1024], dtype=float)
        self.__benchmark_image_attribute = np.zeros(
            shape=[1024, 2048], dtype=float)

        self.__benchmark_pipe = (
            'PipeBlob',
            (
                {'name': 'DevLong64', 'value': 123, },
                {'name': 'DevULong', 'value': np.uint32(123)},
                {'name': 'DevVarUShortArray',
                 'value': range(5), 'dtype': ('uint16',)},
                {'name': 'DevVarDoubleArray',
                 'value': [1.11, 2.22], 'dtype': ('float64',)},
                {'name': 'DevBoolean', 'value': True},
            )
        )

        self.set_change_event("BenchmarkScalarAttribute", True, False)
        self.set_change_event("BenchmarkSpectrumAttribute", True, False)
        self.set_change_event("BenchmarkImageAttribute", True, False)

    def always_executed_hook(self):
        self.__always_executed_hook_count += 1

    def delete_device(self):
        pass

    @DebugIt()
    def dev_state(self):
        if self.__state == "ON":
            argout = DevState.ON
        else:
            argout = DevState.RUNNING
        return argout

    @DebugIt()
    def dev_status(self):
        self.argout = "State is %s" % self.__state
        self.set_status(self.argout)
        self.__status = Device.dev_status(self)
        return self.__status

    @DebugIt()
    def read_attr_hardware(self, data):
        self.__read_attribute_hardware_count += 1

    # ------------------
    # Attributes methods
    # ------------------

    def read_BenchmarkScalarAttribute(self):
        self.__scalar_reads_count += 1
        return self.__benchmark_scalar_attribute

    def write_BenchmarkScalarAttribute(self, value):
        self.__scalar_writes_count += 1
        self.__benchmark_scalar_attribute = value

    def read_AlwaysExecutedHookCount(self):
        return self.__always_executed_hook_count

    def read_ReadAttributeHardwareCount(self):
        return self.__read_attribute_hardware_count

    def read_WriteAttributeCounterCount(self):
        return (self.__scalar_writes_count +
                self.__spectrum_writes_count +
                self.__image_writes_count)

    def read_ScalarReadsCount(self):
        return self.__scalar_reads_count

    def read_SpectrumReadsCount(self):
        return self.__spectrum_reads_count

    def read_ImageReadsCount(self):
        return self.__image_reads_count

    def read_PipeReadsCount(self):
        return self.__pipe_reads_count

    def read_ScalarWritesCount(self):
        return self.__scalar_writes_count

    def read_SpectrumWritesCount(self):
        return self.__spectrum_writes_count

    def read_ImageWritesCount(self):
        return self.__image_writes_count

    def read_PipeWritesCount(self):
        return self.__pipe_writes_count

    def read_CommandCallsCount(self):
        return self.__command_calls_count

    def read_TimeSinceReset(self):
        return time.time() - self.__reset_time

    def read_EventSleepPeriod(self):
        return self.__event_sleep_period

    def write_EventSleepPeriod(self, value):
        self.__event_sleep_period = value

    def is_EventSleepPeriod_allowed(self, attr):
        if attr == attr.READ_REQ:
            return True
        else:
            return self.get_state() not in [DevState.RUNNING]

    def read_ScalarEventsCount(self):
        return self.__scalar_events_count

    def read_BenchmarkSpectrumAttribute(self):
        self.__spectrum_reads_count += 1
        return self.__benchmark_spectrum_attribute

    def write_BenchmarkSpectrumAttribute(self, value):
        self.__spectrum_writes_count += 1
        self.__benchmark_spectrum_attribute = value

    def read_BenchmarkImageAttribute(self):
        self.__image_reads_count += 1
        return self.__benchmark_image_attribute

    def write_BenchmarkImageAttribute(self, value):
        self.__image_writes_count += 1
        self.__benchmark_image_attribute = value

    # -------------
    # Pipes methods
    # -------------

    def read_BenchmarkPipe(self):
        self.__pipe_reads_count += 1
        return self.__benchmark_pipe

    def write_BenchmarkPipe(self, value):
        self.__pipe_writes_count += 1
        self.__benchmark_pipe = value

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def BenchmarkCommand(self):
        self.__command_calls_count += 1

    @command(
        dtype_in='int',
        doc_in="spectrum size",
    )
    @DebugIt()
    def SetSpectrumSize(self, argin):
        self.__benchmark_spectrum_attribute = np.zeros(
            shape=[argin], dtype=float)

    @command(
        dtype_in=('int',),
        doc_in="image size",
    )
    @DebugIt()
    def SetImageSize(self, argin):
        self.__benchmark_image_attribute = np.zeros(
            shape=[argin[0], argin[1]], dtype=float)

    @command(
    )
    @DebugIt()
    def ResetCounters(self):
        self.__always_executed_hook_count = 0
        self.__read_attribute_hardware_count = 0
        self.__write_attribute_counter_count = 0

        self.__scalar_reads_count = 0
        self.__spectrum_reads_count = 0
        self.__image_reads_count = 0
        self.__pipe_reads_count = 0

        self.__scalar_writes_count = 0
        self.__spectrum_writes_count = 0
        self.__image_writes_count = 0
        self.__pipe_writes_count = 0

        self.__command_calls_count = 0
        self.__reset_time = time.time()

    @command()
    @DebugIt()
    def StartScalarEvents(self):
        self.__scalar_events_count = 0
        self.__event_thread = EventThread(
            self.get_name(), self.__event_sleep_period)
        self.__event_thread.start()
        self.__state = "RUNNING"

    def is_StartScalarEvents_allowed(self):
        return self.get_state() not in [DevState.RUNNING]

    @command()
    @DebugIt()
    def StopScalarEvents(self):
        self.__event_thread.running = False
        while not self.__event_thread.finished:
            time.sleep(0.01)
        self.__event_thread.join()
        self.__state = "ON"
        self.__scalar_events_count = self.__event_thread.counter
        errors = self.__event_thread.errors
        if errors:
            print(errors)

    @command()
    @DebugIt()
    def PushScalarEvent(self):
        self.push_change_event(
            "BenchmarkScalarAttribute",
            self.__benchmark_scalar_attribute)

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((PyBenchmarkTarget,), args=args, **kwargs)


if __name__ == '__main__':
    main()
