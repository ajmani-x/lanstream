"""Receiver metrics and bounded, reorder-tolerant JPEG frame assembly."""
import collections
import csv
import threading
import time


class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.started = time.monotonic()
        self.base = None
        self.highest = None
        self.unique = 0
        self.seen = set()
        self.bytes = 0
        self.duplicates = 0
        self.frames = 0
        self.dropped_frames = 0
        self.late_frames = 0
        self.jitter = 0.0
        self.previous = None
        self.rtt = 0.0
        self.window = collections.deque()

    def packet(self, packet, size, now):
        with self.lock:
            seq = packet.sequence
            if self.base is None:
                self.base = self.highest = seq
            if seq in self.seen:
                self.duplicates += 1
                return False
            # Very old packets are ignored after the deduplication horizon.
            if seq < self.highest - 8192:
                return False
            self.seen.add(seq)
            if len(self.seen) > 16384:
                self.seen = {x for x in self.seen if x >= self.highest - 8192}
            self.highest = max(self.highest, seq)
            self.base = min(self.base, seq)
            self.unique += 1
            self.bytes += size
            self.window.append((now, size))
            if self.previous:
                arrival, sent = self.previous
                delta = abs((now - arrival) - (packet.timestamp - sent)) * 1000
                self.jitter += (delta - self.jitter) / 16
            self.previous = (now, packet.timestamp)
            return True

    def increment(self, name):
        with self.lock:
            setattr(self, name, getattr(self, name) + 1)

    def snapshot(self):
        with self.lock:
            now = time.monotonic()
            elapsed = max(.001, now - self.started)
            while self.window and self.window[0][0] < now - 1:
                self.window.popleft()
            expected = 0 if self.base is None else self.highest - self.base + 1
            missing = max(0, expected - self.unique)
            return dict(elapsed_s=round(elapsed, 2), packets=self.unique,
                        missing=missing, loss_pct=round(100 * missing / max(1, expected), 2),
                        duplicates=self.duplicates, frames=self.frames,
                        dropped_frames=self.dropped_frames, late_frames=self.late_frames,
                        jitter_ms=round(self.jitter, 2), rtt_ms=round(self.rtt, 2),
                        throughput_mbps=round(sum(x[1] for x in self.window) * 8 / 1e6, 3),
                        average_mbps=round(self.bytes * 8 / elapsed / 1e6, 3),
                        fps=round(self.frames / elapsed, 1), bytes=self.bytes)


class Assembler:
    def __init__(self, metrics, buffer_ms=120):
        if not 0 <= buffer_ms <= 3000:
            raise ValueError('Buffer must be 0–3000 ms')
        self.metrics, self.delay = metrics, buffer_ms / 1000
        self.pending = {}
        self.anchor = None
        self.last_played = -1
        self.observed = set()

    def add(self, packet, now):
        if self.anchor is None:
            self.anchor = (now, packet.timestamp)
        if packet.frame <= self.last_played:
            return
        entry = self.pending.get(packet.frame)
        if entry is None:
            if packet.frame in self.observed:
                return
            self.observed.add(packet.frame)
            if len(self.observed) > 512:
                self.observed = {x for x in self.observed if x >= packet.frame - 256}
            deadline = self.anchor[0] + packet.timestamp - self.anchor[1] + self.delay
            if deadline < now - .1:
                self.metrics.increment('late_frames')
                return
            if len(self.pending) >= 64:
                oldest = min(self.pending)
                del self.pending[oldest]
                self.metrics.increment('dropped_frames')
            # Even a zero playout buffer needs a brief chunk assembly window.
            deadline = max(deadline, now + .015)
            entry = self.pending[packet.frame] = [deadline, packet.count, {}]
        if packet.count != entry[1]:
            return
        entry[2][packet.index] = packet.payload

    def ready(self, now):
        frames = []
        for frame in sorted(list(self.pending)):
            deadline, count, parts = self.pending[frame]
            if now < deadline:
                continue
            del self.pending[frame]
            if frame <= self.last_played:
                continue
            if len(parts) == count:
                frames.append(b''.join(parts[i] for i in range(count)))
                self.last_played = frame
                self.metrics.increment('frames')
            else:
                self.metrics.increment('dropped_frames')
        return frames


class CSVRecorder:
    def __init__(self, path):
        from pathlib import Path
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open('w', newline='')
        self.writer = None

    def write(self, stats):
        if self.writer is None:
            self.writer = csv.DictWriter(self.file, fieldnames=list(stats))
            self.writer.writeheader()
        self.writer.writerow(stats)
        self.file.flush()

    def close(self):
        self.file.close()
