# LANStream

A peer-to-peer video streaming application for computers on the same local network. Built with Python, LANStream combines TCP session control with UDP video transport and provides live network statistics, configurable packet loss, and jitter experiments.

## Features

- Stream video files or a built-in animated demo over a LAN.
- Connect multiple receivers to one source.
- Use TCP for session management and UDP for video delivery.
- Reassemble numbered video chunks with duplicate detection and buffering.
- Monitor throughput, estimated packet loss, jitter, and control round-trip time.
- View a live receive-throughput graph.
- Simulate packet loss and random delivery delays.
- Export receiver statistics to CSV and save individual frames.
- Discover active senders on the local network.
- Run through a desktop interface or command-line tools.

## How It Works

```text
Video file / animated demo
          ↓
Resize and encode each frame as JPEG
          ↓
Split frames into numbered chunks
          ↓
Send UDP packets to each receiver
          ↓
Validate packets and reassemble frames
          ↓
Buffer and display complete frames
```

A separate TCP connection handles joining, metadata exchange, heartbeat messages, statistics reports, and disconnection.

Every application instance can act as a sender, receiver, or both. During a stream, the source sends a separate copy of each media packet to every receiver. Receivers do not relay video to other peers.

## Requirements

- Python 3.10 or newer
- Tkinter
- Pillow
- OpenCV

Internet access is needed to install dependencies initially. Streaming itself only requires a reachable local network.

Wireshark and NS-2 are optional analysis tools.

## Installation

Clone or download this repository and open a terminal in the project directory.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

On Linux, install your distribution’s matching Python Tk and venv packages if they are missing.

After installation, `start.command` on macOS and `start.bat` on Windows provide convenient launchers.

## Quick Start

### Test on One Computer

1. Launch the application.
2. Keep the animated demo selected.
3. Click **Start sender**.
4. Set the sender address to `127.0.0.1` and the TCP port to `5000`.
5. Click **Join stream**.

The playback window should show the animation while packet counters and network statistics update.

To test multiple receivers, launch another application instance and join the same sender without starting a second sender on that port.

### Stream Between Computers

1. Connect both computers to the same Wi-Fi or Ethernet LAN.
2. Launch the application on each computer.
3. Start a sender on the source computer.
4. Enter the source computer’s displayed **Local IP** on each receiver.
5. Use the same TCP control port and click **Join stream**.

Allow Python through the firewall when required. Guest Wi-Fi networks with client isolation may block communication between devices.

`127.0.0.1` refers to the current computer; use the sender’s LAN IP when connecting from another device.

## Network Experiments

The application provides three controls for studying playback under different conditions:

| Setting | Purpose |
|---|---|
| Loss (%) | Probability of intentionally discarding each outgoing packet copy |
| Jitter (ms) | Maximum additional random delay applied to each outgoing packet copy |
| Buffer (ms) | Receiver waiting time for frame assembly and playout |

Example conditions:

| Experiment | Loss | Jitter | Buffer |
|---|---:|---:|---:|
| Baseline | 0% | 0 ms | 120 ms |
| Packet loss | 5% | 0 ms | 120 ms |
| High jitter, short buffer | 0% | 160 ms | 40 ms |
| High jitter, larger buffer | 0% | 160 ms | 250 ms |

Restart the affected sessions after changing settings. Keep the source, FPS, resolution, and JPEG quality consistent when comparing runs.

A larger buffer can improve tolerance of delayed packets, but it adds playback delay and cannot recover permanently lost chunks.

## Dashboard Metrics

| Metric | Meaning |
|---|---|
| Throughput | Accepted UDP application bytes received during the last second, expressed in Mb/s |
| Packet loss | Estimated gaps within the observed packet sequence range |
| Jitter | Smoothed variation in relative packet transit timing |
| Control RTT | Round-trip time measured using TCP PING/PONG messages |
| Frames played | Complete frames released to the playback callback |
| Incomplete frames | Partially received frames discarded after expiration or eviction |
| Average FPS | Complete frames released per second over the receiver session |

The green graph shows **receive throughput**, sampled approximately every half-second and retaining about 50 seconds of history. Its vertical scale adjusts automatically.

Configured loss and jitter are experiment inputs; the measured values need not match them exactly. Reordered packets can temporarily appear missing, and throughput alone does not indicate playback quality.

Receiver statistics are automatically written to CSV files under `captures/`.

## Command-Line Usage

Run these commands with the virtual environment activated.

```bash
# Stream the animated demo
python -m lanstream send

# Stream a video file repeatedly
python -m lanstream send --file movie.mp4 --loop

# Apply artificial packet loss and delay
python -m lanstream send --loss 5 --jitter 80

# Receive and record statistics
python -m lanstream receive 192.168.1.10 --duration 30 --csv captures/run.csv

# Receive a local stream and save individual frames
python -m lanstream receive 127.0.0.1 --duration 5 --save-frames captures/frames

# Discover active senders
python -m lanstream discover
```

Run sender and receiver commands in separate terminals. CLI receivers collect statistics and optionally save JPEGs; use the desktop interface for live playback.

## Wireshark Analysis

Capture the loopback interface for same-computer tests, or the appropriate Wi-Fi/Ethernet interface for LAN tests.

Useful display filters:

| Traffic | Filter |
|---|---|
| TCP control, default port | `tcp.port == 5000` |
| LANStream video packets | `udp.payload[0:4] == 4c:56:53:31` |
| Sender discovery | `udp.port == 5002` |

Use **Follow → TCP Stream** to inspect session messages and **Statistics → I/O Graphs** to examine traffic rates.

Video uses dynamically assigned UDP ports. Wireshark does not automatically calculate loss and jitter for this custom media protocol; use application statistics and sequence numbers alongside captures.

## Testing

```bash
# Unit and local networking integration checks
python -m unittest discover -s tests -v

# Desktop playback smoke check
python -m experiments.gui_smoke

# Run six local loss/jitter experiment conditions
python -m experiments.run_local --seconds 6 --output captures/experiment.csv
```

The GUI smoke check requires a graphical desktop. Networking checks require permission to open local TCP and UDP sockets.

## Project Structure

```text
lanstream/
├── __main__.py       # Entry point and command-line interface
├── gui.py            # Desktop dashboard and playback
├── media.py          # Video decoding and generated demo
├── protocol.py       # Binary media and JSON control framing
├── network.py        # Discovery, sender, and receiver
└── metrics.py        # Statistics, frame assembly, and CSV recording

docs/                 # Architecture, lab guide, and code walkthrough
experiments/          # Local experiments, GUI check, and optional NS-2 tools
tests/                # Automated checks
captures/             # Generated statistics and capture outputs
main.py               # Desktop launcher
requirements.txt      # Runtime dependencies
pyproject.toml        # Package configuration
```

## Documentation

- [Architecture and protocol](docs/ARCHITECTURE.md)
- [Lab and Wireshark guide](docs/LAB_GUIDE.md)
- [Code walkthrough](docs/CODE_WALKTHROUGH.md)
- [Viva notes](docs/VIVA.md)
- [Validation record](docs/VALIDATION.md)

## Scope and Limitations

- Video only; audio is not transmitted.
- Intended for trusted local networks, without authentication or encryption.
- No NAT traversal, media retransmission, or adaptive congestion control.
- Sender bandwidth increases with receiver count.
- Packet loss estimates cannot identify unknown losses before the first or after the last observed sequence number.
- Control RTT is not an exact measurement of one-way video latency.
- JPEG frames use more bandwidth than codecs that compress across frames.
- The optional NS-2 model approximates UDP traffic; it does not run or decode the application’s video stream.
