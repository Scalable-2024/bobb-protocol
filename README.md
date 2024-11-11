# Bobb Protocol

## Introduction
For the Bobb protocol we have made the choice to use HTTP protocol as the underlying transport protocol. This choice was made because of the simplicity of the protocol and the fact that it is widely used.

The Bobb protocol is a simple protocol that is used to send and receive messages between Low Earth Orbit (LEO) satellites and base stations. The protocol is designed to be simple and easy to implement

## Protocol
The protocol will be greatly based on the other bob2 protocol which we discussed during class and in the other repository.

### Message format
#### Handshake message
The handshake message is used to discover satellites and base stations in the network. The message follows the following format:
```json
{
    "type": "handshake",
    "ip": "10.0.0.1",
    "function": "disaster-imaging",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzZ",
    "connected": [
      {
        "ip": "10.0.0.2",
        "function": "disaster-imaging",
        "public_key": "-----BEGIN PUBLIC KEY----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzZ",
        "connected": []
      },
      {
        "ip": "10.0.0.3",
        "function": "whale-tracking",
        "public_key": "-----BEGIN PUBLIC KEY----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzZ",
        "connected": []
      }
    ]
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

## Features
The Bobb protocol has the following features:
- Satellite discovery
- Handshaking
- End-to-end encryption using Public Key Infrastructure (PKI)

### Satellite discovery
Satellite discovery is done by sending a broadcast message to all satellites in the network. The satellite will respond with a message containing its IP, function and public key.

### Handshaking
Handshaking is done during satellite discovering. The satellite will send a message containing its IP, function and public key. The basestation will respond with a message containing its IP, function and public key.

During the handshaking phase the satellites and basestation save the information (IP, function and public key) of the other party. This information is then propagated to all other satellites and base stations in the network.

The handshake includes information about which other satellites or base stations are connected to the satellite or basestation. This again will contain the IP, function and public key of the other party.

### End-to-end encryption using Public Key Infrastructure (PKI)
The Bobb protocol uses Public Key Infrastructure (PKI) to encrypt messages between satellites and base stations. The public key of the other party is used to encrypt the message. The private key of the other party is used to decrypt the message.

## Current use cases
The Bobb protocol is currently used for the following use cases:
- Disaster imaging
- Whale tracking
- Offshore wind farm monitoring

## Future use cases
Whatever other teams come up with

## **API Documentation**
This repository contains a Flask-based API that implements custom headers (X-Bobb-Header and X-Bobb-Optional-Header) for communication. The API provides endpoints to:

## Postman Collection
To test the API endpoints, use the Postman collection linked below:
Postman Collection Link <https://elements.getpostman.com/redirect?entityId=31802781-42cf7b59-0dbf-4800-b6af-69e2161a5772&entityType=collection>

## **Base URL**:
```
https://127.0.0.1:30001
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
      "dest_ipv6": "::1",
      "dest_port": 30001,
      "source_ipv6": "::1",
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
2. Use the URL: `https://127.0.0.1:30001/`.
3. Add the following headers:
   - **X-Bobb-Header**: `<valid hexadecimal Bobb header>`
   - **X-Bobb-Optional-Header**: `<valid hexadecimal Bobb optional header>`.
4. Send the request and observe the response.
