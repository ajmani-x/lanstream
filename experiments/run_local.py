"""Run reproducible LANStream loss/jitter experiments on loopback.
Usage: python -m experiments.run_local --seconds 6 --output captures/experiment.csv
"""
import argparse
import csv
import random
import time
from pathlib import Path
from lanstream.media import VideoSource
from lanstream.network import Sender, Receiver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=6)
    parser.add_argument('--output', default='captures/experiment.csv')
    args = parser.parse_args()
    rows = []
    for loss, jitter, buffer in [(0, 0, 120), (2, 0, 120), (5, 0, 120), (0, 80, 120), (0, 160, 40), (0, 160, 250)]:
        random.seed(42)
        sender = Sender(VideoSource(width=320, fps=15), host='127.0.0.1', port=0, loss=loss, jitter_ms=jitter)
        receiver = None
        try:
            sender.start()
            receiver = Receiver('127.0.0.1', sender.port, buffer_ms=buffer).start()
            receiver.stop_event.wait(args.seconds)
            stats = receiver.metrics.snapshot()
            row = dict(configured_loss_pct=loss, max_jitter_ms=jitter, buffer_ms=buffer, **stats)
            rows.append(row)
            print(row, flush=True)
        finally:
            if receiver:
                receiver.stop()
            sender.stop()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved {path}')


if __name__ == '__main__':
    main()
