# Bobb Protocol

## Important Notes: 
1. The folders "Allow self signed certificate" and "Initial-Topology" were approaches explored and tested but are not implemented in the final Bobb so can be ignored when testing Bobb protocol and use-case.
2. The folder human_count_machine_learning in src/utils/human_count_machine_learning works correctly on pi but is not implemented in the final bobb protocol. 
3. Also when running bobb and use-case erros surrounding json appear, these happen for the first minute or so while running but eventually resolve themselves. Furthermore, the error "Error creating routing table" can also be ignored. They are being created correctly but we did not want to make changes to the code this close to the deadline incase of causing further issues.

## Introduction
For the Bobb protocol we have made the choice to use HTTP protocol as the underlying transport protocol. This choice was made because of the simplicity of the protocol and the fact that it is widely used.

The Bobb protocol is a simple protocol that is used to send and receive messages between Low Earth Orbit (LEO) satellites and base stations. The protocol is designed to be simple and easy to implement

## Protocol
The protocol will be greatly based on the other bob2 protocol which we discussed during class and in the other repository.

### Message format
#### Handshake message
The handshake message is used to discover satellites and base stations in the network. The message follows the following format, with ip address in the X-Bobb-Header:
```json
{
    "device_function": "disaster-imaging",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzZ",
    "port": "33001",
    "connected": []
}
```

The response to the handshake message will be a message with the same format. The message will contain the IP, function and public key of the satellite or basestation. The message will also contain a list of connected satellites or base stations. This list will contain the IP, function and public key of the connected satellites or base stations.

#### Header information
The header should contain the following information:
- Major-Version: Major version of the protocol
- Minor-Version: Minor version of the protocol
- Content-Type: application/json
- Content-Length: length of the message
- Timestamp: timestamp of the message
- Source: IP of the source
- Source-Port: Port of the source
- Destination: IP of the destination
- Destination-Port: Port of the destination
- Max-Hops: Maximum number of hops the message can take

## Running the code
Basic code is provided to create a satellite (in progress) - this should be forked for customisation specific to your team, but shared logic should remain the same.

To start up one satellite on your machine - uses default port 33001:
```shell
sh run.sh
```

To start up many satellites at once on one machine (max 100, shown here 5):
```shell
sh multi-satellite.sh 5
```

## Features
The Bobb protocol has the following features:
- Satellite discovery
- Handshaking
- End-to-end encryption using Public Key Infrastructure (PKI)

### Satellite discovery
Satellite discovery is done by sending a broadcast message to all satellites in the network. All satellites running Bob2 code will respond with a 200 status code. These will be added to a list, which neighbours are selected from.

The code for this is in discovery.py, and is acting outside the model of satellites - while satellites find each other by rotating in LEO until they can see another satellite, our raspberry pis have no movement or antennae, so we need to retrieve IP addresses of all possible satellites before simulating the satellite behaviour.

This list is stored in `resources/satellite_listings/full_satellite_listing_{port}.csv`. This specifies the port in the file name to allow several satellite instances to run independently on a single raspberry pi. The headers are as follows:

```
IPv4,Port,Response Time,Device Type
```

### Handshaking
Handshaking between satellites only has been set up, but the logic will remain the same between satellites and base stations. Each satellite sends a handshake message to each of its neighbours (selected during satellite discovery). This contains the satellites IP, port, function, and public key. The receiving satellite stores these details in a json - `resources/satellite_neighbours/neighbours_{port}.json`. This specifies the port in the file name to allow several satellite instances to run independently on a single raspberry pi. Currently, connected nodes are not specified here, but they are supported. An example of this:
```json
[
    {
        //"ip": "::ffff:172.31.116.126", Included in the header instead
        "name": "kind-pike-10.35.70.1:33001",
        "function": "whale-tracking",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VuAyEAEhqgVWqTrTRHydIj7aHflbuFhIYrrCdi4GiOKUqyKkQ=\n-----END PUBLIC KEY-----\n",
        "port": 33001,
        "connected_nodes": []
    },
]
```

### End-to-end encryption using Public Key Infrastructure (PKI)
The Bobb protocol uses Public Key Infrastructure (PKI) to encrypt messages between satellites and base stations. The public key of the other party is used to encrypt the message. The private key of the other party is used to decrypt the message.

## Current use cases
The Bobb protocol is currently used for the following use cases:
- Disaster imaging (Group 13)
- Whale tracking (Group 1)
- Post flood survivor detection (Group 9)

## Device Types
There are a number of device types/satellite functions supported by this protocol/system, which are defined in src/config/constants. Some of these may have different behaviours, controlled by their type as defined on startup. To make use of this, pass whatever valid device type is required into multi-device.sh. Note that this setup treats base stations as a valid device type.

## Future use cases
Whatever other teams come up with

## **API Documentation**
This repository contains a Flask-based API that implements custom headers (X-Bobb-Header and X-Bobb-Optional-Header) for communication. The API provides endpoints to:

## Postman Collection
To test the API endpoints, use the Postman collection linked below:
Postman Collection Link <https://elements.getpostman.com/redirect?entityId=31802781-42cf7b59-0dbf-4800-b6af-69e2161a5772&entityType=collection>

## **Base URL**:
The first satellite is on port 33001, and satellites can run on any port between 33001-33100 (inclusive).
```
https://127.0.0.1:33001
```

### **Endpoints**

---

#### **1. GET `/`**

**Description**:
Returns a greeting message along with validated BobbHeaders and BobbOptionalHeaders.

**Headers**:
- **X-Bobb-Header** (Required): A hexadecimal string representing the Bobb protocol header.
- **X-Bobb-Optional-Header** (Optional): A hexadecimal string representing the optional Bobb header.

**Response**:
- **200 OK**: If headers are valid.

**Response Body**:
```json
{
  "status": "success",
  "data": {
    "message": "Hello with Bobb and Bobb Headers!",
    "bobb_header_data": {
      "version_major": 1,
      "version_minor": 0,
      "message_type": 1,
      "dest_ipv4": "127.0.0.1",
      "dest_port": 33001,
      "source_ipv4": "127.0.0.1",
      "source_port": 12345,
      "sequence_number": 123,
      "timestamp": 1697083106
    },
    "bobb_optional_data": {
      "timestamp": 1697083106,
      "hop_count": 5,
      "priority": 2,
      "encryption_algo": "AES128"
    }
  },
  "status_code": 200
}
```

**Error Responses**:
- **400 Bad Request**: If a required header is missing or invalid.

**Example**:
```json
{
  "error": "Invalid Bobb header",
  "details": "Header value is not properly formatted"
}
```

---

### **Headers Example**

**X-Bobb-Header**:
```plaintext
010001000000000000000000000000000000011ffd0000000000000000000000000000000130390000007b672df81d
```

**X-Bobb-Optional-Header**:
```plaintext
672df859050241455331323800000000000000000000
```

---

### **Testing with Postman**

1. Set the request type to `GET`.
2. Use the URL: `https://127.0.0.1:33001/`.
3. Add the following headers:
   - **X-Bobb-Header**: `<valid hexadecimal Bobb header>`
   - **X-Bobb-Optional-Header**: `<valid hexadecimal Bobb optional header>`.
4. Send the request and observe the response.
