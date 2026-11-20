# Validation record

Validation performed on this computer on 18 November 2026, using Python 3.13.5, OpenCV 4.11.0, Pillow 13.0.0 and Tk 8.6.

## Automated checks

`python -m unittest discover -s tests -v`: **16 checks passed**.

Coverage includes binary framing and MTU bounds, malformed packets, TCP fragmentation/coalescing, reordered and duplicate packets, missing-frame expiration, loss estimation, two simultaneous receivers, JPEG decode, CSV export, discovery, simulated jitter/loss, zero-buffer assembly, invalid joins, source shutdown/port reuse, buffered EOF drain, actual AVI decoding, and NS-2 trace parsing against a small known fixture.

`python -m experiments.gui_smoke`: **passed**. This opened the actual Tk window, started a sender, joined it, rendered received JPEG frames, checked that start/join/stop controls fit within the window, and stopped both sessions. The check exited automatically.

`python -m compileall -q lanstream tests experiments`: passed.

## Measured local experiments

`python -m experiments.run_local --seconds 3 --output captures/experiment.csv` produced six real loopback measurements. The initial measurement set is included in `captures/experiment.csv`.

| Configured loss | Maximum packet delay | Buffer | Frames played | Incomplete frames | Observed loss estimate |
|---|---|---|---|---|---|
| 0% | 0 ms | 120 ms | 44 | 0 | 0.00% |
| 2% | 0 ms | 120 ms | 37 | 7 | 2.54% |
| 5% | 0 ms | 120 ms | 36 | 8 | 3.33% |
| 0% | 80 ms | 120 ms | 44 | 0 | 0.00% |
| 0% | 160 ms | 40 ms | 0 | 45 | 1.11% |
| 0% | 160 ms | 250 ms | 42 | 0 | 1.11% |

These are short runs, not performance guarantees. At high jitter, the endpoint snapshot can include sequence gaps for packets still in flight; a nonzero gap estimate is not necessarily permanent loss. Longer repeated runs are more useful for a report. Frame loss is more severe than packet loss because a JPEG frame needs all of its chunks. A larger buffer restored playback under the measured high-jitter condition.

## Remaining external checks

- Separate physical machines and Wi-Fi/firewall behavior require a real LAN; only loopback transport was exercised here.
- NS-2 is not installed on this computer. The simulator script and trace-analysis tooling are included, but no NS-2 execution or simulation results are claimed.
- Wireshark captures must be taken on the actual chosen interface. No fabricated capture files are supplied.
