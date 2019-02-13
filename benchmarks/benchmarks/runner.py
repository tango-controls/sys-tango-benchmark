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
import json
import yaml
import sys
import os
import time
from multiprocessing import Queue

from argparse import RawTextHelpFormatter

from . import release
from . import readbenchmark
from . import writebenchmark
from . import eventbenchmark
from . import pipebenchmark
from . import servers


def main():
    """ the main function
    """

    parser = argparse.ArgumentParser(
        description='run set of benchmarks for default or specified '
        'set of parameters',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        dest="version",
        help="program version")
    parser.add_argument(
        "-c", "--config", dest="config",
        default="default.yml",
        help="YAML or JSON file with configuration, default: default.yml\n"
        "Its exmaples can be found in the 'config_examples' directory")

    options = parser.parse_args()

    if options.version:
        print(release.version)
        sys.exit(0)

    try:
        filename = options.config
        if not os.path.exists(filename):
            home = os.path.expanduser("~")
            hfilename = os.path.join(home, filename)
            if not os.path.exists(hfilename):
                filename = hfilename
        options.config
    except Exception:
        print("Error: cannot find the configuration file: %s" % filename)
        parser.print_help()
        print("")
        sys.exit(255)

    try:
        with open(filename, 'r') as stream:
            if filename.endswith(".json"):
                cflist = json.load(stream)
            else:
                cflist = yaml.load(stream)

        benchmarks = []
        devices = []
        for cfel in cflist:
            if "benchmark" in cfel.keys():
                benchmarks.append(cfel)
            elif "target_device" in cfel.keys():
                devices.append(cfel)

    except Exception:
        print("Error: cannot read the configuration file: %s" % filename)
        parser.print_help()
        print("")
        sys.exit(255)

    scripts = {
        "readbenchmark": readbenchmark,
        "writebenchmark": writebenchmark,
        "eventbenchmark": eventbenchmark,
        "pipebenchmark": pipebenchmark,
    }

    stqueue = Queue()
    starter = servers.Starter(devices, stqueue)
    starter.start()
    starter.join()
    started = stqueue.get(block=False)

    # without it we gets Timeout errors
    time.sleep(2)

    for bmk in benchmarks:
        script = bmk.pop("benchmark")
        if script.lower() in scripts.keys():
            scripts[script].main(**bmk)

    if started:
        stoper = servers.Stoper(*started)
        stoper.start()
        stoper.join()


if __name__ == "__main__":
    main()
