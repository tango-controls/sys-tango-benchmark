#!/usr/bin/env bash

if [ $# -eq 0 ]
   then
       python /opt/waitfordevice.py sys/benchmark/pytarget01 sys/benchmark/cpptarget01
else
       python /opt/waitfordevice.py sys/tg_test/1
fi
exec tg_benchmarkrunner $@
