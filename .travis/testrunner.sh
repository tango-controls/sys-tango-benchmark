#!/usr/bin/env bash

echo "run benchmark runner tests"
if [ "$1" = "2" ]; then
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python setup.py test'
else
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python3 setup.py test'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi
