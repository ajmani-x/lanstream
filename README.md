# LANStream: complete beginner, code study, and demonstration guide

LANStream sends video directly from one computer to other computers on the same local network. It also lets you observe what happens when packets are lost or arrive at uneven times.

This guide explains the project from the beginning. You do not need NS-2 or Wireshark to run the application. Wireshark is useful for showing real network packets; NS-2 is an optional, separate experiment included because it appears in the original synopsis. The application currently streams video only, without audio.

## Contents

1. [What the project does](#1-what-the-project-does)
2. [Basic concepts](#2-basic-concepts)
3. [Installation and running](#3-installation-and-running)
4. [What happens from Start to playback](#4-what-happens-from-start-to-playback)
5. [Every part of the dashboard](#5-every-part-of-the-dashboard)
6. [What the moving demo means](#6-what-the-moving-demo-means)
7. [What the graph actually shows](#7-what-the-graph-actually-shows)
8. [Loss, jitter, buffering, and their formulas](#8-loss-jitter-buffering-and-their-formulas)
9. [How to demonstrate and test the project](#9-how-to-demonstrate-and-test-the-project)
10. [Which code files to study](#10-which-code-files-to-study)
11. [Important code explained](#11-important-code-explained)
12. [Wireshark demonstration](#12-wireshark-demonstration)
13. [CSV files and command-line experiments](#13-csv-files-and-command-line-experiments)
14. [Troubleshooting and limitations](#14-troubleshooting-and-limitations)
15. [Presentation and viva answers](#15-presentation-and-viva-answers)

For a numbered explanation of **every nonblank line in the application code**, open [CODE_WALKTHROUGH.md](docs/CODE_WALKTHROUGH.md). Read this README first, then use the walkthrough beside your editor. Blank lines only separate sections; they do not execute.

## 1. What the project does

Imagine you have a video on your laptop. Your friend wants to watch it on their laptop while connected to the same Wi-Fi. Instead of uploading the video to a website, your laptop reads the video, compresses its pictures, splits them into small packets, and sends those packets directly to your friend's computer. Their computer reconstructs the pictures and displays them.

The sender can send the same stream to several receivers. Each receiver gets its own copy of the UDP packets. Any application instance can send, receive, or do both.

This is a peer-to-peer application with a source-to-receivers topology. For a particular stream, one peer acts as its source. There is no separate central media server, cloud account, or registration service. Receivers do not forward video to one another in this implementation.

The project has two purposes:

- Build a working LAN video stream using socket programming.
- Study network behavior by observing throughput, packet gaps, arrival variation, round-trip time, and playback under controlled loss and delay.

## 2. Basic concepts

### 2.1 LAN, IP address, and localhost

A **LAN**, or Local Area Network, connects devices in a limited area, such as a home, lab, or hostel. Wi-Fi or Ethernet can provide this connection. Internet access is unnecessary once dependencies are installed.

An **IP address** identifies a network interface so packets can be routed to it. A typical local address might look like `192.168.1.10`; your actual address may differ.

`127.0.0.1` is **loopback**, meaning "this computer." Use it when sender and receiver run on one computer. Your friend must enter your actual LAN IP to connect to you. Entering `127.0.0.1` on their computer connects back to their own computer.

`0.0.0.0` is the sender's default bind address: listen on available IPv4 interfaces. It is not the address your friend should type as the destination.

### 2.2 Ports and sockets

An IP address finds a computer; a **port** identifies a network endpoint used by an application on it. An IP and port together form an address such as `192.168.1.10:5000`.

A **socket** is the programming interface through which the app sends or receives network data.

| Purpose | Protocol and port |
|---|---|
| Joining, metadata, heartbeats and reports | TCP, default port `5000` |
| Discovering active senders | UDP, port `5002` |
| Sending and receiving video | UDP, ports automatically chosen by the OS |

The receiver tells the sender its media port during JOIN. The sender advertises its own media source port in INFO. Video does not use a fixed UDP port `5000`.

### 2.3 TCP versus UDP

**TCP** provides an ordered, reliable byte stream while the connection remains usable. It handles retransmission, but the application must still decide where one message ends and another begins. Our control messages end with a newline.

**UDP** sends individual datagrams without guaranteeing delivery, order, or duplicate suppression. Our app supplies sequence numbers, chunk indexes, buffering, and duplicate detection itself.

We use TCP for control because a missing JOIN or metadata message would prevent a session from working. We use UDP for media so the receiver can skip incomplete pictures and continue with later ones without waiting for media retransmission.

UDP is not automatically faster in every situation. This application prioritizes timely independent frames and accepts missing frames. It does not implement adaptive bitrate or congestion control.

### 2.4 Video, frames, JPEG, chunks, and packets

A video is a sequence of pictures called **frames**. At 20 FPS, the source targets 20 pictures each second: approximately one every 50 ms.

The source encodes each picture as an independent **JPEG**. If one JPEG cannot be reconstructed, the next JPEG can still be decoded. This is convenient for a networking demonstration, but costs more bandwidth than codecs that compress across frames.

A JPEG may be larger than one network-friendly packet, so it is split into **chunks** of at most 1160 bytes. A 32-byte application header is attached to each chunk, giving a maximum application UDP payload of 1192 bytes.

```text
One JPEG frame, for example 5000 bytes
        |
        +-- chunk 0: 1160 bytes + header
        +-- chunk 1: 1160 bytes + header
        +-- chunk 2: 1160 bytes + header
        +-- chunk 3: 1160 bytes + header
        +-- chunk 4:  360 bytes + header
```

All five chunks are needed for that frame. A **packet sequence number** identifies each chunk transmission in the source stream; a **frame number** groups chunks belonging to the same picture. A frame is not the same thing as a packet.

### 2.5 MTU and headers

A network's **Maximum Transmission Unit (MTU)** limits the size of a packet carried without fragmentation. A typical LAN MTU is 1500 bytes. Our largest application payload is 1192 bytes; adding normal IPv4 and UDP headers gives 1220 bytes, below that typical limit. Other network paths can have different limits.

The app header carries the stream ID, packet sequence number, frame number, chunk index, number of chunks, and a sender timestamp. It is described in [section 11](#11-important-code-explained).

### 2.6 Threads, queues, locks, and time

A **thread** lets the application handle network work while its window stays responsive. The sender accepts connections, handles TCP sessions, encodes/schedules media, and answers discovery in separate threads. The receiver handles media and control in separate threads.

A **lock** protects shared state such as the sender's peer list and receiver metrics. A **queue** passes messages or frames safely between threads. Tk widgets are updated on the main GUI thread.

`time.monotonic()` measures elapsed time using a clock that does not jump when the wall-clock date/time changes. Its starting point is not shared between computers. The app uses time differences rather than subtracting absolute monotonic readings from different machines.

## 3. Installation and running

### 3.1 On the original Mac with the prepared environment

Open a terminal in the project directory:

```bash
cd /Users/aryanajmani/Desktop/cn_project
.venv/bin/python main.py
```

You can also double-click `start.command` on this Mac.

### 3.2 On another Mac or Linux computer

Install Python 3.10 or newer with Tk support. Extract `LANStream.zip`, open a terminal in its `LANStream` folder, then run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

On Linux, install your distribution's matching Python Tk and venv packages if those components are missing.

### 3.3 On Windows

Install Python 3.10 or newer with Tk support and enable its PATH option. Extract the ZIP, open **Command Prompt** in the extracted project folder, then run:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

If your installation provides `py` instead of `python`, use `py -m venv .venv` for the first command. After setup you can double-click `start.bat`.

Pillow draws/encodes demo images and displays received JPEGs. OpenCV reads video files. Tk provides the desktop window. Internet is needed to download dependencies initially; it is not needed for normal LAN streaming. Do not copy `.venv` between different computers: recreate it there.

### 3.4 Testing with a friend

1. Connect both computers to the same reachable Wi-Fi or Ethernet LAN.
2. Run the app on both computers.
3. On the source computer, click **Start sender**.
4. On the receiver computer, enter the source computer's **Local IP** displayed in the header.
5. Use the same TCP control port, normally `5000`, and click **Join stream**.
6. Allow Python through the local firewall if prompted. UDP media also needs to pass.

The **Discover LAN senders** button broadcasts a request and fills in the first discovered result. If broadcasts are blocked, enter the sender IP manually. Guest networks may isolate devices even when they share a Wi-Fi name.

## 4. What happens from Start to playback

```text
Start sender
    |
    +-- Open TCP listener for session control
    +-- Open UDP media socket and discovery responder
    +-- Wait for a receiver before reading the source

Join stream
    |
    +-- Receiver opens its own UDP socket
    +-- Receiver connects to the sender over TCP
    +-- JOIN tells the sender the receiver's UDP port
    +-- INFO tells the receiver the stream ID, codec, and source UDP port

Continuous streaming
    |
    +-- Source reads/generates one picture
    +-- Source resizes it and encodes it as JPEG
    +-- packetize() splits it and adds headers
    +-- Sender applies configured artificial loss and random delay
    +-- Sender transmits UDP copies to each receiver
    +-- Receiver validates source, session, and packet format
    +-- Metrics tracks sequence gaps and packet arrival timing
    +-- Assembler collects chunks until each frame's deadline
    +-- Complete frames go to playback; incomplete frames are skipped
    +-- GUI displays the latest JPEG and updates metrics/graph
```

Meanwhile, the receiver sends PING and STAT messages roughly once per second. The sender echoes PONG and stores peer reports. LEAVE disconnects one receiver. END indicates source completion or shutdown; receivers allow a short drain period for buffered frames.

A later receiver joins the source's current playback position. This is not a separate on-demand playback session for each receiver.

## 5. Every part of the dashboard

### 5.1 Source and connection controls

| Display or control | What it means |
|---|---|
| Local IP | An address chosen using a routing lookup; often your LAN address. VPNs/multiple adapters can make a different address necessary. |
| Video source | The generated animation or the filename being sent. |
| Choose video | Select an MP4/AVI/MOV/MKV/WebM file supported by the OpenCV build. |
| Use demo | Select the built-in animated source; no video download is required. |
| Loop video | When a selected file ends, start it again. The generated demo already continues until stopped. |
| Sender IP / hostname | The destination to use when this instance joins a stream. |
| TCP control port | Sender listen port and receiver connection port; both ends must agree. |
| Discover LAN senders | Find senders using UDP discovery. It does not automatically join. |
| Start sender | Start serving the selected source. It does not automatically join or show received playback. |
| Join stream | Become a receiver of the entered sender. Joining your own sender is supported. |
| Stop all sessions | Stop both sender and receiver roles in this instance. Other receivers of a sender stop receiving when that sender is stopped. |
| Save current frame | Save the last received image as a JPEG, not as an entire recorded video. |

### 5.2 Media and network settings

| Setting | Allowed values | Meaning and likely effect |
|---|---|---|
| FPS | 1–60 | Target source pictures per second; larger values usually increase bandwidth and processing work. |
| Width | 160–1920 pixels | Source picture width; aspect ratio is preserved for files. Larger images usually make larger JPEGs. |
| JPEG quality | 10–95 | JPEG encoder quality setting, not percent of delivered frames. Higher settings usually increase image detail and bytes. |
| Loss (%) | 0–100 | Probability that each outgoing packet copy is intentionally discarded at the sender. |
| Jitter (ms) | 0–2000 | Maximum artificial random delay for each outgoing packet copy; delay is sampled between zero and this value. |
| Buffer (ms) | 0–3000 | Receiver playout wait, giving chunks time to arrive and be reordered. Larger values can improve playback under jitter but add delay. |

FPS, width, quality, loss, jitter, source selection and loop apply to a new sender. Buffer applies to a new receiver. Editing a box does not change an already running session. Restart the affected role; for the same-window demonstration, use **Stop all sessions**, then start and join again.

### 5.3 Metric cards and counters

| Display | Exact meaning in this app |
|---|---|
| THROUGHPUT, Mb/s | Valid, unique UDP application bytes received during the last second, multiplied by 8 and divided by 1,000,000. Includes our 32-byte header, excludes UDP/IP/link headers. |
| PACKET LOSS, % | Running estimate of missing packet sequence numbers within the observed range; not the sender's configured loss probability. |
| JITTER, ms | Smoothed variation in relative packet transit timing, computed from receive intervals and sender timestamp intervals. |
| CONTROL RTT, ms | Time for a TCP PING to travel to the source and its matching PONG to return. Not one-way video latency. |
| Frames played | Complete frames released by the assembler to the playback callback. The GUI can skip stale queued images when slow, so this is not an exact screen refresh count. |
| Incomplete | Partially received frames discarded at a deadline or buffer eviction. Frames with every packet lost are not counted here. |
| Late | First arrivals of previously unobserved frames more than 100 ms beyond their calculated deadline. Does not count every late packet. |
| Avg FPS | Frames released / elapsed receiver time. It is a session average, not instantaneous source FPS. |
| Packets | Number of valid unique packets accepted by receiver metrics. |
| Connected receivers | Currently registered peers in this sender instance. |
| Sent packets | Successful UDP send calls across all receivers; this is not confirmation of downstream delivery. |
| Simulated drops | Packet copies discarded by the impairment logic, including its queue-cap safeguard. |
| Peer loss in the list | The peer's latest STAT report, received roughly once per second. |
| Log and status line | Join/leave, source completion, discovery, and error messages. |

Metric cards and the green graph describe this instance's **receiver**. Sender-only windows can show outgoing counts without showing received playback or receiver metrics. At startup, RTT=0 can mean no reply has been measured yet.

## 6. What the moving demo means

The demo is generated in `VideoSource.read()` in [media.py](lanstream/media.py). It is a test picture, not a visualization of packets travelling across the LAN.

| Visible part | Meaning |
|---|---|
| Dark grid | A static background to make motion easy to see. |
| Moving green circle | A synthetic object following sine/cosine motion. Smooth movement helps demonstrate continuous frame delivery. |
| Frame number | Source frame index. Gaps in visible numbers can result from skipped/incomplete frames or GUI refresh sampling. |
| Time in seconds | Source media time, calculated as frame index / target FPS; not wall-clock time or measured network delay. |
| FPS printed inside the image | Configured target source FPS; not measured receiver playback FPS. |

The motion is generated with:

```python
phase = self.index / self.fps
cx = int(w / 2 + math.sin(phase * 1.4) * w * .32)
cy = int(h / 2 + math.cos(phase * 1.9) * h * .24)
```

`phase` advances as frames are generated. `sin()` and `cos()` move the circle left/right and up/down. The sender then JPEG-encodes this picture and transmits it exactly like a file-derived picture.

Loss and jitter do not change the circle's mathematical path. They affect which pictures the receiver can show and when. If pictures are skipped, the circle may jump. If no new complete picture reaches the GUI, the last shown picture can stay on screen, looking frozen. A larger buffer can smooth delivery but cannot recreate packets that were permanently lost.

Even healthy playback can visibly skip some frame numbers: the GUI polls at about 40 ms and keeps only the latest queued picture. The source FPS label therefore does not prove every frame was physically drawn on the screen.

## 7. What the graph actually shows

The green line below the metric cards is **receive throughput over recent time**. It is not a loss graph, jitter graph, latency graph, video-quality score, or representation of the circle's position.

- **Horizontal direction:** time, from older samples on the left toward newer samples on the right.
- **Vertical direction:** received throughput. Higher points mean more accepted application bytes in the recent one-second window.
- **Sampling interval:** the GUI requests a sample approximately every 500 ms.
- **History:** it keeps at most 100 samples, nominally about 50 seconds.
- **Units:** the associated throughput card is in decimal megabits per second (Mb/s).

The graph has no numeric axis ticks. At startup its line fills from the left. Once it has 100 samples, older samples disappear as new ones are appended. GUI scheduling can make the actual duration slightly different from 50 seconds. History is not cleared when a new receiver session starts in the same window, so a restart can leave earlier-session samples visible temporarily.

### 7.1 The formula and a numerical example

```text
Throughput (Mb/s) = received application bytes in the last second × 8 / 1,000,000
```

If the last second contains 100,000 accepted bytes:

```text
100,000 × 8 / 1,000,000 = 0.8 Mb/s
```

The graph appends the same rounded `throughput_mbps` statistic used by the card. This is the received stream rate, not your Wi-Fi's maximum speed or the available unused network capacity. The first partial second is not extrapolated to a full second.

### 7.2 Why the line moves up and down

JPEG sizes vary with image content. Frame pacing, OS scheduling, packet arrival variation, and packets entering/leaving the sliding one-second window also affect the number. Loss reduces the amount delivered. Jitter can bunch packets into bursts even without permanent loss.

The graph counts valid received packets even if their frame is later incomplete or too late to play. Consequently, the graph can look healthy while the video is choppy or frozen. Throughput alone does not measure playback quality.

### 7.3 Automatic vertical scaling

`App.update_stats()` chooses:

```python
scale = max(.1, max(self.history))
```

It maps the largest retained sample near the top. If an old peak leaves the history, the scale can change and move the visible line even when the absolute bitrate changes little. Compare the numeric throughput card or CSV files when making quantitative comparisons between runs. Two screenshots with similar line heights do not necessarily represent the same bitrate.

The sample's pixel coordinates are calculated using:

```python
x = i * (w - 10) / 99 + 5
y = h - 5 - value / scale * (h - 25)
```

Canvas coordinates grow downward, so a larger throughput subtracts more from `y` and draws a higher point. The `99` spreads 100 samples across the available width.

## 8. Loss, jitter, buffering, and their formulas

### 8.1 Configured packet loss versus observed packet loss

At the sender, every packet copy for every receiver goes through this decision:

```python
if random.random() * 100 < self.loss:
    self.simulated_drops += 1
    continue
```

`random.random()` generates a value from zero up to, but not including, one. At Loss=5, the condition is true with probability 5%. `continue` skips scheduling that particular packet copy.

This does not mean "drop exactly five out of every hundred" or "freeze for 5% of the time." It is an independent random decision per copy. Two receivers can lose different packets. More actual losses may also occur in the network or OS.

At the receiver:

```text
Expected packets = highest observed sequence − lowest observed sequence + 1
Missing packets  = max(0, expected packets − unique received packets)
Loss estimate %  = missing packets / expected packets × 100
```

Example: received packet numbers `100, 101, 103, 104`.

```text
Expected = 104 − 100 + 1 = 5
Received = 4
Missing  = 1
Loss     = 1 / 5 × 100 = 20%
```

If packet 102 arrives later, the estimate returns to 0%. Therefore the loss number can decrease as well as increase. It is cumulative across the receiver session, not a last-second loss percentage.

The receiver cannot infer missing packets before its first observed packet or beyond its last observed packet. At 100% artificial loss, no sequence numbers arrive: the app can show zero for its gap estimate while receiving nothing. That means the observed range is unknown, not successful delivery. Check packet/frame counts and source simulated drops as well.

### 8.2 Packet loss versus frame loss

A frame needs every chunk to be complete. If a picture uses ten packets and the independent packet loss probability is 5%, its approximate survival probability is:

```text
P(complete frame) = (1 − 0.05)^10 ≈ 0.599
```

Only about 60% of frames would survive under those simplified assumptions. Packet loss of 5% can therefore cause around 40% frame loss in that example. Actual results depend on frame size, timing, packet-loss behavior and buffer deadlines.

Increasing image width or JPEG quality usually makes more packets per frame and can make frame completion more vulnerable. Reducing width, quality or FPS can reduce load. Increasing the buffer does not recover packets that were never transmitted or permanently lost.

### 8.3 Configured jitter versus measured jitter

At the sender, a queued packet gets a due time:

```python
timestamp + random.uniform(0, self.jitter)
```

Internally `self.jitter` is in seconds. A configured 80 ms means each packet copy receives a random additional scheduled delay between 0 and 80 ms. A min-heap sends the earliest due packet first. Later sequence numbers can therefore arrive before earlier ones. OS scheduling and encoding work can add delay beyond the selected bound; the bound applies to the artificial component.

The JITTER card is not the same number as this input. It estimates variations in relative transit timing using:

```text
D = (current arrival − previous arrival)
    − (current sender timestamp − previous sender timestamp)

J = J + (|D| in milliseconds − J) / 16
```

This smoothing reduces sudden jumps. For example, if sender timestamps differ by 50 ms but arrivals differ by 70 ms, that pair contributes an absolute difference of 20 ms. Starting with J=0, the first update gives J=1.25 ms, not 20 ms. More observations gradually move the estimate.

All chunks of one frame carry the same sender timestamp. The app measures variation in arrival order, including reordered packets; this is an RTP-style formula used in a custom JPEG protocol, not actual RTP media transport.

Clock offsets cancel in the differences, so synchronized machine clocks are not required. Measured jitter can be nonzero with the artificial jitter input at zero because real scheduling and transport still vary.

### 8.4 What the buffer does

Without a buffer, the receiver may need a picture before all its pieces have arrived. A buffer adds waiting time so early and late pieces can be put back in order.

For the first valid packet, the assembler records an anchor: local arrival time and sender timestamp. Frame deadlines are then:

```text
Deadline = first local arrival
           + (frame sender timestamp − first sender timestamp)
           + configured buffer in seconds
```

This relates sender pacing to the receiver's local clock without assuming identical clock origins. The implementation also allows at least 15 ms from a frame's first packet for chunk assembly, even when Buffer=0.

At a deadline, a complete frame is released. A partially received frame is discarded. Too-old frames are rejected and pending data is bounded so memory cannot grow forever.

A buffer of 250 ms usually tolerates more arrival variation than 40 ms, but adds a larger baseline wait. It does not guarantee a particular total end-to-end delay: encoding, routing, scheduling, queueing, and display refresh also contribute.

### 8.5 RTT, latency, and FPS

The receiver sends a TCP PING containing a local timestamp, and the sender returns that same value in PONG:

```text
RTT ms = (receiver time at matching PONG − receiver time at PING) × 1000
```

This is a TCP control round trip, including processing/scheduling. It is not the time a particular JPEG took to reach the screen; dividing it by two does not establish exact one-way video delay.

Source FPS is a target. Receiver average FPS counts complete released frames divided by elapsed time, including connection and buffering time. It may start low, increase gradually, and remain below the source FPS under loss or slow processing.

## 9. How to demonstrate and test the project

### 9.1 Baseline: one computer, one window

1. Launch the application.
2. Select **Use demo**.
3. Set FPS=20, Width=640, Quality=70, Loss=0, Jitter=0, Buffer=120.
4. Click **Start sender**. The log shows the TCP and media UDP ports.
5. Enter Sender IP=`127.0.0.1`, TCP port=`5000`.
6. Click **Join stream** and let it run for 20–30 seconds.

Expected: the circle moves, frames and packet counters increase, throughput is nonzero, RTT becomes nonzero after a reply, and loss is normally near zero on a healthy loopback test. A small amount of timing variation is normal. Sender and receiver can exist in the same window because they use separate sockets and threads.

Say: "The source encodes independent JPEG frames, sends numbered chunks over UDP, and manages the session with TCP. The receiver reassembles and buffers frames."

### 9.2 Two receivers

Keep the first window sending and receiving. Open a second terminal in the project folder and run the app again. In the second window, enter `127.0.0.1:5000` and click **Join stream**; do not click Start sender there on the same port.

Expected: both windows play the current stream and the source shows two connected receivers. The sender sends a separate packet copy to each receiver, so its aggregate traffic increases. Each receiver's graph shows only its own received flow; it should not automatically double when another receiver joins.

Close or stop the second receiver. The first should continue. On a different computer, use the source LAN IP rather than loopback.

### 9.3 Compare packet loss

Use three separate 20–30 second runs. Click **Stop all sessions** before changing settings, then start the sender and join again.

| Run | Loss input | Jitter input | Buffer | What to observe |
|---|---|---|---|---|
| Baseline | 0% | 0 ms | 120 ms | Usually smooth movement, low sequence-gap estimate. |
| Moderate loss | 2% | 0 ms | 120 ms | More incomplete frames; gaps/jumps can become visible. |
| Greater loss | 5% | 0 ms | 120 ms | Typically more frame drops and reduced average playback FPS. |

Keep FPS, width, quality and source the same to make comparisons useful. Record source simulated drops, receiver loss estimate, incomplete frames, average FPS and throughput. The result is random, so use "observed" rather than claiming a guaranteed exact percentage.

Say: "The configured percentage is the sender's probability of discarding each packet. The displayed percentage is estimated at the receiver from sequence gaps. One missing chunk can make a whole JPEG unusable."

### 9.4 Compare jitter and buffers

Restart both roles for each run:

| Run | Loss | Maximum artificial delay | Receiver buffer | Expected trend |
|---|---|---|---|---|
| Small delay | 0% | 80 ms | 120 ms | Buffer often absorbs this variation on loopback. |
| Short buffer | 0% | 160 ms | 40 ms | Many frames may miss deadlines; movement can freeze or jump. |
| Larger buffer | 0% | 160 ms | 250 ms | More complete frames may play, with more waiting time. |

With high jitter, packet counts and throughput can remain substantial even when frames cannot be played. This is a useful demonstration: delivery rate alone does not guarantee real-time playback quality. In-flight reordered packets may temporarily produce a loss estimate even with zero configured loss.

Say: "The packets can arrive out of order or after their playback deadlines. A larger buffer waits longer, improving completion at the cost of delay."

### 9.5 Show an actual video file

Stop all sessions, click **Choose video**, pick a supported file, choose whether to loop, then start and join. Use moderate width/quality initially. The file's audio is not transmitted. The selected source FPS samples the file by media time rather than simply playing every original frame at a different speed.

### 9.6 Show a physical LAN connection

Repeat the baseline with the sender on one laptop and receiver on your friend's laptop. Show the actual IPs and connected peer entry. The same-machine test demonstrates sockets but does not verify your firewall, Wi-Fi or router configuration; the two-machine test does.

### 9.7 Collect evidence and end the demo

Take screenshots of normal playback, two peers, the loss run and the buffer comparison. Keep receiver CSVs from `captures/`. If using Wireshark, save real `.pcapng` files. Stop all sessions at the end.

Use a comparison table in your report:

| Source/FPS/width/quality | Duration | Receivers | Input loss/jitter/buffer | Observed loss/jitter/RTT | Frames/incomplete | Throughput |
|---|---|---|---|---|---|---|
| Fill in your actual settings | Record seconds | Record count | Record inputs | Copy measured values | Copy counters | Copy Mb/s |

## 10. Which code files to study

Study the files in this order. The line-by-line companion explains the application files and the local experiment runner with the actual source lines alongside their meanings.

| Order | File | What to understand |
|---|---|---|
| 1 | [main.py](main.py) | How the program starts and delegates to the command parser. |
| 2 | [lanstream/__main__.py](lanstream/__main__.py) | GUI versus CLI modes, options, construction and shutdown. |
| 3 | [lanstream/media.py](lanstream/media.py) | File decoding, demo generation, resizing and JPEG encoding. |
| 4 | [lanstream/protocol.py](lanstream/protocol.py) | Binary headers, chunk splitting/parsing, and TCP message framing. |
| 5 | [lanstream/network.py](lanstream/network.py) | Socket lifecycle, JOIN/INFO, media scheduling, impairment and receiving. |
| 6 | [lanstream/metrics.py](lanstream/metrics.py) | Loss/jitter/throughput formulas, frame assembly and CSV. |
| 7 | [lanstream/gui.py](lanstream/gui.py) | Buttons, GUI queues, playback, cards and throughput graph. |
| 8 | [experiments/run_local.py](experiments/run_local.py) | Automated comparisons of impairment conditions. |

Other useful files:

- `lanstream/__init__.py`: package description/version.
- `requirements.txt` and `pyproject.toml`: dependencies and package configuration.
- `tests/test_project.py`: executable examples of expected packet handling and streaming behavior.
- `experiments/gui_smoke.py`: opens the GUI, starts/joins a stream, checks rendering, and closes it.
- `experiments/streaming.tcl`: optional NS-2 UDP/CBR model, separate from the app.
- `experiments/analyze_trace.py`: reads the old wired NS-2 trace format; it does not parse Wireshark captures.
- `start.command` and `start.bat`: convenience launchers after setup.
- `docs/ARCHITECTURE.md`, `docs/LAB_GUIDE.md`, `docs/VIVA.md`, `docs/VALIDATION.md`: supplementary design, lab, viva and existing validation notes.
- `cn_synopsis_416_359_181_182.pdf`: original proposal.

If time is limited, prioritize `protocol.py`, `Sender._stream()`, `Receiver.start()`, `Receiver._media()`, `Metrics.packet()`, `Metrics.snapshot()`, `Assembler.add()/ready()` and `App.update_stats()`. These explain the central networking and measurement behavior.

## 11. Important code explained

The complete per-line reference is in [CODE_WALKTHROUGH.md](docs/CODE_WALKTHROUGH.md). These examples connect the most important lines to the concepts above.

### 11.1 Binary packet header: protocol.py

```python
HEADER = struct.Struct('!4sQIIHHd')
```

`struct` converts Python values into fixed-format binary data. `!` means network byte order (big-endian) with standard field sizes and no native alignment padding.

| Format | Field | Bytes | Purpose |
|---|---|---|---|
| `4s` | Magic `LVS1` | 4 | Identify this app's packet format. |
| `Q` | Stream ID | 8 | Distinguish sessions. |
| first `I` | Sequence number | 4 | Identify each source packet and estimate gaps. |
| second `I` | Frame number | 4 | Group chunks into pictures. |
| first `H` | Chunk index | 2 | Put pieces of a frame in order. |
| second `H` | Chunk count | 2 | Know when a frame is complete. |
| `d` | Sender timestamp | 8 | Relate source pacing to receiver arrivals. |

Total: 32 bytes. The media chunk follows this header.

```python
count = (len(data) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
```

This is integer ceiling division. For 5000 bytes and a 1160-byte chunk size it returns 5, ensuring the final partial chunk gets a packet.

```python
data[index * PAYLOAD_SIZE:(index + 1) * PAYLOAD_SIZE]
```

This slice extracts the chunk at `index`. `yield` returns one datagram at a time. Sequence numbers increase for every chunk, while frame number stays the same for all chunks of a picture. `& 0xffffffff` keeps counters within unsigned 32-bit range; these lab metrics assume sessions do not span a wrap.

### 11.2 TCP messages: protocol.py

`Channel.send()` builds a JSON object, encodes it as bytes and appends `b'\n'`. A lock prevents simultaneous writes from interleaving. `sendall()` attempts to send the entire message or raises an error.

`Channel.receive()` accumulates bytes until a newline appears. TCP can split one message across multiple reads or combine several messages into one read. The buffer preserves unread bytes. `json.loads()` decodes one complete message, then the code checks that it is a dictionary with a string `type`.

### 11.3 Socket setup: network.py

```python
socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

Create an IPv4 TCP socket. Sender `bind()` chooses the listening address and port; `listen()` makes it accept connections; `accept()` returns a separate connected socket for each peer.

```python
socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

Create an IPv4 UDP socket. `sendto()` sends a datagram to an IP/port pair. `recvfrom()` returns the datagram plus its source address. Binding a UDP socket to port 0 asks the OS to choose an available port. The receiver shares its assigned port with the sender over TCP.

### 11.4 Media scheduler: network.py

`Sender._stream()` first sends any queued packets whose due times have arrived. It then checks whether a new source frame is due. If there are no receivers, it waits without reading the source.

After reading a JPEG, `packetize()` produces its datagrams. For each datagram and receiver, the code applies loss, assigns a random due time, and inserts it into a heap. The unique `ticket` prevents heap ties from depending on packet bytes or destinations. A bounded queue prevents unlimited growth under excessive load.

`next_frame` advances using `1 / fps`. Waiting is interruptible using `stop_event.wait()`, allowing stop requests to wake loops early. Encoding and scheduling take time, so source FPS remains a target rather than a real-time guarantee.

### 11.5 Receiver pipeline: network.py and metrics.py

The receiver opens its UDP socket before JOIN so it can already accept arriving media. It reads INFO over TCP, validates the codec and session metadata, then starts media and control threads.

`Receiver._media()` accepts media only from the advertised IP/port and stream ID. `unpack()` validates framing. `Metrics.packet()` rejects duplicates/very old packets and updates statistics. `Assembler.add()` stores chunks. `Assembler.ready()` releases complete frames at deadlines and counts expired partial frames. The `on_frame` callback passes reconstructed JPEG bytes to the GUI or CLI.

The GUI's one-frame queue keeps the newest available picture; it does not accumulate an unlimited display backlog.

### 11.6 Why a deque is used for throughput: metrics.py

```python
self.window.append((now, size))
while self.window and self.window[0][0] < now - 1:
    self.window.popleft()
```

Each accepted packet contributes its arrival time and byte length. A deque makes removal from the oldest end efficient. Snapshots discard entries older than one second and sum the remaining sizes. This is a sliding window, explaining why the throughput number changes when packets enter or age out of the window.

### 11.7 Frame reconstruction: metrics.py

```python
b''.join(parts[i] for i in range(count))
```

Once every indexed chunk is present, concatenate their payloads in chunk order to recreate the original JPEG bytes. It is unsafe to concatenate in arrival order because UDP packets can arrive out of order.

### 11.8 GUI updates and the graph: gui.py

`tick()` runs approximately every 40 ms, processes worker messages, and draws the newest received JPEG. `draw_frame()` decodes the bytes with Pillow, resizes to fit the canvas, creates a Tk image and keeps a Python reference so Tk does not lose the image.

`update_stats()` runs approximately every 500 ms, reads a snapshot, updates the cards/counters, appends throughput to the 100-sample history, rescales the graph and draws the green line. It separately reads sender statistics to update the peer list and outgoing counts.

`background()` runs starts/stops/discovery outside the Tk thread. Buttons are temporarily disabled while such an operation is running. `messages` and `frames` bridge workers to the main GUI thread.

## 12. Wireshark demonstration

You can demonstrate application behavior without Wireshark. For packet evidence, open Wireshark and start capturing before joining. Choose **Loopback/lo0** for `127.0.0.1` tests or the actual Wi-Fi/Ethernet interface for separate computers.

Paste these into the display-filter bar:

| Goal | Filter |
|---|---|
| TCP control traffic on the default port | `tcp.port == 5000` |
| LANStream media identified by its magic bytes | `udp.payload[0:4] == 4c:56:53:31` |
| Discovery | `udp.port == 5002` |

Right-click a TCP packet and use **Follow → TCP Stream** to read JOIN, INFO, PING/PONG, STAT and leave/end messages. In a media packet, inspect the raw bytes to find the `LVS1` header. Wireshark does not automatically decode all fields of our custom protocol into named columns.

Use **Statistics → Conversations** to show separate receiver flows. Use **Statistics → I/O Graphs**, filtered to media, to inspect packet/bit rates over time. Wireshark's selected byte-count layer can include headers excluded by the app, so its values need not exactly match the dashboard.

Wireshark does not automatically calculate custom-protocol loss/jitter for us. Compare application sequence gaps and CSV statistics. Artificially dropped packets never leave the sender and therefore do not appear even in a sender-side capture. Capture at the receiver when discussing what actually reached that receiver.

TCP control and UDP media carry different workloads here. Their captures show how the app uses both protocols, but do not establish a controlled TCP-versus-UDP media benchmark. See [LAB_GUIDE.md](docs/LAB_GUIDE.md) for more detail.

## 13. CSV files and command-line experiments

### 13.1 CSV recording

GUI receiver sessions automatically record to `captures/receiver-YYYYMMDD-HHMMSS.csv` relative to the project working directory. Reports are written approximately once per second and once again on stop. Open the CSV in a spreadsheet app or text editor.

| Column | Meaning |
|---|---|
| `elapsed_s` | Elapsed receiver time. |
| `packets`, `bytes` | Accepted unique packet and application-byte totals. |
| `missing`, `loss_pct` | Current sequence-gap count and percentage. |
| `duplicates` | Repeated packet sequence numbers detected within the retained horizon. |
| `frames` | Complete frames released to playback. |
| `dropped_frames` | Partial frames expired/evicted. |
| `late_frames` | First-seen frames rejected by the lateness rule. |
| `jitter_ms`, `rtt_ms` | Estimated transit variation and latest control round-trip measurement. |
| `throughput_mbps` | Application throughput in the most recent one-second window. |
| `average_mbps` | Application bytes over the entire elapsed session, converted to Mb/s. |
| `fps` | Complete frames released divided by elapsed time. |

### 13.2 Automated experiment

With the environment activated, or replacing `python` with the appropriate environment interpreter:

```bash
python -m experiments.run_local --seconds 6 --output captures/experiment.csv
```

This runs six conditions sequentially on loopback: baseline, 2% loss, 5% loss, 80 ms jitter, 160 ms jitter with a short buffer, and 160 ms jitter with a larger buffer. It uses width=320 and FPS=15, which may differ from your GUI settings. `--seconds` applies to each condition, not the whole experiment. A fixed random seed controls the artificial random choices, but OS timing still makes results vary. For a report, prefer longer repeated runs such as 30 seconds per condition.

The CSV endpoint is sampled while each stream is active, so delayed packets may still be in flight. Do not interpret all high-jitter endpoint sequence gaps as permanent losses. The existing [validation record](docs/VALIDATION.md) contains measured examples; treat your own results as observations rather than trying to reproduce the exact numbers.

### 13.3 CLI sender and receiver

```bash
python -m lanstream send
python -m lanstream send --file movie.mp4 --loop
python -m lanstream send --loss 5 --jitter 80 --width 480 --fps 15
python -m lanstream receive 192.168.1.10 --duration 30 --csv captures/run.csv
python -m lanstream receive 127.0.0.1 --duration 5 --save-frames captures/frames
python -m lanstream discover
```

Run the sender and receiver in separate terminals. CLI receivers measure and optionally save individual JPEGs; use the GUI for live viewing. Ctrl+C stops the session. `--duration` can end a run automatically. Discovery prints discovered senders; it does not stream video by itself.

### 13.4 Automated tests

```bash
python -m unittest discover -s tests -v
# Optional: opens a real desktop window and closes it after checking playback.
python -m experiments.gui_smoke
```

Tests use local sockets, so they need permission to bind/connect on loopback. They check framing, reordering, duplicate handling, missing-frame expiry, loss calculations, two receivers, JPEG decoding, CSV output, discovery, impairment handling, zero buffer, invalid joins, shutdown, source EOF, file decoding, and trace parsing. Existing tests passed during the recorded implementation validation; physical LAN/firewall behavior still needs a real two-computer test.

### 13.5 Optional NS-2 files

The main app does not import or need NS-2. If the optional simulator is available:

```bash
ns experiments/streaming.tcl 10ms 0.02 2Mb captures/ns2-loss
python experiments/analyze_trace.py captures/ns2-loss.tr
```

This models UDP/CBR traffic on a small topology, not the actual Python JPEG decoder. It can vary delay, random loss and offered load. NS-2 was not installed during the implementation checks, so no simulator execution is claimed. If your teacher permits omitting this objective, demonstrate the real application impairment tests and Wireshark instead, and update the final synopsis/report accordingly.

## 14. Troubleshooting and limitations

| Symptom | What to check |
|---|---|
| Window does not open | Use the correct environment interpreter; install requirements and Tk support. |
| Address already in use | Another sender owns that TCP port. Stop it or choose a different port at both ends. |
| Connection refused | Start the sender first and confirm its IP/port. |
| Connection times out | Check routing, firewall, Wi-Fi client isolation and the selected adapter/IP. |
| Connected but no video | Check received packet counts, UDP firewall access, loss input and source errors. |
| Frozen image with rising packet counts | Frames may be incomplete or miss deadlines. Reduce jitter/loss or increase buffer, and inspect incomplete-frame counters. |
| Discovery finds nothing | Enter the sender IP/port manually; broadcast filtering may be the cause. |
| Loss shows zero but no packets arrive | No sequence range exists to estimate gaps. Check connectivity and sender simulated drops. |
| High bandwidth or CPU use | Reduce FPS, width, quality or receiver count. |
| File will not open | Try a supported common video format/codec; OpenCV codec availability depends on the build. |
| Graph has earlier-run samples | History persists in the same window. Relaunch the app for a completely fresh chart. |
| Sender's cards remain at zero | Cards describe receiving. Join a stream in that instance to populate them. |

Project scope and limits:

- Video only; no audio or audio/video synchronization.
- No internet peer discovery, NAT traversal or automatic remote access across unrelated networks.
- No authentication or encryption; intended for a trusted lab LAN.
- No automatic retransmission/FEC, bitrate adaptation or congestion control for media.
- Direct unicast copies, so sender bandwidth grows with receiver count.
- Loss estimates have unknown first/last boundaries and can temporarily count reordered packets as missing.
- Whole frames with no packets observed are absent from the incomplete-frame count.
- Throughput counts accepted application packets, not decoded video quality or physical link utilization.
- Packet counters are 32-bit; the measurement logic is intended for lab sessions shorter than a sequence-number wrap.
- Complete-frame counters describe releases to the playback callback, not guaranteed display refreshes.
- A slow GUI can skip stale images while preserving responsiveness.

## 15. Presentation and viva answers

### A short opening explanation

"Our project shares video directly between computers on a LAN. We use TCP for reliable session commands and UDP for numbered JPEG chunks. The receiver puts chunks back in order and waits in a configurable playback buffer. We measure packet loss estimates, arrival jitter, throughput and control round-trip time. Artificial loss and delay let us demonstrate the effect of network conditions on video playback."

### What is the moving circle?

A generated test video. It gives us a reproducible visual source without needing a downloaded video. Its jumps reveal skipped pictures, but it is not itself a packet animation.

### What is the green line?

Receiver application throughput, sampled roughly every half-second and retained for about 50 seconds. It uses a sliding one-second byte count and automatic vertical scaling. It is not a jitter or loss plot.

### Why can video freeze while throughput stays high?

Packets may arrive but not make complete frames before their deadlines. The graph counts valid received bytes; playback needs every chunk of each JPEG in time.

### Why does loss move up and down?

New sequence gaps increase the estimate; late arrivals can fill them. It is cumulative over observed packet numbers. Artificial loss is random, so its configured probability is not an exact delivered percentage.

### Does increasing the buffer solve loss?

It helps packets that are delayed or reordered. It cannot recreate permanently missing chunks. It trades extra waiting time for better tolerance of arrival variation.

### Why TCP control and UDP media?

Control needs ordered reliable commands. Independent video frames can be skipped when incomplete so playback continues with later frames. The project chooses that tradeoff; it does not prove UDP is always faster.

### What would you improve next?

Add audio synchronization, authenticated/encrypted sessions, congestion-aware quality adjustment, better loss recovery, and a controlled comparison using identical media over TCP and UDP.
