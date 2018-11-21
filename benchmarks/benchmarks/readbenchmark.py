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

from argparse import RawTextHelpFormatter

from . import release


class ReadBenchmark():
    """  master class for read benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        # : (:obj:`str`) device proxy
        self.__device = options.device

        # : (:obj:`str`) device attribute name
        self.__attribute = options.attribute

        # : (:obj:`float`) time period in seconds
        self.__period = float(options.period)

        # : (:obj:`int`) number of clients
        self.__clients = float(options.clients)

    def start():
        """ start benchmark
        """


def main():
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
        "-n", "--number-of-clients", dest="clients", default="1",
        help="number of clients to be spawned, default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, default: 10")
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, default: BenchmarkScalarAttribute")

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

    rdbm = ReadBenchmark(options=options)
    rdbm.start()


if __name__ == "__main__":
    main()
