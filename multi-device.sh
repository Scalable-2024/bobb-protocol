#!/bin/sh

# Define the target directory for resource cleanup
TARGET_DIR="resources/"

# Check if the RESET_RESOURCES argument is provided and valid
RESET_RESOURCES=$3
echo $RESET_RESOURCES
if [ "$RESET_RESOURCES" = "true" ]; then
    # Check if the target directory exists
    if [ -d "$TARGET_DIR" ]; then
        # Find and delete all files within the directory, leaving subdirectories intact
        find "$TARGET_DIR" -type f -delete
        echo "All files under $TARGET_DIR have been deleted."
    else
        echo "Directory $TARGET_DIR does not exist."
    fi
elif [ "$RESET_RESOURCES" != "false" ]; then
    echo "Invalid value for RESET_RESOURCES. Use 'true' or 'false'."
    exit 1
fi

# Validate the number of instances argument
if [ -z "$1" ] || [ "$1" -lt 1 ] || [ "$1" -gt 100 ]; then
    echo "Usage: $0 <number between 1 and 100> <DEVICE_FUNCTION> [START_PORT] <RESET_RESOURCES>"
    exit 1
fi

# Check if DEVICE_FUNCTION is provided
DEVICE_FUNCTION=$2
if [ -z "$DEVICE_FUNCTION" ]; then
    echo "Usage: $0 <number between 1 and 100> <DEVICE_FUNCTION> [START_PORT] <RESET_RESOURCES>"
    exit 1
fi

# Set the starting port; default to 33001 if not provided
START_PORT=$4
if [ -z "$START_PORT" ]; then
    START_PORT=33001
fi

# Run the original script the specified number of times with ports incrementing from START_PORT
i=0
while [ "$i" -lt "$1" ]; do
    port=$((START_PORT + i))
    ./run.sh "$port" "$DEVICE_FUNCTION" &
    i=$((i + 1))
done

echo "$1 instances starting on ports from $START_PORT to $port with device function '$DEVICE_FUNCTION'."
