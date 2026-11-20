"""TCP signalling, UDP media, LAN discovery, and network impairment."""
import heapq
import json
import random
import secrets
import socket
import threading
import time
from .protocol import Channel, packetize, unpack, HEADER, PAYLOAD_SIZE
from .metrics import Metrics, Assembler, CSVRecorder

DISCOVERY_PORT = 5002
DISCOVERY_MAGIC = b'LANSTREAM_DISCOVER_V1'


def local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # UDP connect selects a route; it does not send traffic to this address.
        sock.connect(('192.0.2.1', 9))
        return sock.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        sock.close()


def discover(timeout=1.2):
    results = {}
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(.2)
        for host in ('255.255.255.255', '127.0.0.1'):
            try:
                sock.sendto(DISCOVERY_MAGIC, (host, DISCOVERY_PORT))
            except OSError:
                pass
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                data, addr = sock.recvfrom(4096)
                info = json.loads(data)
                if info.get('app') == 'LANStream' and 1 <= int(info['port']) <= 65535:
                    info['host'] = addr[0]
                    results[(addr[0], int(info['port']))] = info
            except (socket.timeout, ValueError, KeyError, TypeError):
                continue
    return list(results.values())


class Sender:
    def __init__(self, source, host='0.0.0.0', port=5000, loss=0, jitter_ms=0, on_event=None):
        if not 0 <= loss <= 100 or not 0 <= jitter_ms <= 2000:
            raise ValueError('Loss must be 0–100%; jitter 0–2000 ms')
        self.source, self.host, self.port = source, host, port
        self.loss, self.jitter = loss, jitter_ms / 1000
        self.on_event = on_event or (lambda message: None)
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.clients = {}
        self.connections = set()
        self.threads = []
        self.stream = secrets.randbits(64)
        self.sent_packets = self.sent_bytes = self.simulated_drops = 0
        self.started = time.monotonic()
        self.listener = self.udp = self.discovery = None

    def _thread(self, target, *args):
        thread = threading.Thread(target=target, args=args, daemon=True)
        self.threads.append(thread)
        thread.start()

    def start(self):
        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.bind((self.host, self.port))
            self.port = self.listener.getsockname()[1]
            self.listener.listen(16)
            self.listener.settimeout(.3)
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp.bind((self.host, 0))
            self.udp_port = self.udp.getsockname()[1]
            self._thread(self._accept)
            self._thread(self._stream)
            self._thread(self._discover)
            self.on_event(f'Sender listening on TCP {self.port}; media UDP {self.udp_port}')
        except Exception:
            self.stop()
            raise
        return self

    def _accept(self):
        while not self.stop_event.is_set():
            try:
                sock, address = self.listener.accept()
                sock.settimeout(5)
                channel = Channel(sock)
                with self.lock:
                    if len(self.connections) >= 32:
                        channel.close()
                        continue
                    self.connections.add(channel)
                self._thread(self._session, channel, address)
            except socket.timeout:
                continue
            except OSError:
                break

    def _session(self, channel, address):
        try:
            message = channel.receive()
            port = message.get('udp_port')
            if message['type'] != 'JOIN' or not isinstance(port, int) or not 1 <= port <= 65535:
                channel.send('ERROR', message='JOIN requires a valid udp_port')
                return
            channel.send('INFO', stream=self.stream, udp_port=self.udp_port,
                         name=self.source.name, fps=self.source.fps, width=self.source.width,
                         codec='JPEG', version=1)
            with self.lock:
                self.clients[channel] = dict(address=(address[0], port), stats={}, last=time.monotonic())
            self.on_event(f'Peer joined: {address[0]}:{port}')
            channel.sock.settimeout(.4)
            while not self.stop_event.is_set():
                try:
                    message = channel.receive()
                except socket.timeout:
                    with self.lock:
                        client = self.clients.get(channel)
                        last = client['last'] if client else 0
                    if time.monotonic() - last > 10:
                        break
                    continue
                with self.lock:
                    if channel in self.clients:
                        self.clients[channel]['last'] = time.monotonic()
                kind = message['type']
                if kind == 'PING':
                    channel.send('PONG', nonce=message.get('nonce'))
                elif kind == 'STAT':
                    stats = message.get('stats', {})
                    if isinstance(stats, dict):
                        with self.lock:
                            if channel in self.clients:
                                self.clients[channel]['stats'] = stats
                elif kind == 'INFO':
                    channel.send('INFO', stream=self.stream, fps=self.source.fps, name=self.source.name)
                elif kind == 'LEAVE':
                    break
        except (OSError, EOFError, ValueError, TypeError):
            pass
        finally:
            with self.lock:
                was_joined = self.clients.pop(channel, None)
                self.connections.discard(channel)
            channel.close()
            if was_joined:
                self.on_event(f'Peer left: {address[0]}')

    def _discover(self):
        try:
            self.discovery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery.bind(('', DISCOVERY_PORT))
            self.discovery.settimeout(.3)
            while not self.stop_event.is_set():
                try:
                    data, address = self.discovery.recvfrom(256)
                    if data == DISCOVERY_MAGIC:
                        response = json.dumps(dict(app='LANStream', port=self.port, name=self.source.name)).encode()
                        self.discovery.sendto(response, address)
                except socket.timeout:
                    continue
        except OSError:
            if not self.stop_event.is_set():
                self.on_event('Discovery unavailable; connect using IP and TCP port.')
        finally:
            if self.discovery:
                self.discovery.close()

    def _stream(self):
        sequence, frame = 0, 0
        queue = []
        ticket = 0
        next_frame = time.monotonic()
        finished = False
        try:
            while not self.stop_event.is_set():
                now = time.monotonic()
                while queue and queue[0][0] <= now:
                    _, _, data, address = heapq.heappop(queue)
                    try:
                        self.udp.sendto(data, address)
                        self.sent_packets += 1
                        self.sent_bytes += len(data)
                    except OSError:
                        if self.stop_event.is_set():
                            break
                if finished:
                    if not queue:
                        break
                    self.stop_event.wait(.002)
                    continue
                with self.lock:
                    destinations = [client['address'] for client in self.clients.values()]
                if not destinations:
                    next_frame = now
                    self.stop_event.wait(.02)
                    continue
                if now < next_frame:
                    self.stop_event.wait(min(.005, next_frame - now))
                    continue
                data = self.source.read()
                if data is None:
                    finished = True
                    continue
                timestamp = time.monotonic()
                packets = list(packetize(data, self.stream, frame, sequence, timestamp))
                for datagram in packets:
                    for address in destinations:
                        if random.random() * 100 < self.loss:
                            self.simulated_drops += 1
                            continue
                        if len(queue) >= 100000:
                            self.simulated_drops += 1
                            continue
                        ticket += 1
                        heapq.heappush(queue, (timestamp + random.uniform(0, self.jitter), ticket, datagram, address))
                sequence = (sequence + len(packets)) & 0xffffffff
                frame += 1
                next_frame = max(next_frame + 1 / self.source.fps, timestamp)
            if finished:
                self.on_event('Video finished.')
        except Exception as exc:
            self.on_event(f'Stream error: {exc}')
        finally:
            self.source.close()
            self.stop()

    def snapshot(self):
        with self.lock:
            peers = [dict(host=v['address'][0], port=v['address'][1], stats=dict(v['stats'])) for v in self.clients.values()]
        return dict(peers=peers, packets=self.sent_packets, bytes=self.sent_bytes,
                    simulated_drops=self.simulated_drops, running=not self.stop_event.is_set())

    def stop(self):
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        with self.lock:
            channels = list(self.connections)
        for channel in channels:
            try:
                channel.send('END', message='Stream ended')
            except (OSError, ValueError):
                pass
            channel.close()
        for sock in (self.listener, self.udp, self.discovery):
            if sock:
                sock.close()
        for thread in list(self.threads):
            if thread is not threading.current_thread():
                thread.join(timeout=1)
        self.source.close()


