#!/bin/bash

python3 -m venv bobb_venv
source ./bobb_venv/bin/activate

pip3 install -r requirements.txt


# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

hypercorn src.app:app --certfile cert/cert.pem --keyfile cert/key.pem --bind 127.0.0.1:8189 --reload
