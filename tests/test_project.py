import csv
import io
import socket
import tempfile
import time
import unittest
from pathlib import Path
from lanstream.protocol import packetize, unpack, HEADER, PAYLOAD_SIZE, Channel
from lanstream.metrics import Metrics, Assembler
from lanstream.media import VideoSource
from lanstream.network import Sender, Receiver, discover


def wait_for(predicate, timeout=4):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(.02)
    return False


class ProtocolTests(unittest.TestCase):
    def test_round_trip_and_mtu(self):
        content = bytes(range(256)) * 30
        chunks = list(packetize(content, 99, 7, 50, 12.5))
        packets = [unpack(data) for data in chunks]
        self.assertTrue(all(len(data) <= 1192 for data in chunks))
        self.assertEqual(b''.join(p.payload for p in packets), content)
        self.assertEqual([p.sequence for p in packets], list(range(50, 50+len(packets))))
        self.assertTrue(all(p.stream == 99 and p.frame == 7 for p in packets))

    def test_invalid_datagrams(self):
        for data in (b'', b'bad', b'x' * 1400, HEADER.pack(b'LVS1', 1, 1, 1, 3, 1, 1) + b'x'):
            with self.assertRaises(ValueError):
                unpack(data)
        with self.assertRaises(ValueError):
            list(packetize(b'', 1, 1, 1, 1))

    def test_trace_analyzer(self):
        from experiments.analyze_trace import analyze
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.tr'
            path.write_text('+ 1.0 0 1 cbr 1192 ------- 0 0.0 2.0 0 100\n'
                            'r 1.1 1 2 cbr 1192 ------- 0 0.0 2.0 0 100\n'
                            '+ 1.2 0 1 cbr 1192 ------- 0 0.0 2.0 1 101\n')
            result = analyze(path)
            self.assertEqual(result['sent'], 2)
            self.assertEqual(result['received'], 1)
            self.assertEqual(result['loss_pct'], 50)
            self.assertEqual(result['mean_delay_ms'], 100)

    def test_control_fragmentation_and_coalescing(self):
        left, right = socket.socketpair()
        try:
            channel = Channel(left)
            right.sendall(b'{"type":"JOIN",')
            right.sendall(b'"udp_port":1234}\n{"type":"LEAVE"}\n')
            self.assertEqual(channel.receive()['udp_port'], 1234)
            self.assertEqual(channel.receive()['type'], 'LEAVE')
        finally:
            left.close()
            right.close()

    def test_reassembly_reorder_and_duplicates(self):
        metrics = Metrics()
        assembler = Assembler(metrics, 100)
        content = b'j' * 3500
        chunks = [unpack(d) for d in packetize(content, 1, 0, 0, 10)]
        for p in reversed(chunks):
            if metrics.packet(p, HEADER.size+len(p.payload), 20):
                assembler.add(p, 20)
        self.assertFalse(metrics.packet(chunks[0], 100, 20))
        self.assertEqual(assembler.ready(20.05), [])
        self.assertEqual(assembler.ready(20.11), [content])
        self.assertEqual(metrics.snapshot()['loss_pct'], 0)
        self.assertEqual(metrics.snapshot()['duplicates'], 1)

    def test_missing_frame_expires(self):
        metrics = Metrics()
        assembler = Assembler(metrics, 10)
        p = unpack(next(packetize(b'x' * 3000, 1, 0, 0, 1)))
        assembler.add(p, 1)
        self.assertEqual(assembler.ready(2), [])
        self.assertEqual(metrics.snapshot()['dropped_frames'], 1)
        self.assertFalse(assembler.pending)

    def test_loss_recovered_by_reorder(self):
        metrics = Metrics()
        packets = [unpack(d) for d in packetize(b'x'*3000, 1, 0, 0, 1)]
        metrics.packet(packets[0], 100, 1)
        metrics.packet(packets[2], 100, 1)
        self.assertAlmostEqual(metrics.snapshot()['loss_pct'], 33.33)
        metrics.packet(packets[1], 100, 1)
        self.assertEqual(metrics.snapshot()['loss_pct'], 0)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.resources = []

    def tearDown(self):
        for resource in reversed(self.resources):
            resource.stop()

    def sender(self, **kwargs):
        sender = Sender(VideoSource(width=320, fps=12), host='127.0.0.1', port=0, **kwargs)
        self.resources.append(sender)
        return sender.start()

    def receiver(self, sender, frames, **kwargs):
        receiver = Receiver('127.0.0.1', sender.port, on_frame=frames.append, **kwargs)
        self.resources.append(receiver)
        return receiver.start()

    def test_two_receivers_decode_and_export(self):
        from PIL import Image
        sender = self.sender()
        frames_a, frames_b = [], []
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / 'stats.csv'
            a = self.receiver(sender, frames_a, csv_path=csv_path)
            b = self.receiver(sender, frames_b)
            self.assertTrue(wait_for(lambda: len(frames_a) >= 8 and len(frames_b) >= 8))
            self.assertTrue(wait_for(lambda: a.metrics.snapshot()['rtt_ms'] > 0))
            self.assertEqual(len(sender.snapshot()['peers']), 2)
            for jpeg in (frames_a[-1], frames_b[-1]):
                image = Image.open(io.BytesIO(jpeg))
                image.load()
                self.assertEqual(image.size, (320, 180))
            a.stop()
            self.assertTrue(wait_for(lambda: len(sender.snapshot()['peers']) == 1))
            before = len(frames_b)
            self.assertTrue(wait_for(lambda: len(frames_b) >= before+3))
            with csv_path.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertGreater(int(rows[-1]['frames']), 0)

    def test_zero_buffer_still_assembles_chunks(self):
        sender = self.sender()
        frames = []
        self.receiver(sender, frames, buffer_ms=0)
        self.assertTrue(wait_for(lambda: len(frames) >= 5))

    def test_discovery(self):
        sender = self.sender()
        self.assertTrue(wait_for(lambda: sender.discovery is not None))
        found = discover(.5)
        self.assertTrue(any(x['port'] == sender.port for x in found))

    def test_jitter_reordering(self):
        sender = self.sender(jitter_ms=25)
        frames = []
        receiver = self.receiver(sender, frames, buffer_ms=150)
        self.assertTrue(wait_for(lambda: len(frames) >= 8))
        self.assertEqual(receiver.metrics.snapshot()['dropped_frames'], 0)

    def test_loss_still_plays_independent_frames(self):
        sender = self.sender(loss=10)
        frames = []
        receiver = self.receiver(sender, frames, buffer_ms=150)
        self.assertTrue(wait_for(lambda: len(frames) >= 5, timeout=6))
        self.assertGreater(sender.snapshot()['simulated_drops'], 0)
        self.assertGreater(receiver.metrics.snapshot()['missing'], 0)

    def test_sender_shutdown_and_restart_port(self):
        sender = self.sender()
        frames = []
        receiver = self.receiver(sender, frames)
        self.assertTrue(wait_for(lambda: len(frames) > 1))
        port = sender.port
        sender.stop()
        self.assertTrue(wait_for(receiver.stop_event.is_set))
        replacement = Sender(VideoSource(width=320), host='127.0.0.1', port=port)
        self.resources.append(replacement)
        replacement.start()
        self.assertEqual(replacement.port, port)

    def test_invalid_join_does_not_stop_sender(self):
        sender = self.sender()
        sock = socket.create_connection(('127.0.0.1', sender.port))
        try:
            channel = Channel(sock)
            channel.send('JOIN', udp_port=-1)
            self.assertEqual(channel.receive()['type'], 'ERROR')
        finally:
            sock.close()
        frames = []
        self.receiver(sender, frames)
        self.assertTrue(wait_for(lambda: bool(frames)))

    def test_finite_source_drains_playout(self):
        source = VideoSource(width=320, fps=10)
        original_read = source.read
        counter = [0]
        def read():
            counter[0] += 1
            return original_read() if counter[0] <= 6 else None
        source.read = read
        sender = Sender(source, host='127.0.0.1', port=0).start()
        self.resources.append(sender)
        frames = []
        receiver = self.receiver(sender, frames, buffer_ms=250)
        self.assertTrue(wait_for(receiver.stop_event.is_set))
        self.assertEqual(len(frames), 6)

    def test_video_file_decode_and_eof(self):
        import cv2
        import numpy as np
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'video.avi')
            writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), 10, (160, 120))
            self.assertTrue(writer.isOpened())
            for i in range(10):
                writer.write(np.full((120, 160, 3), i*20, dtype=np.uint8))
            writer.release()
            source = VideoSource(path, width=320, fps=10)
            try:
                count = 0
                while source.read() is not None:
                    count += 1
                    self.assertLess(count, 15)
                self.assertEqual(count, 10)
            finally:
                source.close()


if __name__ == '__main__':
    unittest.main()
