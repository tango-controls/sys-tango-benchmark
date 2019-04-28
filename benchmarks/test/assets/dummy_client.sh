#!/usr/bin/env bash

PERIOD="$_TANGO_BENCHMARK_period"

NOW=`date +%s`
COUNTER=`expr $NOW % 1000000`
ERRORS=`expr $NOW % 100`

sleep $PERIOD

echo "$COUNTER $PERIOD $ERRORS"
