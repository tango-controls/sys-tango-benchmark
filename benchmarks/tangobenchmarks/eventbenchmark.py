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

from tangobenchmarks.utility.benchmark import common_main


def _add_arguments(parser):
    parser.add_argument(
        "-a", "--attribute", dest="attribute",
        default="BenchmarkScalarAttribute",
        help="attribute which will be read, default: BenchmarkScalarAttribute")


def _update_options(options):
    if not options.attribute:
        options.attribute = "BenchmarkScalarAttribute"


def main(**kargs):
    common_main(
        kargs,
        _add_arguments,
        _update_options,
        default_worker='tangobenchmarks.client.python.event.Worker',
        description=(
            'perform check if and how number of parallel '
            'subscribers affects subscription time'),
        title="Event Benchmark",
        header_text="event")


if __name__ == "__main__":
    main()
