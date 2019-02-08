#!/usr/bin/env python

# Copyright (C) 2018  Jan Kotanski, S2Innovation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 3
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

import argparse
import sys
import PyTango
import time
import numpy as np

from argparse import RawTextHelpFormatter
from multiprocessing import Process, Queue

from . import release
from . import utils

TIMEOUTS = False


class WriteWorker(Process):
    """ write worker instance
    """

    def __init__(self, wid, device, pipe, period, value, qresult):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param device: device name
        :type device: :obj:`str`
        :param pipe: pipe name
        :type pipe: :obj:`str`
        :param period: time period
        :type period: :obj:`float`
        :param value:  pipe value
        :type value: :class:`numpy.ndarray`
        :param qresult: queue with result
        :type qresult: :class:`Queue.Queue` or `queue.queue`

        """
        Process.__init__(self)

        # : (:obj:`int`) worker id
        self.__wid = wid
        # : (:obj:`float`) time period in seconds
        self.__period = float(period)
        #: (:obj:`str`) device proxy
        self.__device = device
        #: (:obj:`str`) device pipe name
        self.__pipe = pipe
        #: (:obj:`float` or :class:`np.array`) device pipe value
        self.__value = value
        # : (:class:`PyTango.PipeProxy`) pipe proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0

    def run(self):
        """ worker thread
        """
        self.__proxy = PyTango.DeviceProxy(self.__device)
        if TIMEOUTS:
            if not utils.Starter.checkDevice(self.__proxy):
                raise Exception(
                    "Device %s connection failed" % self.__device)
        stime = time.time()
        etime = stime
        while etime - stime < self.__period:
            self.__proxy.write_pipe(self.__pipe, self.__value)
            etime = time.time()
            self.__counter += 1
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime))


class ReadWorker(Process):
    """ read worker instance
    """

    def __init__(self, wid, device, pipe, period, qresult):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param device: device name
        :type device: :obj:`str`
        :param pipe: pipe name
        :type pipe: :obj:`str`
        :param period: time period
        :type period: :obj:`float`
        :param qresult: queue with result
        :type qresult: :class:`Queue.Queue` or `queue.queue`

        """
        Process.__init__(self)

        # : (:obj:`int`) worker id
        self.__wid = wid
        # : (:obj:`float`) time period in seconds
        self.__period = float(period)
        #: (:obj:`str`) device proxy
        self.__device = device
        #: (:obj:`str`) device pipe name
        self.__pipe = pipe
        # : (:class:`PyTango.PipeProxy`) pipe proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0

    def run(self):
        """ worker thread
        """
        self.__proxy = PyTango.DeviceProxy(self.__device)
        stime = time.time()
        etime = stime
        while etime - stime < self.__period:
            self.__proxy.read_pipe(self.__pipe)
            etime = time.time()
            self.__counter += 1
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime))


class WritePipeBenchmark(utils.Benchmark):
    """  master class for pipe benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        utils.Benchmark.__init__(self)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device pipe name
        self.__pipe = options.pipe
        #: (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`int`) number of clients
        self.__clients = int(options.clients)
        #: (:obj:`float` or :class:`numpy.array`) pipe value to pipe
        self.__value = (
            'PipeBlob',
            [
                {'name': 'DevLong64', 'value': 123, },
                {'name': 'DevULong', 'value': np.uint32(123)},
                {'name': 'DevVarUShortArray',
                 'value': range(5), 'dtype': ('uint16',)},
                {'name': 'DevVarDoubleArray',
                 'value': [1.11, 2.22], 'dtype': ('float64',)},
                {'name': 'DevBoolean', 'value': True},
            ]
        )
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(self.__clients)]

        size = max(1, int(options.size))
        value1 = (self.__value[1] *
                  (size // max(1, len(self.__value[1]) - 1) + 1))[:size]

        for i in range(len(value1)):
            value1[i] = dict(value1[i])
            value1[i]["name"] = str(i) + "_" + value1[i]["name"]

        self.__value = self.__value[0], tuple(value1)

        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            WriteWorker(i, self.__device, self.__pipe, self.__period,
                        self.__value, self._qresults[i])
            for i in range(self.__clients)
        ]


class ReadPipeBenchmark(utils.Benchmark):
    """  master class for pipe benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        utils.Benchmark.__init__(self)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device pipe name
        self.__pipe = options.pipe
        #: (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`int`) number of clients
        self.__clients = int(options.clients)
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(self.__clients)]

        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            ReadWorker(i, self.__device, self.__pipe, self.__period,
                       self._qresults[i])
            for i in range(self.__clients)
        ]


