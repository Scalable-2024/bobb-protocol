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
    echo "Usage: $0 <number between 1 and 100> <DEVICE_FUNCTION> <RESET_RESOURCES> [START_PORT]"
    exit 1
fi

# Check if DEVICE_FUNCTION is provided
DEVICE_FUNCTION=$2
if [ -z "$DEVICE_FUNCTION" ]; then
    echo "Usage: $0 <number between 1 and 100> <DEVICE_FUNCTION> <RESET_RESOURCES> [START_PORT]"
    exit 1
fi

# Set the starting port; default to 33001 if not provided
START_PORT=$4
if [ -z "$START_PORT" ]; then
    START_PORT=33001
fi

# Check if Rust is installed
if ! rustc --version &> /dev/null; then
    echo "Rust is not installed. Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain stable --profile default -y 
    . $HOME/.cargo/env
    # Verify the installation
    if rustc --version &> /dev/null; then
        echo "Rust has been installed successfully."
    else
        echo "Rust installation failed. Exiting."
        exit 1
    fi
fi

. $HOME/.cargo/env

# Run the original script the specified number of times with ports incrementing from START_PORT
i=0
while [ "$i" -lt "$1" ]; do
    port=$((START_PORT + i))
    bash run.sh "$port" "$DEVICE_FUNCTION" &
    i=$((i + 1))
done

echo "$1 instances starting on ports from $START_PORT to $port with device function '$DEVICE_FUNCTION'."
