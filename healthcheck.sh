#!/bin/sh -e

PID=$(pidof python)

if [ -n "$PID" ] && [ -e "/proc/$PID" ]; then
    echo "Bot is running on PID $PID"
    exit 0
else
    echo "Bot not running" >&2
    exit 1
fi