# Written by Aryan, modified by Claire and Patrick
#!/bin/bash

# Create and activate a Python virtual environment
python3 -m venv bobb_venv
source ./bobb_venv/bin/activate

echo "Installing Python dependencies"
pip3 install -r requirements.txt 

# Default to port 33001 if not provided
PORT=${1:-33001}
export PORT
echo $PORT

# Set IP address enviroment variable based on the OS (useful for testing on different device operating systems (even though pi will use linux))
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS-specific command
    export IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux command
    export IP=$(hostname -I | awk '{print $1}')
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows command (please note this will only work if bash is running on windows)
    export IP=$(ipconfig | findstr /i "IPv4" | findstr /v "127.0.0.1" | awk '{print $NF}')
else
    echo "Unsupported OS"
    exit 1
fi

# Check if the input (DEVICE_FUNCTION) is provided
DEVICE_FUNCTION=$2
if [ -z "$DEVICE_FUNCTION" ]; then
    echo "Usage: $0 <DEVICE_FUNCTION>"
    exit 1
fi
export DEVICE_FUNCTION


hypercorn src.app:app --certfile cert/cert.pem --keyfile cert/key.pem --bind 0.0.0.0:$PORT --reload
