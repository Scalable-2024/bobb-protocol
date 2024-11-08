### **API Documentation**

#### **Base URL**: 
```
https://127.0.0.1:8189
```

---

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
      "dest_port": 8189,
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
2. Use the URL: `https://127.0.0.1:8189/`.
3. Add the following headers:
   - **X-Bobb-Header**: `<valid hexadecimal Bobb header>`
   - **X-Bobb-Optional-Header**: `<valid hexadecimal Bobb optional header>`.
4. Send the request and observe the response.
