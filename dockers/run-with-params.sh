#!/usr/bin/env bash
#
# Usage examples:
#
#  run-with-params.sh
#
#  run-with-params.sh /var/lib/tango/config_examples/cpp_test.yml
#
#  run-with-params.sh /var/lib/tango/config_examples/java_test.yml
#
#  run-with-params.sh /var/lib/tango/config_examples/python_test.json
#
#  run-with-params.sh bash
#
#  run-with-params.sh ping
#
docker-compose build
docker-compose run  client $@
docker-compose down
