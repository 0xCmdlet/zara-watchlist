#!/bin/bash

# Test script to trigger rate limiting
# WARNING: This will likely get you temporarily blocked!

echo "=========================================="
echo "Starting rate limit test..."
echo "This will run the script 20 times rapidly"
echo "Press Ctrl+C to stop early"
echo "=========================================="

# Change to your project directory
cd /root/zara-watchlist

for i in {1..20}
do
    echo ""
    echo "========== Run #$i - $(date) =========="
    xvfb-run python3 src/main.py
    echo "Completed run #$i"

    # Very short delay (1 second) - this should trigger blocking
    sleep 1
done

echo ""
echo "=========================================="
echo "Test complete. Check the output above for errors"
echo "If you got blocked, wait 30-60 minutes before trying again"
echo "=========================================="
