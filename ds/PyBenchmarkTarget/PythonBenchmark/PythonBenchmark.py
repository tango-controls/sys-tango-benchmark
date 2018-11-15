# -*- coding: utf-8 -*-
#
# This file is part of the PythonBenchmark project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Benchmark device

Benchmark device for counting attribute, command and pipe calls
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(PythonBenchmark.additionnal_import) ENABLED START #
import numpy as np
import time
# PROTECTED REGION END #    //  PythonBenchmark.additionnal_import

__all__ = ["PythonBenchmark", "main"]


class PythonBenchmark(Device):
    """
    Benchmark device for counting attribute, command and pipe calls
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(PythonBenchmark.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  PythonBenchmark.class_variable

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
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(PythonBenchmark.init_device) ENABLED START #
        self.__always_executed_hook_count = 0
        self.__read_attribute_hardware_count = 0
        self.__write_attribute_counter_count = 0
        self.__read_attribute_counter_count = 0

        self.__scalar_reads_count = 0
        self.__spectrum_reads_count = 0
        self.__image_reads_count = 0

        self.__scalar_writes_count = 0
        self.__spectrum_writes_count = 0
        self.__image_writes_count = 0

        self.__command_calls_count = 0

        self.__reset_time = time.time()

        self.__benchmark_scalar_attribute = 0.0
        self.__benchmark_spectrum_attribute = np.zeros(
            shape=[1024], dtype=float)
        self.__benchmark_image_attribute = np.zeros(
            shape=[1024, 2048], dtype=float)
        # PROTECTED REGION END #    //  PythonBenchmark.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(PythonBenchmark.always_executed_hook) ENABLED START #
        self.__always_executed_hook_count += 1
        # PROTECTED REGION END #    //  PythonBenchmark.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(PythonBenchmark.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PythonBenchmark.delete_device

    def dev_state(self):
        # PROTECTED REGION ID(PythonBenchmark.dev_state) ENABLED START #
        argout = PyTango.DevState.ON
        return argout
        # PROTECTED REGION END #    //  PythonBenchmark.dev_state

    def dev_status(self):
        # PROTECTED REGION ID(PythonBenchmark.dev_status) ENABLED START #
        self.argout = "State is ON"
        self.set_status(self.argout)
        self.__status = Device.dev_status(self)
        return self.__status
        # PROTECTED REGION END #    //  PythonBenchmark.dev_status

    def read_attr_hardware(self, data):
        # PROTECTED REGION ID(PythonBenchmark.read_attr_hardware) ENABLED START #
        self.__write_attribute_counter_count += 1 
        # PROTECTED REGION END #    //  PythonBenchmark.read_attr_hardware


    # ------------------
    # Attributes methods
    # ------------------

    def read_BenchmarkScalarAttribute(self):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkScalarAttribute_read) ENABLED START #
        self.__scalar_reads_count += 1
        return self.__benchmark_scalar_attribute
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkScalarAttribute_read

    def write_BenchmarkScalarAttribute(self, value):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkScalarAttribute_write) ENABLED START #
        self.__scalar_writes_count += 1
        self.__benchmark_scalar_attribute = value
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkScalarAttribute_write

    def read_AlwaysExecutedHookCount(self):
        # PROTECTED REGION ID(PythonBenchmark.AlwaysExecutedHookCount_read) ENABLED START #
        return self.__always_executed_hook_count
        # PROTECTED REGION END #    //  PythonBenchmark.AlwaysExecutedHookCount_read

    def read_ReadAttributeHardwareCount(self):
        # PROTECTED REGION ID(PythonBenchmark.ReadAttributeHardwareCount_read) ENABLED START #
        return self.__read_attribute_hardware_count
        # PROTECTED REGION END #    //  PythonBenchmark.ReadAttributeHardwareCount_read

    def read_WriteAttributeCounterCount(self):
        # PROTECTED REGION ID(PythonBenchmark.WriteAttributeCounterCount_read) ENABLED START #
        return self.__read_attribute_counter_count
        # PROTECTED REGION END #    //  PythonBenchmark.WriteAttributeCounterCount_read

    def read_ScalarReadsCount(self):
        # PROTECTED REGION ID(PythonBenchmark.ScalarReadsCount_read) ENABLED START #
        return self.__scalar_reads_count
        # PROTECTED REGION END #    //  PythonBenchmark.ScalarReadsCount_read

    def read_SpectrumReadsCount(self):
        # PROTECTED REGION ID(PythonBenchmark.SpectrumReadsCount_read) ENABLED START #
        return self.__spectrum_reads_count
        # PROTECTED REGION END #    //  PythonBenchmark.SpectrumReadsCount_read

    def read_ImageReadsCount(self):
        # PROTECTED REGION ID(PythonBenchmark.ImageReadsCount_read) ENABLED START #
        return self.__image_reads_count
        # PROTECTED REGION END #    //  PythonBenchmark.ImageReadsCount_read

    def read_ScalarWritesCount(self):
        # PROTECTED REGION ID(PythonBenchmark.ScalarWritesCount_read) ENABLED START #
        return self.__scalar_writes_count
        # PROTECTED REGION END #    //  PythonBenchmark.ScalarWritesCount_read

    def read_SpectrumWritesCount(self):
        # PROTECTED REGION ID(PythonBenchmark.SpectrumWritesCount_read) ENABLED START #
        return self.__spectrum_writes_count
        # PROTECTED REGION END #    //  PythonBenchmark.SpectrumWritesCount_read

    def read_ImageWritesCount(self):
        # PROTECTED REGION ID(PythonBenchmark.ImageWritesCount_read) ENABLED START #
        return self.__image_writes_count
        # PROTECTED REGION END #    //  PythonBenchmark.ImageWritesCount_read

    def read_CommandCallsCount(self):
        # PROTECTED REGION ID(PythonBenchmark.CommandCallsCount_read) ENABLED START #
        return self.__command_calls_count
        # PROTECTED REGION END #    //  PythonBenchmark.CommandCallsCount_read

    def read_TimeSinceReset(self):
        # PROTECTED REGION ID(PythonBenchmark.TimeSinceReset_read) ENABLED START #
        return time.time() - self.__reset_time
        # PROTECTED REGION END #    //  PythonBenchmark.TimeSinceReset_read

    def read_BenchmarkSpectrumAttribute(self):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkSpectrumAttribute_read) ENABLED START #
        self.__spectrum_reads_count += 1
        return self.__benchmark_spectrum_attribute
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkSpectrumAttribute_read

    def write_BenchmarkSpectrumAttribute(self, value):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkSpectrumAttribute_write) ENABLED START #
        self.__spectrum_writes_count += 1
        self.__benchmark_spectrum_attribute = value
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkSpectrumAttribute_write

    def read_BenchmarkImageAttribute(self):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkImageAttribute_read) ENABLED START #
        self.__image_reads_count += 1
        return self.__benchmark_image_attribute
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkImageAttribute_read

    def write_BenchmarkImageAttribute(self, value):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkImageAttribute_write) ENABLED START #
        self.__image_writes_count += 1
        self.__benchmark_image_attribute = value
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkImageAttribute_write


    # -------------
    # Pipes methods
    # -------------

    def read_BenchmarkPipe(self):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkPipe_read) ENABLED START #
        return dict(x=0,y=0)
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkPipe_read

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def BenchmarkCommand(self):
        # PROTECTED REGION ID(PythonBenchmark.BenchmarkCommand) ENABLED START #
        self.__command_calls_count += 1
        # PROTECTED REGION END #    //  PythonBenchmark.BenchmarkCommand

    @command(
    dtype_in='int', 
    doc_in="spectrum size", 
    )
    @DebugIt()
    def SetSpectrumSize(self, argin):
        # PROTECTED REGION ID(PythonBenchmark.SetSpectrumSize) ENABLED START #
        self.__benchmark_spectrum_attribute = np.zeros(
            shape=[argin], dtype=float)
        # PROTECTED REGION END #    //  PythonBenchmark.SetSpectrumSize

    @command(
    dtype_in=('int',), 
    doc_in="image size", 
    )
    @DebugIt()
    def SetImageSize(self, argin):
        # PROTECTED REGION ID(PythonBenchmark.SetImageSize) ENABLED START #
        self.__benchmark_image_attribute = np.zeros(
            shape=[argin[0], argin[1]], dtype=float)
        # PROTECTED REGION END #    //  PythonBenchmark.SetImageSize

    @command(
    )
    @DebugIt()
    def ResetCounters(self):
        # PROTECTED REGION ID(PythonBenchmark.ResetCounters) ENABLED START #
        self.__always_executed_hook_count = 0
        self.__read_attribute_hardware_count = 0
        self.__write_attribute_counter_count = 0
        self.__read_attribute_counter_count = 0

        self.__scalar_reads_count = 0
        self.__spectrum_reads_count = 0
        self.__image_reads_count = 0

        self.__scalar_writes_count = 0
        self.__spectrum_writes_count = 0
        self.__image_writes_count = 0

        self.__command_calls_count = 0
        self.__reset_time = time.time()
        # PROTECTED REGION END #    //  PythonBenchmark.ResetCounters

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(PythonBenchmark.main) ENABLED START #
    return run((PythonBenchmark,), args=args, **kwargs)
    # PROTECTED REGION END #    //  PythonBenchmark.main

if __name__ == '__main__':
    main()
