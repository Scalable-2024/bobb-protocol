# Written by Aryan
import struct
import socket
import time


class Bob2Headers:
    def __init__(self, version_major=1, version_minor=0, message_type=1, sequence_number=123, timestamp=None):
        self.version_major = version_major
        self.version_minor = version_minor
        self.message_type = message_type
        self.sequence_number = sequence_number
        self.timestamp = timestamp if timestamp else int(time.time())
        self.dest_ipv4 = "127.0.0.1"
        self.source_ipv4 = "127.0.0.1"
        self.dest_port = 30001
        self.source_port = 12345

    def build_header(self):
        dest_ip_bytes = socket.inet_pton(socket.AF_INET, self.dest_ipv4)
        source_ip_bytes = socket.inet_pton(socket.AF_INET, self.source_ipv4)
        header = struct.pack("!BBB", self.version_major,
                             self.version_minor, self.message_type)
        header += dest_ip_bytes + struct.pack("!H", self.dest_port)
        header += source_ip_bytes + struct.pack("!H", self.source_port)
        header += struct.pack("!I", self.sequence_number)
        header += struct.pack("!I", self.timestamp)
        return header.hex()


# Generate the custom header value
header = Bob2Headers().build_header()
