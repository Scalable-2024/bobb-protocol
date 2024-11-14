#!/bin/sh

# Clear temporary resources
TARGET_DIR="resources/"

# Check if the target directory exists
if [ -d "$TARGET_DIR" ]; then
    # Find and delete all files within the directory, leaving subdirectories intact
    find "$TARGET_DIR" -type f -delete
    echo "All files under $TARGET_DIR have been deleted."
else
    echo "Directory $TARGET_DIR does not exist."
fi

# Check if the input is provided and is a valid number between 1 and 100
if [ -z "$1" ] || [ "$1" -lt 1 ] || [ "$1" -gt 100 ]; then
    echo "Usage: $0 <number between 1 and 100>"
    exit 1
fi

# Run the original script the specified number of times with ports from 33001 to 33100
i=0
while [ "$i" -lt "$1" ]; do
    port=$((33001 + i))
    ./run.sh "$port" &
    i=$((i + 1))
done

echo "$1 instances starting on ports from 33001 to $port."