class Receiver:
    def __init__(self, host, port=5000, buffer_ms=120, on_frame=None, on_event=None, csv_path=None):
        self.host, self.port = host, port
        self.on_frame = on_frame or (lambda jpeg: None)
        self.on_event = on_event or (lambda message: None)
        self.metrics = Metrics()
        self.assembler = Assembler(self.metrics, buffer_ms)
        self.csv_path = csv_path
        self.stop_event = threading.Event()
        self.threads = []
        self.udp = self.channel = None
        self.info = {}
        self.end_at = None
        self.recorder = None

    def start(self):
        try:
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
            self.udp.bind(('', 0))
            self.udp.settimeout(.01)
            sock = socket.create_connection((self.host, self.port), timeout=5)
            self.peer_ip = sock.getpeername()[0]
            self.channel = Channel(sock)
            self.channel.send('JOIN', udp_port=self.udp.getsockname()[1])
            self.info = self.channel.receive()
            if self.info['type'] != 'INFO' or self.info.get('codec') != 'JPEG':
                raise ValueError('Sender did not provide compatible stream metadata')
            if not isinstance(self.info.get('stream'), int) or not isinstance(self.info.get('udp_port'), int):
                raise ValueError('Invalid sender metadata')
            self.channel.sock.settimeout(.2)
            if self.csv_path:
                self.recorder = CSVRecorder(self.csv_path)
            for target in (self._media, self._control):
                thread = threading.Thread(target=target, daemon=True)
                self.threads.append(thread)
                thread.start()
            self.on_event(f"Joined {self.info.get('name', 'stream')} at {self.peer_ip}:{self.port}")
        except Exception:
            self.stop()
            raise
        return self

    def _media(self):
        try:
            while not self.stop_event.is_set():
                try:
                    data, address = self.udp.recvfrom(65535)
                    if address != (self.peer_ip, self.info['udp_port']):
                        continue
                    packet = unpack(data)
                    if packet.stream != self.info['stream']:
                        continue
                    now = time.monotonic()
                    if self.metrics.packet(packet, len(data), now):
                        self.assembler.add(packet, now)
                except (socket.timeout, ValueError):
                    pass
                for jpeg in self.assembler.ready(time.monotonic()):
                    self.on_frame(jpeg)
                if self.end_at and time.monotonic() >= self.end_at:
                    break
        except OSError:
            pass
        except Exception as exc:
            self.on_event(f'Playback error: {exc}')
        finally:
            self.stop()

    def _control(self):
        next_report = 0
        pending_ping = None
        last_reply = time.monotonic()
        try:
            while not self.stop_event.is_set():
                now = time.monotonic()
                if now >= next_report:
                    if pending_ping is None:
                        pending_ping = now
                        self.channel.send('PING', nonce=pending_ping)
                    stats = self.metrics.snapshot()
                    self.channel.send('STAT', stats=stats)
                    if self.recorder:
                        self.recorder.write(stats)
                    next_report = now + 1
                try:
                    message = self.channel.receive()
                except socket.timeout:
                    if time.monotonic() - last_reply > 10:
                        raise EOFError('Sender timed out')
                    continue
                last_reply = time.monotonic()
                if message['type'] == 'PONG' and pending_ping == message.get('nonce'):
                    with self.metrics.lock:
                        self.metrics.rtt = (time.monotonic() - pending_ping) * 1000
                    pending_ping = None
                elif message['type'] == 'END':
                    break
        except (OSError, EOFError, ValueError, TypeError) as exc:
            if not self.stop_event.is_set():
                self.on_event(f'Control channel ended: {exc}')
        finally:
            self.end_at = time.monotonic() + self.assembler.delay + .2

    def stop(self):
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        if self.channel:
            try:
                self.channel.send('LEAVE')
            except (OSError, ValueError):
                pass
            self.channel.close()
        if self.udp:
            self.udp.close()
        for thread in list(self.threads):
            if thread is not threading.current_thread():
                thread.join(timeout=1)
        if self.recorder:
            self.recorder.write(self.metrics.snapshot())
            self.recorder.close()
        self.on_event('Receiver stopped.')
