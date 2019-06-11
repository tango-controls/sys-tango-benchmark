#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

CLIENT_SOURCE=tg-benchmark-client
CLIENT_SCRIPT=tg_benchmark_client_java

INSTALL_PREFIX=${INSTALL_PREFIX:-${TANGO_ROOT:-/usr}}

mkdir -p "$INSTALL_PREFIX/bin"
mkdir -p "$INSTALL_PREFIX/share/java"

set -e
set -x

cp -f "$DIR/$CLIENT_SOURCE"-*/target/*.jar "$INSTALL_PREFIX/share/java"

for dir in "$DIR/$CLIENT_SOURCE"-*; do
  client="$(echo "$dir" | awk -F- '{print $NF}')"
  outfile="$INSTALL_PREFIX/bin/${CLIENT_SCRIPT}_${client}"
  sed "s/^CLIENT=$/CLIENT=$client/g" "$DIR/javaclient-script-template" > "$outfile"
  chmod +x "$outfile"
done
