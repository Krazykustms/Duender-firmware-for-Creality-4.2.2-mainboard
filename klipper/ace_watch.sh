#!/bin/bash
echo ACE_WATCH_STARTED
while true; do
  ts=$(date +%H:%M:%S)
  hits=$(lsusb 2>/dev/null | grep -iE '28e9|anycubic|05e3|018a' || true)
  acms=$(ls /dev/ttyACM* 2>/dev/null || true)
  if [ -n "$hits" ] || [ -n "$acms" ]; then
    echo "ACE_DETECTED $ts"
    echo "$hits"
    ls -l /dev/ttyACM* 2>/dev/null || true
    ls -l /dev/serial/by-id/ 2>/dev/null || true
    lsusb
    echo ---
  else
    echo "scan $ts: no ACE"
  fi
  sleep 2
done
