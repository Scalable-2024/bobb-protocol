import struct
import time


class LEOOptionalHeaders:
    def __init__(self, timestamp=None, hop_count=255, priority=0, encryption_algo="None"):
        self.timestamp = timestamp if timestamp else int(time.time())
        self.hop_count = hop_count
        self.priority = priority
        self.encryption_algo = encryption_algo

    def build_optional_header(self):
        """
        Builds a binary representation of the optional header.

        Returns:
            bytes: The binary optional header.
        """
        header = struct.pack("!I", self.timestamp)  # 4 bytes for timestamp
        header += struct.pack("!B", self.hop_count)  # 1 byte for hop count
        header += struct.pack("!B", self.priority)  # 1 byte for priority
        # 16 bytes for encryption_algo
        header += self.encryption_algo.encode('utf-8').ljust(16, b'\0')
        return header


if __name__ == "__main__":
    # Example usage
    leo_header = LEOOptionalHeaders(
        timestamp=int(time.time()),
        hop_count=5,
        priority=2,
        encryption_algo="AES128"
    )

    # Generate the binary header and convert it to hex for HTTP transmission
    hex_header = leo_header.build_optional_header().hex()