def main(**kargs):
    """ the main function
    """

    parser = argparse.ArgumentParser(
        description='perform check if and how a number of simultaneous '
        'clients affect pipes pipe speed',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        dest="version",
        help="program version")
    parser.add_argument(
        "-d", "--device", dest="device",
        help="device on which the test will be performed")
    parser.add_argument(
        "-n", "--numbers-of-clients", dest="clients", default="1",
        help="numbers of clients to be spawned separated by ',' .\n"
        "The numbers can be given as python slices <start>:<stop>:<step> ,\n"
        "e.g. 1,23,45:50:2 , default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, default: 10")
    parser.add_argument(
        "-i", "--pipe", dest="pipe",
        default="BenchmarkPipe",
        help="pipe which will be read/write, default: BenchmarkPipe")
    parser.add_argument(
        "-s", "--size", dest="size",
        default="1",
        help="pipe size, default: 1, e.g. -s 134 ")
    parser.add_argument(
        "-f", "--csv-file", dest="csvfile",
        help="pipe output in a CSV file")
    parser.add_argument(
        "-t", "--title", dest="title",
        default="Pipe Benckmark",
        help="benchmark title")
    parser.add_argument(
        "--description", dest="description",
        default="Speed test",
        help="benchmark description")
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true", default=False,
        help="verbose mode")

    if not kargs:
        options = parser.parse_args()
    else:
        options = parser.parse_args([])
        for ky, vl in kargs.items():
            setattr(options, ky, vl)

    clients = []

    if options.version:
        print(release.version)
        sys.exit(0)

    if not options.device:
        parser.print_help()
        print("")
        sys.exit(255)

    if not options.clients:
        options.clients = "1"
    else:
        try:
            sclients = options.clients.split(',')
            for sc in sclients:
                if ":" in sc:
                    sld = list(map(int, sc.split(":")))
                    clients.extend(list(range(*sld)))
                else:
                    clients.append(int(sc))
        except Exception:
            print("Error: number of clients is not an integer")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.period:
        options.period = "10"
    else:
        try:
            float(options.period)
        except Exception:
            print("Error: test period is not a number")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.pipe:
        options.pipe = "BenchmarkPipe"

    headers = [
        "Run no.",
        "Sum counts [write]", "error [write]",
        "Sum Speed [write/s]", "error [write/s]",
        "Counts [write]", "error [write]",
        "Speed [write/s]", "error [write/s]",
        "No. ", "  Time [s]  ", "error [s]"
    ]

    if options.csvfile:
        csvo = utils.CSVOutput(options.csvfile, options)
        csvo.printInfo()
        csvo.printHeader(headers)

    rst = utils.RSTOutput(options)
    rst.printInfo()
    rst.printHeader(headers)

    for i, cl in enumerate(clients):
        options.clients = cl
        bm = WritePipeBenchmark(options=options)
        bm.start()
        bm.fetchResults(options.verbose)
        out = bm.output(False)
        record = [
            str(i),
            out["sumcounts"], out["err_sumcounts"],
            out["sumspeed"], out["err_sumspeed"],
            out["counts"], out["err_counts"],
            out["speed"], out["err_speed"],
            cl,
            out["time"], out["err_time"]
        ]
        rst.printLine(record)
        if options.csvfile:
            csvo.printLine(record)

    rst.printEnd()

    headers = [
        "Run no.",
        "Sum counts [read]", "error [read]",
        "Sum Speed [read/s]", "error [read/s]",
        "Counts [read]", "error [read]",
        "Speed [read/s]", "error [read/s]",
        "No. ", "  Time [s]  ", "error [s]"
    ]

    if options.csvfile:
        csvo.printHeader(headers)

    rst.printHeader(headers)

    for i, cl in enumerate(clients):
        options.clients = cl
        bm = ReadPipeBenchmark(options=options)
        bm.start()
        bm.fetchResults(options.verbose)
        out = bm.output(False)
        record = [
            str(i),
            out["sumcounts"], out["err_sumcounts"],
            out["sumspeed"], out["err_sumspeed"],
            out["counts"], out["err_counts"],
            out["speed"], out["err_speed"],
            cl,
            out["time"], out["err_time"]
        ]
        rst.printLine(record)
        if options.csvfile:
            csvo.printLine(record)

    rst.printEnd()

    if options.csvfile:
        csvo.printEnd()


if __name__ == "__main__":
    main()
