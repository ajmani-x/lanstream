"""Bounded binary media framing and newline-delimited JSON control messages."""
import json
import socket
import struct
import threading
from dataclasses import dataclass

MAGIC = b'LVS1'
HEADER = struct.Struct('!4sQIIHHd')
PAYLOAD_SIZE = 1160  # 1192-byte UDP payload; below a typical 1500-byte MTU.
MAX_FRAME_BYTES = 2_000_000
MAX_CHUNKS = (MAX_FRAME_BYTES + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
MAX_CONTROL = 16384

@dataclass(frozen=True)
class Packet:
    stream: int
    sequence: int
    frame: int
    index: int
    count: int
    timestamp: float
    payload: bytes


def packetize(data, stream, frame, sequence, timestamp):
    if not data or len(data) > MAX_FRAME_BYTES:
        raise ValueError('Encoded frame must contain 1–2,000,000 bytes')
    count = (len(data) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
    for index in range(count):
        yield HEADER.pack(MAGIC, stream, (sequence + index) & 0xffffffff,
                          frame & 0xffffffff, index, count, timestamp) + data[index * PAYLOAD_SIZE:(index + 1) * PAYLOAD_SIZE]


def unpack(data):
    if len(data) <= HEADER.size or len(data) > HEADER.size + PAYLOAD_SIZE:
        raise ValueError('Invalid datagram size')
    magic, stream, seq, frame, index, count, timestamp = HEADER.unpack_from(data)
    if magic != MAGIC or not 0 < count <= MAX_CHUNKS or index >= count:
        raise ValueError('Invalid media header')
    import math
    if not math.isfinite(timestamp):
        raise ValueError('Invalid timestamp')
    return Packet(stream, seq, frame, index, count, timestamp, data[HEADER.size:])


class Channel:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = bytearray()
        self.lock = threading.Lock()

    def send(self, kind, **fields):
        message = json.dumps(dict(type=kind, **fields), separators=(',', ':'), allow_nan=False).encode() + b'\n'
        if len(message) > MAX_CONTROL:
            raise ValueError('Control message too large')
        with self.lock:
            self.sock.sendall(message)

    def receive(self):
        while b'\n' not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError('Control connection closed')
            self.buffer.extend(chunk)
            if len(self.buffer) > MAX_CONTROL:
                raise ValueError('Control message too large')
        line, _, rest = self.buffer.partition(b'\n')
        self.buffer = bytearray(rest)
        message = json.loads(line)
        if not isinstance(message, dict) or not isinstance(message.get('type'), str):
            raise ValueError('Invalid control message')
        return message

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
