#!/bin/sh
# Wait-for-it utility — blocks until a TCP port is open
# Usage: ./wait-for-it.sh host:port [-t timeout] [-- command args]

set -e

TIMEOUT=30
QUIET=0

echoerr() {
    if [ "$QUIET" -ne 1 ]; then printf "%s\n" "$*" 1>&2; fi
}

usage() {
    exitcode="$1"
    cat << USAGE >&2
Usage:
    $0 host:port [-t timeout] [-- command args]
    -q | --quiet                        Do not output status messages
    -t TIMEOUT                          Timeout in seconds (default $TIMEOUT)
    -- COMMAND ARGS                     Execute command with args after the test finishes
USAGE
    exit "$exitcode"
}

wait_for() {
    HOST=$(echo "$1" | cut -d: -f1)
    PORT=$(echo "$1" | cut -d: -f2)
    for i in $(seq $TIMEOUT); do
        nc -z "$HOST" "$PORT" >/dev/null 2>&1 && return 0
        sleep 1
    done
    return 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        *:* ) HOSTPORT="$1"; shift 1;;
        -q | --quiet) QUIET=1; shift 1;;
        -t) TIMEOUT="$2"; shift 2;;
        --) shift; break;;
        -h | --help) usage 0;;
        *) echoerr "Unknown argument: $1"; usage 1;;
    esac
done

if [ -z "$HOSTPORT" ]; then
    echoerr "Error: you must provide a host and port to test."
    usage 2
fi

wait_for "$HOSTPORT"
if [ $? -eq 0 ]; then
    echoerr "$HOSTPORT is available after $TIMEOUT seconds"
else
    echoerr "$HOSTPORT is NOT available after $TIMEOUT seconds"
    exit 1
fi

if [ $# -gt 0 ]; then
    exec "$@"
fi
