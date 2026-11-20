# Demonstration and analysis guide

## Demonstration checklist

1. Launch two instances on one computer. Start demo sender in one and join `127.0.0.1` in the other.
2. Show TCP JOIN/INFO in Wireshark, UDP media, and increasing receiver frame/packet counters.
3. Join a second receiver. Show source fan-out and two entries in the peer list.
4. Leave one receiver. The other continues.
5. Stream an actual video file. Show JPEG playback and CSV output.
6. Restart the sender with loss `2%`, then `5%`. Compare loss estimates and complete frames.
7. Restart with `160 ms` jitter and a `40 ms` receive buffer, then compare with `250 ms` buffer.
8. Repeat between separate machines on the same LAN. Record computer IPs, connection type and settings.

## Wireshark

Use the loopback interface for same-computer tests and the Wi-Fi/Ethernet interface for separate machines. Select the interface before starting capture. Start capture before joining so control metadata is included. On a custom TCP port, substitute that port in the filters below.

| Goal | Display filter |
|---|---|
| Control channel | `tcp.port == 5000` |
| Media packets by magic | `udp.payload[0:4] == 4c:56:53:31` |
| Discovery | `udp.port == 5002` |
| Two lab machines | `ip.addr == 192.168.1.10 && ip.addr == 192.168.1.11` |
| TCP retransmissions | `tcp.analysis.retransmission` |
| One exact media port | `udp.port == PORT_FROM_SENDER_LOG` |

Use **Follow → TCP Stream** to read JOIN, INFO, PING/PONG, STAT and LEAVE/END. There is no audio stream. Use **Statistics → Conversations** to identify separate receiver flows. Use **Statistics → I/O Graphs** to compare rates. Inspect media bytes: the first four bytes are ASCII `LVS1`; the binary header layout is in ARCHITECTURE.md.

UDP alone has no universal loss counter. Compare application sequence numbers and application CSV metrics. A receiver-side capture shows what reached that host; a sender-side capture alone cannot establish downstream delivery. TCP control and UDP media have different workloads, so this capture demonstrates their behavior but is not a controlled comparison of TCP versus UDP media performance. Save actual captures as `.pcapng` under `captures/`.

## Local impairment experiment

```bash
python -m experiments.run_local --seconds 6 --output captures/experiment.csv
```

Six conditions run sequentially on loopback. Random seed 42 controls the impairment generator, but scheduling and network behavior still vary. Results are measured on your machine; repeat longer runs (30 seconds per condition) for a report. The CSV includes the configuration and observed statistics. At larger jitter, a short buffer tends to discard frames; increasing the buffer can recover complete frames at the cost of delay. At packet loss p, a frame with n independently lost packets survives with probability approximately `(1-p)^n`; larger JPEGs are more vulnerable.

## NS-2 experiment

NS-2 is separate from the Python dependencies. Run in a Linux environment with the `ns` executable available. From the project root:

```bash
mkdir -p captures
ns experiments/streaming.tcl 10ms 0.00 2Mb captures/baseline
ns experiments/streaming.tcl 50ms 0.00 2Mb captures/delay
ns experiments/streaming.tcl 10ms 0.02 2Mb captures/loss
ns experiments/streaming.tcl 10ms 0.00 5Mb captures/congestion
python experiments/analyze_trace.py captures/baseline.tr
python experiments/analyze_trace.py captures/delay.tr
python experiments/analyze_trace.py captures/loss.tr
python experiments/analyze_trace.py captures/congestion.tr
```

Topology: source → router → receiver; access link 10 Mb/s, bottleneck 3 Mb/s, queue limit 40 packets. UDP CBR uses 1192-byte packets for ten seconds. The script varies propagation delay, random packet loss and offered load. Above-capacity load produces queueing and delay variation. It does not directly generate independently random propagation jitter; the Python experiment supplies explicit random per-packet jitter. The trace analyzer reports source enqueues, destination receives, missing packet percentage, mean end-to-end simulated delay, adjacent packet delay variation and received throughput. Simulated delay is known from the single simulator clock; it is different from measured application TCP RTT.

Do not treat the CBR model as a video decoder or measured LAN result. Attach your actual trace files and compare trends. If NS-2 is not installed, the Python application and local impairment experiment remain usable.

## Report template

Record for every run: duration, machine IDs, Wi-Fi/Ethernet, video resolution/FPS/quality, receiver count, configured loss/jitter/buffer, measured throughput/loss/jitter/RTT, complete/incomplete frames, and capture filenames. Include screenshots of playback, TCP stream, UDP header, and I/O graph. Explain differences in measured throughput between sender and receiver and document the measurement limitations in README.md.

## Troubleshooting

- No connection: confirm sender is running; check IP, TCP port, firewall and Wi-Fi client isolation.
- Connected but no video: check UDP firewall permissions and received packet count; reduce loss, width or quality; increase buffer for jitter.
- Discovery empty: use the sender IP and port manually. Broadcast filtering does not necessarily block direct connections.
- Port busy: stop the old sender or choose another TCP port on both peers.
- High loss on Wi-Fi: reduce width/FPS/quality and receiver count, or use Ethernet.
- No file playback: try a common MP4 or AVI file; unsupported codecs depend on the installed OpenCV build.
- Tk import failure: install Python with Tk support. CLI modes work without Tk.
