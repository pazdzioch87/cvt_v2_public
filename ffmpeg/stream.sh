#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e
set -x  # Enable debug output

# Check if CAMERA_URL and SRS_URL are set
if [ -z "$CAMERA_URL" ] || [ -z "$SRS_URL" ]; then
  echo "Error: CAMERA_URL and SRS_URL must be set."
  exit 1
fi

# Start an infinite loop to keep the stream alive
while true; do
  echo "Starting FFmpeg stream..."
  ffmpeg -hide_banner -loglevel warning -i "$CAMERA_URL" -c copy -f flv "$SRS_URL" || true
  echo "Stream interrupted. Restarting in 5 seconds..."
  sleep 5
done