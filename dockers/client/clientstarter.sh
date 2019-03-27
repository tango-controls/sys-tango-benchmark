#!/usr/bin/env bash

echo ""
echo "TANGO_HOST=$TANGO_HOST"
echo ""
if [ $# -eq 0 ]
   then
       python /opt/waitfordevice.py sys/benchmark/pytarget01 sys/benchmark/cpptarget01 sys/benchmark/javatarget01
else
       python /opt/waitfordevice.py sys/tg_test/1
fi
exec tg_benchmarkrunner $@
