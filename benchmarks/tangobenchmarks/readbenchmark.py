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

from . import utils

from multiprocessing import Queue

from tangobenchmarks.client.python.read import Worker
from tangobenchmarks.utility.benchmark import common_main


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


def _add_arguments(parser):
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, "
        "default: BenchmarkScalarAttribute")


def _update_options(options):
    if not options.attribute:
        options.attribute = "BenchmarkScalarAttribute"


def main(**kargs):
    common_main(
        kargs,
        _add_arguments,
        _update_options,
        benchmark_class=ReadBenchmark,
        description=(
            'perform check if and how a number of simultaneous '
            'clients affect attributes reads speed'),
        title="Read Benchmark",
        header_text="read")


if __name__ == "__main__":
    main()
