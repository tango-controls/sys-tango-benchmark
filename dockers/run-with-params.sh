#!/usr/bin/env bash
#
# Usage:
#
#  run-with-param.sh
#
#  run-with-param.sh /my/config/file.yml
#
#  run-with-param.sh /my/config/file.json
#
#  run-with-param.sh bash
#
#  run-with-param.sh ping
#
sudo docker-compose up --build --no-start
sudo docker-compose run  client $@
sudo docker-compose down
