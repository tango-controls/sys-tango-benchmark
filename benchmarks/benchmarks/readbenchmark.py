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

from argparse import RawTextHelpFormatter
from multiprocessing import Process, Queue

from . import release
from . import utils

TIMEOUTS = False


class Worker(Process):
    """ worker instance
    """

    def __init__(self, wid, device, attribute, period, qresult):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param device: device name
        :type device: :obj:`str`
        :param attribute: attribute name
        :type attribute: :obj:`str`
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
        #: (:obj:`str`) device attribute name
        self.__attribute = attribute
        # : (:class:`PyTango.AttributeProxy`) attribute proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0
        # : (:obj:`int`) error counter
        self.__error = 0

    def run(self):
        """ worker thread
        """
        self.__proxy = PyTango.AttributeProxy(
            "%s/%s" % (self.__device, self.__attribute))
        if TIMEOUTS:
            if not utils.Starter.checkDevice(self.__proxy):
                raise Exception(
                    "Device %s connection failed" % self.__device)

        stime = time.time()
        etime = stime
        while etime - stime < self.__period:
            try:
                self.__proxy.read()
            except Exception:
                self.__error += 1
            else:
                etime = time.time()
                self.__counter += 1
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime))


class ReadBenchmark(utils.Benchmark):
    """  master class for read benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """
        utils.Benchmark.__init__(self)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device attribute name
        self.__attribute = options.attribute
        #: (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`int`) number of clients
        self.__clients = int(options.clients)
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(self.__clients)]
        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            Worker(i, self.__device, self.__attribute, self.__period,
                   self._qresults[i])
            for i in range(self.__clients)
        ]


def main(**kargs):
    """ the main function
    """
    parser = argparse.ArgumentParser(
        description='perform check if and how a number of simultaneous '
        'clients affect attributes reads speed',
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
        help="numbers of clients to be "
        "spawned separated by ',' .\n"
        "The numbers can be given as python "
        "slices <start>:<stop>:<step> ,\n"
        "e.g. 1,23,45:50:2 , default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, "
        "default: 10")
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, "
        "default: BenchmarkScalarAttribute")
    parser.add_argument(
        "-f", "--csv-file", dest="csvfile",
        help="write output in a CSV file")
    parser.add_argument(
        "-t", "--title", dest="title",
        default="Read Benckmark",
        help="benchmark title")
    parser.add_argument(
        "--description", dest="description",
        default="Speed test",
        help="benchmark description")
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true",
        default=False,
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
        except Exception as e:
            print("Error: number of clients is not an integer")
            if options.verbose:
                print(str(e))
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.period:
        options.period = "10"
    else:
        try:
            float(options.period)
        except Exception as e:
            print("Error: test period is not a number")
            if options.verbose:
                print(str(e))
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.attribute:
        options.attribute = "BenchmarkScalarAttribute"

    headers = [
        "Run no.",
        "Sum counts [read]", "error [read]",
        "Sum Speed [read/s]", "error [read/s]",
        "Counts [read]", "error [read]",
        "Speed [read/s]", "error [read/s]",
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
        bm = ReadBenchmark(options=options)
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
