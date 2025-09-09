#!/bin/bash

# Kill Apple media tracking processes continuously
# This script runs in the background and kills media analysis processes every 15 seconds

while true; do
	# Kill the processes silently (ignore if they're not running)
	killall -SIGINT mediaanalysisd 2>/dev/null
	killall -SIGINT mediaanalysisd-access 2>/dev/null
	killall -SIGINT photoanalysisd 2>/dev/null
	sleep 15
done