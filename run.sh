#!/bin/bash

python3 -m venv bobb_venv
source ./bobb_venv/bin/activate

echo "Installing Python dependencies"
pip3 install -r requirements.txt > /dev/null 2>&1

# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# Set default port
PORT=${1:-33001}
export PORT

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



hypercorn src.app:app --certfile cert/cert.pem --keyfile cert/key.pem --bind 0.0.0.0:$PORT --reload
