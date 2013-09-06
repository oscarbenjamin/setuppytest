#!/bin/sh

set -o errexit

export CWD=`pwd`
cram --shell=bash "$@" TESTS.t
if [ "$NO_WHEEL" = "1" ]; then
    echo "Skipping wheel tests..."
else
    cram --shell=bash "$@" TESTS_WHEEL.t
fi
