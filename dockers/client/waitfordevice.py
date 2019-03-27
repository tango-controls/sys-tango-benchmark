#!/usr/bin/env python

from benchmarks import servers
import argparse

parser = argparse.ArgumentParser(
    description="waits till the device is running")
parser.add_argument(
    "-d", "--device", dest="device",
    help="device on which the test will be performed")
args = parser.parse_args()
if args.device is None:
    device = "sys/tg_test/1"
pydevice = "sys/benchmark/pytarget01"
cppdevice = "sys/benchmark/cpptarget01"
javadevice = "sys/benchmark/javatarget01"

st = servers.Starter(None, None)
st.checkDevice(device, 120, True)
st.checkDevice(pydevice, 120)
st.checkDevice(cppdevice, 120)
st.checkDevice(javadevice, 120)
