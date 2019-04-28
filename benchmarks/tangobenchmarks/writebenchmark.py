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

import numpy as np

from . import utils

from multiprocessing import Queue

from tangobenchmarks.client.python.write import Worker
from tangobenchmarks.utility.benchmark import common_main


class WriteBenchmark(utils.Benchmark):
    """  master class for write benchmark
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
        self.__period = options.period
        #: (:obj:`int`) number of clients
        self.__clients = options.clients
        #: (:obj:`float` or :class:`numpy.array`) attribute value to write
        self.__value = 0
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(self.__clients)]

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
                (value * (shape[0] // max(1, len(value) - 1) + 1))[:shape[0]]
            ).reshape(shape)
        elif len(shape) == 2:
            self.__value = np.array(
                (
                    value * (shape[0] * shape[1] // max(1, len(value) - 1) + 1)
                )[:shape[0] * shape[1]]
            ).reshape(shape)

        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            Worker(i, self.__device, self.__attribute, self.__period,
                   self.__value, self._qresults[i])
            for i in range(self.__clients)
        ]


def _add_arguments(parser):
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, "
        "default: BenchmarkScalarAttribute")
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


def _update_options(options):
    if not options.attribute:
        options.attribute = "BenchmarkScalarAttribute"


def main(**kargs):
    common_main(
        kargs,
        _add_arguments,
        _update_options,
        benchmark_class=WriteBenchmark,
        description=(
            'perform check if and how a number of simultaneous '
            'clients affect attributes write speed'),
        title="Write Benchmark",
        header_text="write")


if __name__ == "__main__":
    main()
