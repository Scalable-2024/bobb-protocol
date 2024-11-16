# headers/bob2_headers.py

import struct
import socket
import time


class BobbHeaders:
    def __init__(self, version_major=0, version_minor=0, message_type=0,
                 dest_ipv4="127.0.0.1", dest_port=12345, source_ipv4="127.0.0.1", source_port=12345,
                 sequence_number=0, timestamp=None):
        self.version_major = version_major
        self.version_minor = version_minor
        self.message_type = message_type
        self.dest_ipv4 = dest_ipv4
        self.dest_port = dest_port
        self.source_ipv4 = source_ipv4
        self.source_port = source_port
        self.sequence_number = sequence_number
        self.timestamp = timestamp if timestamp is not None else int(time.time())

    def build_header(self):
        try:
            dest_ip_bytes = socket.inet_pton(socket.AF_INET, self.dest_ipv4)
            source_ip_bytes = socket.inet_pton(socket.AF_INET, self.source_ipv4)
        except socket.error:
            raise ValueError("Invalid IPv4 address")

        # Pack header with IPv4 addresses
        header = struct.pack("!BBB", self.version_major,
                             self.version_minor, self.message_type)
        header += dest_ip_bytes + struct.pack("!H", self.dest_port)
        header += source_ip_bytes + struct.pack("!H", self.source_port)
        header += struct.pack("!I", self.sequence_number)
        header += struct.pack("!I", self.timestamp)

        return header

    def parse_header(self, raw_data):
        version_major, version_minor, message_type = struct.unpack(
            "!BBB", raw_data[:3])
        dest_ipv4 = socket.inet_ntop(socket.AF_INET, raw_data[3:7])
        dest_port = struct.unpack("!H", raw_data[7:9])[0]
        source_ipv4 = socket.inet_ntop(socket.AF_INET, raw_data[9:13])
        source_port = struct.unpack("!H", raw_data[13:15])[0]
        sequence_number = struct.unpack("!I", raw_data[15:19])[0]
        timestamp = struct.unpack("!I", raw_data[19:23])[0]

        return {
            "version_major": version_major,
            "version_minor": version_minor,
            "message_type": message_type,
            "dest_ipv4": dest_ipv4,
            "dest_port": dest_port,
            "source_ipv4": source_ipv4,
            "source_port": source_port,
            "sequence_number": sequence_number,
            "timestamp": timestamp,
        }
