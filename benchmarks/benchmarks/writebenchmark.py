#!/usr/bin/env python

# Copyright (C) 2018  Jan Kotanski, S2Innovation
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

import argparse
import sys
import PyTango
import time
import numpy as np

from argparse import RawTextHelpFormatter
from multiprocessing import Process, Queue

from . import release
from . import utils


class Worker(Process):
    """ worker instance
    """

    def __init__(self, wid, device, attribute, period, value, qresult):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param device: device name
        :type device: :obj:`str`
        :param attribute: attribute name
        :type attribute: :obj:`str`
        :param attribute: time period
        :type attribute: :obj:`float`
        :param value:  attribute value
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
        #: (:obj:`str`) device attribute name
        self.__attribute = attribute
        #: (:obj:`float` or :class:`np.array`) device attribute value
        self.__value = value
        # : (:class:`PyTango.AttributeProxy`) attribute proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0

    def run(self):
        """ worker thread
        """
        self.__proxy = PyTango.AttributeProxy(
            "%s/%s" % (self.__device, self.__attribute))
        stime = time.time()
        etime = stime
        while etime - stime < self.__period:
            self.__proxy.write(self.__value)
            etime = time.time()
            self.__counter += 1
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime))


class WriteBenchmark():
    """  master class for read benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device attribute name
        self.__attribute = options.attribute
        #: (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`int`) number of clients
        self.__clients = int(options.clients)
        #: (:obj:`float` or :class:`numpy.array`) attribute value to write
        self.__value = 0
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self.__results = [Queue() for i in range(self.__clients)]

        try:
            shape = list(map(int, options.shape.split(',')))
        except Exception:
            shape = None

        try:
            value = list(
                map(float, options.value.replace('m', '-').split(',')))
        except Exception:
            value = [0]
        if shape is None:
            if len(value) == 1:
                self.__value = value[0]
            elif len(value) > 1:
                self.__value = np.array(value)
        elif len(shape) == 1:
            self.__value = np.array(
                (value * (shape[0] / max(1, len(value) - 1)))[:shape[0]]
            ).reshape(shape)
        elif len(shape) == 2:
            self.__value = np.array(
                (
                    value * (shape[0] * shape[1] / max(1, len(value) - 1))
                )[:shape[0] * shape[1]]
            ).reshape(shape)

        #: (:obj:`list` < :class:`Worker` >) process worker
        self.__workers = [
            Worker(i, self.__device, self.__attribute, self.__period,
                   self.__value, self.__results[i])
            for i in range(self.__clients)
        ]

    def start(self):
        """ start benchmark
        """
        for wk in self.__workers:
            wk.start()
        for wk in self.__workers:
            wk.join()

    def output(self):
        """ create output
        """
        for qres in self.__results:
            try:
                res = qres.get(block=False)
                print("id: %s, counts: %s, time: %s s, speed: %s counts/s" % (
                    res.wid, res.counts, res.ctime, res.speed()))
            except Exception:
                pass


def main():
    """ the main function
    """

    parser = argparse.ArgumentParser(
        description='perform check if and how a number of simultaneous '
        'clients affect attributes write speed',
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
        "-n", "--number-of-clients", dest="clients", default="1",
        help="number of clients to be spawned, default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, default: 10")
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, default: BenchmarkScalarAttribute")
    parser.add_argument(
        "-s", "--attribute-shape", dest="shape",
        default="",
        help="attribute which will be read, default: '', "
        "e.g. -s '128,64' ")
    parser.add_argument(
        "-w", "--attribute-value", dest="value",
        default="0",
        help="value to be written, default: 0, "
        "e.g. -w '12.28,12.234,m123.3' where m123.3 means -123.3")

    options = parser.parse_args()

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
            int(options.clients)
        except Exception:
            print("Error: number of clients is not an integer")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.period:
        options.period = "10"
    else:
        try:
            float(options.clients)
        except Exception:
            print("Error: test period is not a number")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.attribute:
        options.attribute = "BenchmarkScalarAttribute"

    rdbm = WriteBenchmark(options=options)
    rdbm.start()
    rdbm.output()


if __name__ == "__main__":
    main()
