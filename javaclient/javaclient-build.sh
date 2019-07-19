#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

CLIENT_SOURCE=tg-benchmark-client

set -e
set -x

for dir in "$DIR/$CLIENT_SOURCE"-*; do
  mvn -f "$dir/pom.xml" package
done
