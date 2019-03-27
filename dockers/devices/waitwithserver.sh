#!/usr/bin/env bash
#
# waitwithserver.sh TANGOSERVER INSTANCE --verbose
#

PD=$(ps -ef | grep "$1 "| sed 's/$/ /' | grep " $2 " | grep -v 'waitwithserver.sh'|  awk '{print $2}')
if [[ $PD  ]]; then
    PD=$(echo "$PD" |  awk '{print $1}')
    if [[ $3 ]]; then
	echo "Waiting with: $1/$2"
	# ps -ef | grep "$1 "| sed 's/$/ /' | grep -v 'waitforserver.sh'| grep " $2 "
    fi
    tail --pid=$PD -f /dev/null
fi
