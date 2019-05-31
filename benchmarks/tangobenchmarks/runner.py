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
from . import read_benchmark
from . import write_benchmark
from . import event_benchmark
from . import cmd_benchmark
from . import push_event_benchmark
from . import pipe_read_benchmark
from . import pipe_write_benchmark
from . import dynamic_attribute_memory_benchmark
from . import server_startup_time_benchmark
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
        default="config_examples/default.yml",
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
                if hasattr(yaml, 'FullLoader'):
                    cflist = yaml.load(stream, Loader=yaml.FullLoader)
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
        "read_benchmark": read_benchmark,
        "write_benchmark": write_benchmark,
        "cmd_benchmark": cmd_benchmark,
        "event_benchmark": event_benchmark,
        "push_event_benchmark": push_event_benchmark,
        "pipe_read_benchmark": pipe_read_benchmark,
        "pipe_write_benchmark": pipe_write_benchmark,
    }

    new_scripts = dict(
        dynamic_attribute_memory_benchmark=dynamic_attribute_memory_benchmark,
        server_startup_time_benchmark=server_startup_time_benchmark,
    )

    stqueue = Queue()
    starter = servers.Starter(devices, stqueue)
    starter.start()
    starter.join()
    tostop = stqueue.get(block=False)

    # without it we gets Timeout errors
    time.sleep(2)

    for bmk in benchmarks:
        script = bmk.pop("benchmark")
        if script in new_scripts.keys():
            new_scripts[script].run(bmk)
        elif script.lower() in scripts.keys():
            scripts[script].main(**bmk)

    if tostop:
        stoper = servers.Stoper(*tostop)
        stoper.start()
        stoper.join()


if __name__ == "__main__":
    main()
