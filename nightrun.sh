#!/bin/bash
set -e


cd "$(dirname "$0")"



dos2unix -q night.sh
chmod +x night.sh
time nice -n 19 ./night.sh

echo Nightly Testing Cron Job was successfull
