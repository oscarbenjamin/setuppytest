#!/bin/sh

export CWD=`pwd`
cram --shell=bash "$@" TESTS.t
