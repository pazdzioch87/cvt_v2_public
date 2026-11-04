#!/bin/bash

# Set a maximum number of retries
MAX_RETRIES=10
retry_count=0

echo "Starting FFMPEG streaming service..."
echo "Camera URL: $CAMERA_URL"
echo "SRS URL: $SRS_URL"

while true; do
  # Check camera connectivity first
  if ffprobe -v quiet -i "$CAMERA_URL" -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 2>/dev/null; then
    echo "Camera connection successful, starting stream..."
    
    # Start the streaming
    ffmpeg -i "$CAMERA_URL" -c:v copy -c:a aac -ar 44100 -f flv "$SRS_URL" 2>&1
    
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
      echo "FFMPEG exited with code $exit_code"
    fi
  else
    echo "Cannot connect to camera at $CAMERA_URL"
    retry_count=$((retry_count+1))
    
    if [ $retry_count -ge $MAX_RETRIES ]; then
      echo "Maximum retry attempts ($MAX_RETRIES) reached. Waiting for 60 seconds before trying again."
      sleep 60
      retry_count=0
    fi
  fi
  
  echo "Stream interrupted. Restarting in 5 seconds..."
  sleep 5
done