# Application code: numbered line-by-line study guide

This companion explains the source as it exists alongside this guide. Start with [the README](../README.md) for concepts, dashboard meanings, formulas and demo steps. No application code was changed to create this document.

Each table quotes every nonblank physical source line and explains its purpose. Indentation is significant in Python; it is preserved in the actual source file. Blank lines are omitted because they perform no operation. Continued statements are identified with their originating line. Colors/layout lines are included so you can follow the entire GUI, but prioritize the networking and measurement methods for your viva.

## Python syntax used throughout

| Syntax | Meaning |
|---|---|
| `self` | The current object instance; each sender/receiver keeps separate state. |
| `def`, `class` | Define a function/method or a class; a definition does not immediately execute its body. |
| `None`, `True`, `False` | No value, true, and false. |
| `[]`, `{}`, `set()` | Lists/indexing/slices, dictionaries, and sets (unique elements). Empty `{}` is a dictionary, not a set. |
| `for`, `while`, `if`, `elif`, `else` | Repetition and conditional branching; indented blocks define scope. |
| `try`, `except`, `finally` | Attempt work, handle selected errors, and run cleanup even on failure. |
| `with lock` | Hold a lock for a block, releasing it when leaving the block. |
| `*args`, `**fields`, `**options` | Collect/unpack positional arguments or named dictionary arguments. |
| `lambda` | A small anonymous function, used here for no-op callback defaults. |
| `yield` | Produce one value from a generator while preserving its iteration state. |
| `f"...{value}..."` | Insert values into a formatted string. |
| `b"..."`, `.encode()` | Raw bytes and converting text into bytes for network/image data. |
| `//`, `%`, `&` | Integer floor division, remainder, and bitwise AND. Here AND masks packet/frame counters to uint32. |

## Reading order

Launcher → entry mode → media → protocol → network → metrics → GUI → local experiments. Follow one frame end to end before memorizing individual variable names.

## main.py

Small launcher. It imports the actual entry function and calls it only when executed as a script.

[Open source](../main.py)

### Function responsibilities

This small module contains only module-level setup/entry statements.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""Convenience launcher: python main.py"""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>from lanstream.__main__ import main</code> | Import main from lanstream.__main__ for project helpers used in this file. |
| 4 | <code>if __name__ == '__main__':</code> | Run the following entry-point call only when this file/module is executed directly, not merely imported. |
| 5 | <code>main()</code> | Call main(); see the function summary above for its role in this stage. |

## lanstream/__init__.py

Marks the package and records its version. It performs no networking.

[Open source](../lanstream/__init__.py)

### Function responsibilities

This small module contains only module-level setup/entry statements.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""LANStream: a Computer Networks project."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>__version__ = "1.0.0"</code> | Set __version__ to '1.0.0'. |

## lanstream/__main__.py

Selects GUI, sending, receiving or discovery from command-line arguments, then controls the session lifetime.

[Open source](../lanstream/__main__.py)

### Function responsibilities

- **`main()`**, line 7: Parse arguments, launch the GUI by default, or run a CLI session and stop it on completion.
- **`main.frame()`**, line 48: Optionally save each reconstructed JPEG with a sequential filename, then advance the CLI frame counter.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>import argparse</code> | Import argparse for command-line options and subcommands. |
| 2 | <code>import json</code> | Import json for TCP/discovery JSON serialization. |
| 3 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 4 | <code>from pathlib import Path</code> | Import Path from pathlib for portable filesystem paths. |
| 7 | <code>def main():</code> | Define main(). Parse arguments, launch the GUI by default, or run a CLI session and stop it on completion. |
| 8 | <code>parser = argparse.ArgumentParser(description='LANStream: peer-to-peer LAN video and network analysis')</code> | Set parser to a command-line argument parser with the shown description. |
| 9 | <code>sub = parser.add_subparsers(dest='command')</code> | Set sub to the result of parser.add_subparsers(dest='command'). |
| 10 | <code>sub.add_parser('gui', help='Launch the desktop dashboard (default)')</code> | Register the named command-line subcommand and its help text. |
| 11 | <code>sub.add_parser('discover', help='Find active LAN senders')</code> | Register the named command-line subcommand and its help text. |
| 12 | <code>send = sub.add_parser('send', help='Stream JPEG video over UDP')</code> | Set send to the result of sub.add_parser('send', help='Stream JPEG video over UDP'). |
| 13 | <code>send.add_argument('--file', help='Video path; omit for an animated demo')</code> | Register --file as an optional flag. Video path; omit for an animated demo |
| 14 | <code>send.add_argument('--bind', default='0.0.0.0')</code> | Register --bind as an optional flag, defaulting to '0.0.0.0'.  |
| 15 | <code>send.add_argument('--port', type=int, default=5000)</code> | Register --port as an optional flag, converted using int, defaulting to 5000.  |
| 16 | <code>send.add_argument('--fps', type=int, default=20)</code> | Register --fps as an optional flag, converted using int, defaulting to 20.  |
| 17 | <code>send.add_argument('--width', type=int, default=640)</code> | Register --width as an optional flag, converted using int, defaulting to 640.  |
| 18 | <code>send.add_argument('--quality', type=int, default=70)</code> | Register --quality as an optional flag, converted using int, defaulting to 70.  |
| 19 | <code>send.add_argument('--loop', action='store_true')</code> | Register --loop as an optional flag, true when present and false otherwise.  |
| 20 | <code>send.add_argument('--loss', type=float, default=0, help='Simulated packet loss percent')</code> | Register --loss as an optional flag, converted using float, defaulting to 0. Simulated packet loss percent |
| 21 | <code>send.add_argument('--jitter', type=float, default=0, help='Maximum random packet delay in ms')</code> | Register --jitter as an optional flag, converted using float, defaulting to 0. Maximum random packet delay in ms |
| 22 | <code>send.add_argument('--duration', type=float, default=0)</code> | Register --duration as an optional flag, converted using float, defaulting to 0.  |
| 23 | <code>receive = sub.add_parser('receive', help='Join a stream; GUI is optional')</code> | Set receive to the result of sub.add_parser('receive', help='Join a stream; GUI is optional'). |
| 24 | <code>receive.add_argument('host')</code> | Register host as a required positional argument.  |
| 25 | <code>receive.add_argument('--port', type=int, default=5000)</code> | Register --port as an optional flag, converted using int, defaulting to 5000.  |
| 26 | <code>receive.add_argument('--buffer', type=int, default=120, help='Playout buffer in ms')</code> | Register --buffer as an optional flag, converted using int, defaulting to 120. Playout buffer in ms |
| 27 | <code>receive.add_argument('--csv', default='captures/receiver.csv')</code> | Register --csv as an optional flag, defaulting to 'captures/receiver.csv'.  |
| 28 | <code>receive.add_argument('--save-frames', help='Optional directory for received JPEG frames')</code> | Register --save-frames as an optional flag. Optional directory for received JPEG frames |
| 29 | <code>receive.add_argument('--duration', type=float, default=0)</code> | Register --duration as an optional flag, converted using float, defaulting to 0.  |
| 30 | <code>args = parser.parse_args()</code> | Set args to the parsed command-line options. |
| 31 | <code>if args.command in (None, 'gui'):</code> | Take this branch only when args.command in (None, 'gui') is true; indentation marks which statements belong to it. |
| 32 | <code>from .gui import launch</code> | Import launch from gui for project helpers used in this file. |
| 33 | <code>launch()</code> | Call launch(); see the function summary above for its role in this stage. |
| 34 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 35 | <code>from .network import Sender, Receiver, discover</code> | Import Sender, Receiver, discover from network for project helpers used in this file. |
| 36 | <code>if args.command == 'discover':</code> | Take this branch only when args.command == 'discover' is true; indentation marks which statements belong to it. |
| 37 | <code>print(json.dumps(discover(), indent=2))</code> | Print the shown status/result to the terminal; flush=True makes it visible immediately. |
| 38 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 39 | <code>session = None</code> | Set session to None. |
| 40 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 41 | <code>if args.command == 'send':</code> | Take this branch only when args.command == 'send' is true; indentation marks which statements belong to it. |
| 42 | <code>from .media import VideoSource</code> | Import VideoSource from media for project helpers used in this file. |
| 43 | <code>source = VideoSource(args.file, args.width, args.fps, args.quality, args.loop)</code> | Set source to a video source configured from the selected options. |
| 44 | <code>session = Sender(source, args.bind, args.port, args.loss, args.jitter, print)</code> | Set session to the result of Sender(source, args.bind, args.port, args.loss, args.jitter, print). |
| 45 | <code>session.start()</code> | Start the configured worker thread or session. |
| 46 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 47 | <code>count = 0</code> | Set count to 0. |
| 48 | <code>def frame(jpeg):</code> | Define main.frame(). Optionally save each reconstructed JPEG with a sequential filename, then advance the CLI frame counter. |
| 49 | <code>nonlocal count</code> | Use count from the enclosing function so the callback can update that shared counter. |
| 50 | <code>if args.save_frames:</code> | Take this branch only when args.save_frames is true; indentation marks which statements belong to it. |
| 51 | <code>directory = Path(args.save_frames)</code> | Set directory to a portable Path object for the given filename. |
| 52 | <code>directory.mkdir(parents=True, exist_ok=True)</code> | Ensure the output directory exists, including parents when requested. |
| 53 | <code>(directory / f'frame-{count:06d}.jpg').write_bytes(jpeg)</code> | Write the encoded JPEG bytes to the chosen output file. |
| 54 | <code>count += 1</code> | Increase count by 1. |
| 55 | <code>session = Receiver(args.host, args.port, args.buffer, frame, print, args.csv)</code> | Set session to the result of Receiver(args.host, args.port, args.buffer, frame, print, args.csv). |
| 56 | <code>session.start()</code> | Start the configured worker thread or session. |
| 57 | <code>started = time.monotonic()</code> | Set started to the current local monotonic time in seconds. |
| 58 | <code>while not session.stop_event.wait(1):</code> | Repeat this block while not session.stop_event.wait(1) remains true. |
| 59 | <code>stats = session.snapshot() if args.command == 'send' else session.metrics.snapshot()</code> | Set stats to session.snapshot() if args.command == 'send' else session.metrics.snapshot(); this holds the current receiver report dictionary. |
| 60 | <code>print(json.dumps(stats), flush=True)</code> | Print the shown status/result to the terminal; flush=True makes it visible immediately. |
| 61 | <code>if args.duration &gt; 0 and time.monotonic() - started &gt;= args.duration:</code> | Take this branch only when args.duration &gt; 0 and time.monotonic() - started &gt;= args.duration is true; indentation marks which statements belong to it. |
| 62 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 63 | <code>except KeyboardInterrupt:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 64 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 65 | <code>except (OSError, ValueError, ImportError) as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 66 | <code>parser.exit(1, f'LANStream: {exc}\n')</code> | Call parser.exit(1, f'LANStream: {exc}\n'); see the function summary above for its role in this stage. |
| 67 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 68 | <code>if session:</code> | Take this branch only when session is true; indentation marks which statements belong to it. |
| 69 | <code>session.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 72 | <code>if __name__ == '__main__':</code> | Run the following entry-point call only when this file/module is executed directly, not merely imported. |
| 73 | <code>main()</code> | Call main(); see the function summary above for its role in this stage. |

## lanstream/media.py

Produces one independent JPEG at a time from a file or a generated moving test picture.

[Open source](../lanstream/media.py)

### Function responsibilities

- **`VideoSource.__init__()`**, line 8: Validate media settings, store source options, and open a video file if provided.
- **`VideoSource.read()`**, line 23: Produce the next JPEG bytes, or return None at non-looping file EOF.
- **`VideoSource.close()`**, line 58: Release an opened OpenCV file reader.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""JPEG video frames. Each frame is independently decodable after packet loss."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>import io</code> | Import io for in-memory image byte buffers. |
| 3 | <code>import math</code> | Import math for demo motion or finite-timestamp validation. |
| 4 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 7 | <code>class VideoSource:</code> | Define the VideoSource class, which groups its state and related methods. |
| 8 | <code>def __init__(self, path=None, width=640, fps=20, quality=70, loop=False):</code> | Define VideoSource.__init__(). Validate media settings, store source options, and open a video file if provided. |
| 9 | <code>if not 160 &lt;= width &lt;= 1920 or not 1 &lt;= fps &lt;= 60 or not 10 &lt;= quality &lt;= 95:</code> | Take this branch only when not 160 &lt;= width &lt;= 1920 or not 1 &lt;= fps &lt;= 60 or (not 10 &lt;= quality &lt;= 95) is true; indentation marks which statements belong to it. |
| 10 | <code>raise ValueError('Width 160–1920, FPS 1–60, JPEG quality 10–95 required')</code> | Raise ValueError('Width 160–1920, FPS 1–60, JPEG quality 10–95 required') to report failure to the caller. |
| 11 | <code>self.path, self.width, self.fps, self.quality, self.loop = path, width, fps, quality, loop</code> | Set (self.path, self.width, self.fps, self.quality, self.loop) to the values path, width, fps, quality, loop. |
| 12 | <code>self.name = 'Animated demo' if not path else __import__('pathlib').Path(path).name</code> | Set self.name to 'Animated demo' if not path else __import__('pathlib').Path(path).name. |
| 13 | <code>self.capture = None</code> | Set self.capture to None; this holds the OpenCV file reader (None selects the generated demo). |
| 14 | <code>if path:</code> | Take this branch only when path is true; indentation marks which statements belong to it. |
| 15 | <code>import cv2</code> | Import cv2 for OpenCV video file decoding. |
| 16 | <code>self.capture = cv2.VideoCapture(str(path))</code> | Set self.capture to the result of cv2.VideoCapture(str(path)); this holds the OpenCV file reader (None selects the generated demo). |
| 17 | <code>if not self.capture.isOpened():</code> | Take this branch only when not self.capture.isOpened() is true; indentation marks which statements belong to it. |
| 18 | <code>self.capture.release()</code> | Release the OpenCV media reader and its file/codec resources. |
| 19 | <code>raise ValueError('Cannot open video. Choose a supported MP4, AVI, MOV or MKV file.')</code> | Raise ValueError('Cannot open video. Choose a supported MP4, AVI, MOV or MKV file.') to report failure to the caller. |
| 20 | <code>self.native_fps = self.capture.get(cv2.CAP_PROP_FPS) or fps</code> | Read the file metadata FPS with fallback; this stored attribute is not used to pace the stream. |
| 21 | <code>self.index = 0</code> | Set self.index to 0; this holds the source frame counter used for file sampling and demo time. |
| 23 | <code>def read(self):</code> | Define VideoSource.read(). Produce the next JPEG bytes, or return None at non-looping file EOF. |
| 24 | <code>from PIL import Image, ImageDraw</code> | Import Image, ImageDraw from PIL for Pillow image drawing, encoding and display. |
| 25 | <code>if self.capture is not None:</code> | Take this branch only when self.capture is not None is true; indentation marks which statements belong to it. |
| 26 | <code>import cv2</code> | Import cv2 for OpenCV video file decoding. |
| 27 | <code># Sample by presentation time to preserve file playback speed at target FPS.</code> | Comment: Sample by presentation time to preserve file playback speed at target FPS. Comments explain intent and do not execute. |
| 28 | <code>self.capture.set(cv2.CAP_PROP_POS_MSEC, self.index * 1000 / self.fps)</code> | Sample the file at source media time corresponding to the target output FPS. |
| 29 | <code>ok, array = self.capture.read()</code> | Set (ok, array) to the result of self.capture.read(). |
| 30 | <code>if not ok and self.loop:</code> | If the file ended or a read failed and looping is enabled, seek back to its start and try again. |
| 31 | <code>self.index = 0</code> | Set self.index to 0; this holds the source frame counter used for file sampling and demo time. |
| 32 | <code>self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)</code> | Seek the OpenCV video reader back to its first frame for looping. |
| 33 | <code>ok, array = self.capture.read()</code> | Set (ok, array) to the result of self.capture.read(). |
| 34 | <code>if not ok:</code> | Take this branch only when not ok is true; indentation marks which statements belong to it. |
| 35 | <code>return None</code> | Return None to the caller and leave this function. |
| 36 | <code>image = Image.fromarray(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))</code> | Convert OpenCV BGR channel order to RGB and wrap the frame as a Pillow image. |
| 37 | <code>height = max(2, round(image.height * self.width / image.width))</code> | Choose a positive resized height that preserves the original file aspect ratio. |
| 38 | <code>image = image.resize((self.width, height))</code> | Set image to the result of image.resize((self.width, height)). |
| 39 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 40 | <code>w, h = self.width, round(self.width * 9 / 16)</code> | Set (w, h) to the values self.width, round(self.width * 9 / 16). |
| 41 | <code>image = Image.new('RGB', (w, h), '#101e31')</code> | Set image to a new blank RGB image for this synthetic video frame. |
| 42 | <code>draw = ImageDraw.Draw(image)</code> | Set draw to a drawing context attached to the generated image. |
| 43 | <code>for x in range(0, w, 40):</code> | Loop over range(0, w, 40), assigning each item to x. |
| 44 | <code>draw.line((x, 0, x, h), fill='#1c3048')</code> | Draw one static grid line into the generated demo picture. |
| 45 | <code>for y in range(0, h, 40):</code> | Loop over range(0, h, 40), assigning each item to y. |
| 46 | <code>draw.line((0, y, w, y), fill='#1c3048')</code> | Draw one static grid line into the generated demo picture. |
| 47 | <code>phase = self.index / self.fps</code> | Convert the source frame index into synthetic media time in seconds. |
| 48 | <code>cx = int(w / 2 + math.sin(phase * 1.4) * w * .32)</code> | Compute horizontal circle center using sine motion around the image midpoint. |
| 49 | <code>cy = int(h / 2 + math.cos(phase * 1.9) * h * .24)</code> | Compute vertical circle center with a different-frequency cosine for a moving curved path. |
| 50 | <code>draw.ellipse((cx-24, cy-24, cx+24, cy+24), fill='#31dfb6')</code> | Draw the 48-pixel-wide green test circle into this generated picture; it is not a packet symbol. |
| 51 | <code>draw.text((20, 20), 'LANSTREAM / LIVE NETWORK DEMO', fill='white')</code> | Draw the shown title or source frame/time/FPS text into this picture before transmission. |
| 52 | <code>draw.text((20, h-40), f'Frame {self.index:06d}   &#124;   {phase:07.2f}s   &#124;   {self.fps} FPS', fill='#90b4d6')</code> | Draw the shown title or source frame/time/FPS text into this picture before transmission. |
| 53 | <code>self.index += 1</code> | Increase self.index by 1. |
| 54 | <code>output = io.BytesIO()</code> | Set output to an in-memory byte buffer. |
| 55 | <code>image.save(output, format='JPEG', quality=self.quality)</code> | Compress the current full picture independently as JPEG into the in-memory byte buffer. |
| 56 | <code>return output.getvalue()</code> | Return encoded JPEG bytes for packetization, not a filename. |
| 58 | <code>def close(self):</code> | Define VideoSource.close(). Release an opened OpenCV file reader. |
| 59 | <code>if self.capture:</code> | Take this branch only when self.capture is true; indentation marks which statements belong to it. |
| 60 | <code>self.capture.release()</code> | Release the OpenCV media reader and its file/codec resources. |

## lanstream/protocol.py

Defines the on-wire binary media format and newline-delimited JSON control format.

[Open source](../lanstream/protocol.py)

### Function responsibilities

- **`packetize()`**, line 26: Split one JPEG into bounded payload chunks and yield a header plus payload for each.
- **`unpack()`**, line 35: Validate one media datagram and turn its header/payload into a Packet object.
- **`Channel.__init__()`**, line 48: Keep the connected TCP socket, unread-byte buffer and write lock.
- **`Channel.send()`**, line 53: Serialize one typed JSON message, append a newline, enforce the size bound and send under a lock.
- **`Channel.receive()`**, line 60: Read until a complete newline-delimited JSON message exists, preserving unused bytes.
- **`Channel.close()`**, line 75: Attempt a bidirectional socket shutdown, then release the socket.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""Bounded binary media framing and newline-delimited JSON control messages."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>import json</code> | Import json for TCP/discovery JSON serialization. |
| 3 | <code>import socket</code> | Import socket for TCP/UDP network endpoints and socket constants. |
| 4 | <code>import struct</code> | Import struct for the helpers used below. |
| 5 | <code>import threading</code> | Import threading for background workers, events and locks. |
| 6 | <code>from dataclasses import dataclass</code> | Import dataclass from dataclasses for the immutable decoded Packet record. |
| 8 | <code>MAGIC = b'LVS1'</code> | Four ASCII magic bytes identify a LANStream version-1 media packet. |
| 9 | <code>HEADER = struct.Struct('!4sQIIHHd')</code> | Define a 32-byte big-endian header: magic, uint64 session, uint32 packet/frame, uint16 index/count, float64 timestamp. |
| 10 | <code>PAYLOAD_SIZE = 1160  # 1192-byte UDP payload; below a typical 1500-byte MTU.</code> | Limit the JPEG bytes in each datagram to 1160; adding the 32-byte header gives 1192 application bytes. |
| 11 | <code>MAX_FRAME_BYTES = 2_000_000</code> | Reject JPEGs above 2 MB to bound per-frame input size. |
| 12 | <code>MAX_CHUNKS = (MAX_FRAME_BYTES + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE</code> | Ceiling-divide the maximum frame size by chunk size to bound valid chunk counts. |
| 13 | <code>MAX_CONTROL = 16384</code> | Set a 16 KiB control-message/input-buffer bound. |
| 15 | <code>@dataclass(frozen=True)</code> | Generate standard record methods for Packet; frozen=True prevents modifying its fields after construction. |
| 16 | <code>class Packet:</code> | Define the Packet class, which groups its state and related methods. |
| 17 | <code>stream: int</code> | Declare the stream field with type int; Packet stores it in each immutable decoded record. |
| 18 | <code>sequence: int</code> | Declare the sequence field with type int; Packet stores it in each immutable decoded record. |
| 19 | <code>frame: int</code> | Declare the frame field with type int; Packet stores it in each immutable decoded record. |
| 20 | <code>index: int</code> | Declare the index field with type int; Packet stores it in each immutable decoded record. |
| 21 | <code>count: int</code> | Declare the count field with type int; Packet stores it in each immutable decoded record. |
| 22 | <code>timestamp: float</code> | Declare the timestamp field with type float; Packet stores it in each immutable decoded record. |
| 23 | <code>payload: bytes</code> | Declare the payload field with type bytes; Packet stores it in each immutable decoded record. |
| 26 | <code>def packetize(data, stream, frame, sequence, timestamp):</code> | Define packetize(). Split one JPEG into bounded payload chunks and yield a header plus payload for each. |
| 27 | <code>if not data or len(data) &gt; MAX_FRAME_BYTES:</code> | Take this branch only when not data or len(data) &gt; MAX_FRAME_BYTES is true; indentation marks which statements belong to it. |
| 28 | <code>raise ValueError('Encoded frame must contain 1–2,000,000 bytes')</code> | Raise ValueError('Encoded frame must contain 1–2,000,000 bytes') to report failure to the caller. |
| 29 | <code>count = (len(data) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE</code> | Ceiling division calculates the number of chunks, including a final partial chunk. |
| 30 | <code>for index in range(count):</code> | Visit chunk indexes 0 through count−1 for this JPEG. |
| 31 | <code>yield HEADER.pack(MAGIC, stream, (sequence + index) &amp; 0xffffffff,</code> | Yield one datagram: pack the source/session/chunk fields, then append this indexed slice of JPEG bytes. |
| 32 | <code>frame &amp; 0xffffffff, index, count, timestamp) + data[index * PAYLOAD_SIZE:(index + 1) * PAYLOAD_SIZE]</code> | Continue the statement beginning on line 31. Yield the next packed media datagram, suspending this generator until the next iteration. |
| 35 | <code>def unpack(data):</code> | Define unpack(). Validate one media datagram and turn its header/payload into a Packet object. |
| 36 | <code>if len(data) &lt;= HEADER.size or len(data) &gt; HEADER.size + PAYLOAD_SIZE:</code> | Take this branch only when len(data) &lt;= HEADER.size or len(data) &gt; HEADER.size + PAYLOAD_SIZE is true; indentation marks which statements belong to it. |
| 37 | <code>raise ValueError('Invalid datagram size')</code> | Raise ValueError('Invalid datagram size') to report failure to the caller. |
| 38 | <code>magic, stream, seq, frame, index, count, timestamp = HEADER.unpack_from(data)</code> | Decode the fixed binary header fields from the start of the datagram. |
| 39 | <code>if magic != MAGIC or not 0 &lt; count &lt;= MAX_CHUNKS or index &gt;= count:</code> | Reject another packet format, an invalid chunk count, or an out-of-range chunk index. |
| 40 | <code>raise ValueError('Invalid media header')</code> | Raise ValueError('Invalid media header') to report failure to the caller. |
| 41 | <code>import math</code> | Import math for demo motion or finite-timestamp validation. |
| 42 | <code>if not math.isfinite(timestamp):</code> | Reject NaN/infinite timestamps, which would break deadline and jitter calculations. |
| 43 | <code>raise ValueError('Invalid timestamp')</code> | Raise ValueError('Invalid timestamp') to report failure to the caller. |
| 44 | <code>return Packet(stream, seq, frame, index, count, timestamp, data[HEADER.size:])</code> | Return decoded header values plus the remaining bytes as the JPEG chunk. |
| 47 | <code>class Channel:</code> | Define the Channel class, which groups its state and related methods. |
| 48 | <code>def __init__(self, sock):</code> | Define Channel.__init__(). Keep the connected TCP socket, unread-byte buffer and write lock. |
| 49 | <code>self.sock = sock</code> | Set self.sock to sock. |
| 50 | <code>self.buffer = bytearray()</code> | Set self.buffer to a mutable byte buffer from no initial data. |
| 51 | <code>self.lock = threading.Lock()</code> | Set self.lock to a new mutual-exclusion lock; this holds the lock protecting shared peers or metric counters. |
| 53 | <code>def send(self, kind, **fields):</code> | Define Channel.send(). Serialize one typed JSON message, append a newline, enforce the size bound and send under a lock. |
| 54 | <code>message = json.dumps(dict(type=kind, **fields), separators=(',', ':'), allow_nan=False).encode() + b'\n'</code> | Build a typed JSON object, serialize/encode it, and terminate it with a newline; disallow NaN/Infinity JSON values. |
| 55 | <code>if len(message) &gt; MAX_CONTROL:</code> | Take this branch only when len(message) &gt; MAX_CONTROL is true; indentation marks which statements belong to it. |
| 56 | <code>raise ValueError('Control message too large')</code> | Raise ValueError('Control message too large') to report failure to the caller. |
| 57 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 58 | <code>self.sock.sendall(message)</code> | Send the whole encoded control message or raise a connection error. |
| 60 | <code>def receive(self):</code> | Define Channel.receive(). Read until a complete newline-delimited JSON message exists, preserving unused bytes. |
| 61 | <code>while b'\n' not in self.buffer:</code> | Keep reading until one entire newline-terminated control message is buffered; TCP does not preserve message boundaries. |
| 62 | <code>chunk = self.sock.recv(4096)</code> | Set chunk to the result of self.sock.recv(4096). |
| 63 | <code>if not chunk:</code> | A zero-length TCP read indicates orderly remote closure, not simply "no data yet". |
| 64 | <code>raise EOFError('Control connection closed')</code> | Raise EOFError('Control connection closed') to report failure to the caller. |
| 65 | <code>self.buffer.extend(chunk)</code> | Append all supplied bytes/values to this mutable collection. |
| 66 | <code>if len(self.buffer) &gt; MAX_CONTROL:</code> | Take this branch only when len(self.buffer) &gt; MAX_CONTROL is true; indentation marks which statements belong to it. |
| 67 | <code>raise ValueError('Control message too large')</code> | Raise ValueError('Control message too large') to report failure to the caller. |
| 68 | <code>line, _, rest = self.buffer.partition(b'\n')</code> | Split at the first newline: one complete JSON message, the delimiter, and bytes reserved for later messages. |
| 69 | <code>self.buffer = bytearray(rest)</code> | Retain bytes after the first message; a TCP read may have contained more than one message. |
| 70 | <code>message = json.loads(line)</code> | Set message to the result of json.loads(line). |
| 71 | <code>if not isinstance(message, dict) or not isinstance(message.get('type'), str):</code> | Take this branch only when not isinstance(message, dict) or not isinstance(message.get('type'), str) is true; indentation marks which statements belong to it. |
| 72 | <code>raise ValueError('Invalid control message')</code> | Raise ValueError('Invalid control message') to report failure to the caller. |
| 73 | <code>return message</code> | Return message to the caller and leave this function. |
| 75 | <code>def close(self):</code> | Define Channel.close(). Attempt a bidirectional socket shutdown, then release the socket. |
| 76 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 77 | <code>self.sock.shutdown(socket.SHUT_RDWR)</code> | Disable both send and receive directions of the connected socket before closing it. |
| 78 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 79 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 80 | <code>self.sock.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |

## lanstream/network.py

Implements discovery, sender connections, timed UDP delivery, receivers, heartbeats and cleanup.

[Open source](../lanstream/network.py)

### Function responsibilities

- **`local_ip()`**, line 16: Ask the OS which local address a route would use, with loopback as fallback.
- **`discover()`**, line 28: Broadcast a discovery request, collect bounded responses and return unique sender addresses.
- **`Sender.__init__()`**, line 52: Validate impairment settings and initialize sender sockets, peer state and counters.
- **`Sender._thread()`**, line 68: Start and retain a background worker so shutdown can later join it.
- **`Sender.start()`**, line 73: Bind the TCP and UDP sockets and launch accept, media and discovery workers.
- **`Sender._accept()`**, line 93: Accept TCP peers, cap simultaneous connections at 32 and give each a session worker.
- **`Sender._session()`**, line 110: Validate JOIN, advertise metadata, handle heartbeat/statistics messages and remove departing peers.
- **`Sender._discover()`**, line 160: Reply to the app discovery request with source name and TCP port.
- **`Sender._stream()`**, line 181: Pace JPEG frames, apply artificial loss/delay per receiver, and send queued UDP copies when due.
- **`Sender.snapshot()`**, line 240: Copy peer reports and expose sender totals for the dashboard or CLI.
- **`Sender.stop()`**, line 246: Signal stop, notify/close control connections, close sockets and wait briefly for workers.
- **`Receiver.__init__()`**, line 268: Prepare receiver callbacks, metrics, frame assembler and shutdown state.
- **`Receiver.start()`**, line 282: Bind UDP before JOIN, negotiate metadata over TCP and start media/control workers.
- **`Receiver._media()`**, line 310: Validate arriving datagrams, update metrics, assemble/release JPEGs and drain at session end.
- **`Receiver._control()`**, line 336: Send PING/STAT about once per second, record CSV snapshots and measure matching PONG RTT.
- **`Receiver.stop()`**, line 371: Signal stop, send LEAVE where possible, close sockets, join workers and finalize the CSV.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""TCP signalling, UDP media, LAN discovery, and network impairment."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>import heapq</code> | Import heapq for earliest-due outgoing packet scheduling. |
| 3 | <code>import json</code> | Import json for TCP/discovery JSON serialization. |
| 4 | <code>import random</code> | Import random for artificial packet drop and delay choices. |
| 5 | <code>import secrets</code> | Import secrets for random session identifiers. |
| 6 | <code>import socket</code> | Import socket for TCP/UDP network endpoints and socket constants. |
| 7 | <code>import threading</code> | Import threading for background workers, events and locks. |
| 8 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 9 | <code>from .protocol import Channel, packetize, unpack, HEADER, PAYLOAD_SIZE</code> | Import Channel, packetize, unpack, HEADER, PAYLOAD_SIZE from protocol for project helpers used in this file. |
| 10 | <code>from .metrics import Metrics, Assembler, CSVRecorder</code> | Import Metrics, Assembler, CSVRecorder from metrics for project helpers used in this file. |
| 12 | <code>DISCOVERY_PORT = 5002</code> | Reserve UDP port 5002 for the small discovery protocol. |
| 13 | <code>DISCOVERY_MAGIC = b'LANSTREAM_DISCOVER_V1'</code> | Recognize this exact discovery request before replying. |
| 16 | <code>def local_ip():</code> | Define local_ip(). Ask the OS which local address a route would use, with loopback as fallback. |
| 17 | <code>sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)</code> | Set sock to a new UDP IPv4 socket. |
| 18 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 19 | <code># UDP connect selects a route; it does not send traffic to this address.</code> | Comment: UDP connect selects a route; it does not send traffic to this address. Comments explain intent and do not execute. |
| 20 | <code>sock.connect(('192.0.2.1', 9))</code> | Select a local route using a reserved documentation address; UDP connect here does not transmit a packet. |
| 21 | <code>return sock.getsockname()[0]</code> | Read the local IP selected by the OS routing lookup. |
| 22 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 23 | <code>return '127.0.0.1'</code> | Return '127.0.0.1' to the caller and leave this function. |
| 24 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 25 | <code>sock.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 28 | <code>def discover(timeout=1.2):</code> | Define discover(). Broadcast a discovery request, collect bounded responses and return unique sender addresses. |
| 29 | <code>results = {}</code> | Set results to an empty dictionary. |
| 30 | <code>with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:</code> | Enter socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as a managed resource, automatically exiting/closing it after this block. |
| 31 | <code>sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)</code> | Set the socket option shown: reuse permits address rebinding; broadcast enables discovery; receive buffer requests OS queue capacity. |
| 32 | <code>sock.settimeout(.2)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 33 | <code>for host in ('255.255.255.255', '127.0.0.1'):</code> | Try LAN broadcast as well as loopback so discovery can work in both demonstrations. |
| 34 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 35 | <code>sock.sendto(DISCOVERY_MAGIC, (host, DISCOVERY_PORT))</code> | Send the given UDP bytes to the specified destination IP/port. |
| 36 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 37 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 38 | <code>end = time.monotonic() + timeout</code> | Set end to time.monotonic() + timeout. |
| 39 | <code>while time.monotonic() &lt; end:</code> | Repeat this block while time.monotonic() &lt; end remains true. |
| 40 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 41 | <code>data, addr = sock.recvfrom(4096)</code> | Set (data, addr) to one UDP datagram and its source IP/port. |
| 42 | <code>info = json.loads(data)</code> | Set info to the result of json.loads(data). |
| 43 | <code>if info.get('app') == 'LANStream' and 1 &lt;= int(info['port']) &lt;= 65535:</code> | Take this branch only when info.get('app') == 'LANStream' and 1 &lt;= int(info['port']) &lt;= 65535 is true; indentation marks which statements belong to it. |
| 44 | <code>info['host'] = addr[0]</code> | Use the response packet source IP, rather than trusting an advertised destination address. |
| 45 | <code>results[(addr[0], int(info['port']))] = info</code> | Deduplicate responses by sender IP and TCP port. |
| 46 | <code>except (socket.timeout, ValueError, KeyError, TypeError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 47 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 48 | <code>return list(results.values())</code> | Return the result of list(results.values()) to the caller and leave this function. |
| 51 | <code>class Sender:</code> | Define the Sender class, which groups its state and related methods. |
| 52 | <code>def __init__(self, source, host='0.0.0.0', port=5000, loss=0, jitter_ms=0, on_event=None):</code> | Define Sender.__init__(). Validate impairment settings and initialize sender sockets, peer state and counters. |
| 53 | <code>if not 0 &lt;= loss &lt;= 100 or not 0 &lt;= jitter_ms &lt;= 2000:</code> | Take this branch only when not 0 &lt;= loss &lt;= 100 or not 0 &lt;= jitter_ms &lt;= 2000 is true; indentation marks which statements belong to it. |
| 54 | <code>raise ValueError('Loss must be 0–100%; jitter 0–2000 ms')</code> | Raise ValueError('Loss must be 0–100%; jitter 0–2000 ms') to report failure to the caller. |
| 55 | <code>self.source, self.host, self.port = source, host, port</code> | Set (self.source, self.host, self.port) to the values source, host, port. |
| 56 | <code>self.loss, self.jitter = loss, jitter_ms / 1000</code> | Store loss as a percentage and convert the configured maximum artificial delay from milliseconds to seconds. |
| 57 | <code>self.on_event = on_event or (lambda message: None)</code> | Set self.on_event to on_event or (lambda message: None); this holds the status callback, with a no-op fallback. |
| 58 | <code>self.stop_event = threading.Event()</code> | Set self.stop_event to a new interruptible stop event, initially unset; this holds the shared stop signal, allowing background waits/loops to end. |
| 59 | <code>self.lock = threading.Lock()</code> | Set self.lock to a new mutual-exclusion lock; this holds the lock protecting shared peers or metric counters. |
| 60 | <code>self.clients = {}</code> | Set self.clients to an empty dictionary; this holds the mapping from joined control channels to media addresses and latest reports. |
| 61 | <code>self.connections = set()</code> | Set self.connections to an empty set; this holds the set of all accepted control channels, including ones still joining. |
| 62 | <code>self.threads = []</code> | Set self.threads to an empty list; this holds the list of worker threads to join during cleanup. |
| 63 | <code>self.stream = secrets.randbits(64)</code> | Generate a random 64-bit session ID so the receiver can reject packets from another session. |
| 64 | <code>self.sent_packets = self.sent_bytes = self.simulated_drops = 0</code> | Initialize successful transmission totals and intentional-drop count; totals include copies to every receiver. |
| 65 | <code>self.started = time.monotonic()</code> | Record the local elapsed-time origin; this is not a wall-clock date. |
| 66 | <code>self.listener = self.udp = self.discovery = None</code> | Set self.listener, self.udp, self.discovery to None. |
| 68 | <code>def _thread(self, target, *args):</code> | Define Sender._thread(). Start and retain a background worker so shutdown can later join it. |
| 69 | <code>thread = threading.Thread(target=target, args=args, daemon=True)</code> | Set thread to a worker thread configured with the shown target and arguments. |
| 70 | <code>self.threads.append(thread)</code> | Append the shown new entry to this list/deque for later processing or reporting. |
| 71 | <code>thread.start()</code> | Start the configured worker thread or session. |
| 73 | <code>def start(self):</code> | Define Sender.start(). Bind the TCP and UDP sockets and launch accept, media and discovery workers. |
| 74 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 75 | <code>self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)</code> | Set self.listener to a new TCP IPv4 socket. |
| 76 | <code>self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)</code> | Set the socket option shown: reuse permits address rebinding; broadcast enables discovery; receive buffer requests OS queue capacity. |
| 77 | <code>self.listener.bind((self.host, self.port))</code> | Bind this network socket to the shown local IP/port tuple; an empty host listens on local interfaces and port 0 requests an OS-assigned port. |
| 78 | <code>self.port = self.listener.getsockname()[1]</code> | Set self.port to self.listener.getsockname()[1]. |
| 79 | <code>self.listener.listen(16)</code> | Enable TCP acceptance with a requested pending-connection backlog of 16; the separate registered-connection cap is 32. |
| 80 | <code>self.listener.settimeout(.3)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 81 | <code>self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)</code> | Set self.udp to a new UDP IPv4 socket. |
| 82 | <code>self.udp.bind((self.host, 0))</code> | Bind the source UDP socket to the selected interface(s) and an OS-assigned available port. |
| 83 | <code>self.udp_port = self.udp.getsockname()[1]</code> | Remember the actual source UDP port for the INFO handshake and receiver validation. |
| 84 | <code>self._thread(self._accept)</code> | Start the named sender background worker using the helper. |
| 85 | <code>self._thread(self._stream)</code> | Start the named sender background worker using the helper. |
| 86 | <code>self._thread(self._discover)</code> | Start the named sender background worker using the helper. |
| 87 | <code>self.on_event(f'Sender listening on TCP {self.port}; media UDP {self.udp_port}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 88 | <code>except Exception:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 89 | <code>self.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 90 | <code>raise</code> | Raise the current exception again to report failure to the caller. |
| 91 | <code>return self</code> | Return self to the caller and leave this function. |
| 93 | <code>def _accept(self):</code> | Define Sender._accept(). Accept TCP peers, cap simultaneous connections at 32 and give each a session worker. |
| 94 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 95 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 96 | <code>sock, address = self.listener.accept()</code> | Set (sock, address) to a newly accepted peer TCP socket and its remote address. |
| 97 | <code>sock.settimeout(5)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 98 | <code>channel = Channel(sock)</code> | Set channel to a newline-delimited JSON channel around the connected TCP socket. |
| 99 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 100 | <code>if len(self.connections) &gt;= 32:</code> | Refuse excess control connections to cap per-connection worker resources. |
| 101 | <code>channel.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 102 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 103 | <code>self.connections.add(channel)</code> | Add the shown channel, sequence number or frame ID to this tracking set. |
| 104 | <code>self._thread(self._session, channel, address)</code> | Start the named sender background worker using the helper. |
| 105 | <code>except socket.timeout:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 106 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 107 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 108 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 110 | <code>def _session(self, channel, address):</code> | Define Sender._session(). Validate JOIN, advertise metadata, handle heartbeat/statistics messages and remove departing peers. |
| 111 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 112 | <code>message = channel.receive()</code> | Set message to the next complete decoded TCP control message. |
| 113 | <code>port = message.get('udp_port')</code> | Read the media receive port advertised in JOIN. |
| 114 | <code>if message['type'] != 'JOIN' or not isinstance(port, int) or not 1 &lt;= port &lt;= 65535:</code> | Take this branch only when message['type'] != 'JOIN' or not isinstance(port, int) or (not 1 &lt;= port &lt;= 65535) is true; indentation marks which statements belong to it. |
| 115 | <code>channel.send('ERROR', message='JOIN requires a valid udp_port')</code> | Send the shown typed JSON control message and named fields on TCP. |
| 116 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 117 | <code>channel.send('INFO', stream=self.stream, udp_port=self.udp_port,</code> | Send the shown typed JSON control message and named fields on TCP. |
| 118 | <code>name=self.source.name, fps=self.source.fps, width=self.source.width,</code> | Continue the statement beginning on line 117. Send the shown typed JSON control message and named fields on TCP. |
| 119 | <code>codec='JPEG', version=1)</code> | Continue the statement beginning on line 117. Send the shown typed JSON control message and named fields on TCP. |
| 120 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 121 | <code>self.clients[channel] = dict(address=(address[0], port), stats={}, last=time.monotonic())</code> | Register a destination using the TCP peer IP, its claimed UDP port, empty report and last-contact time. |
| 122 | <code>self.on_event(f'Peer joined: {address[0]}:{port}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 123 | <code>channel.sock.settimeout(.4)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 124 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 125 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 126 | <code>message = channel.receive()</code> | Set message to the next complete decoded TCP control message. |
| 127 | <code>except socket.timeout:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 128 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 129 | <code>client = self.clients.get(channel)</code> | Set client to the requested dictionary/GUI value, with any fallback shown. |
| 130 | <code>last = client['last'] if client else 0</code> | Set last to client['last'] if client else 0. |
| 131 | <code>if time.monotonic() - last &gt; 10:</code> | Remove a peer that has sent no control messages for over ten seconds. |
| 132 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 133 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 134 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 135 | <code>if channel in self.clients:</code> | Take this branch only when channel in self.clients is true; indentation marks which statements belong to it. |
| 136 | <code>self.clients[channel]['last'] = time.monotonic()</code> | Set self.clients[channel]['last'] to the current local monotonic time in seconds. |
| 137 | <code>kind = message['type']</code> | Set kind to message['type']. |
| 138 | <code>if kind == 'PING':</code> | Take this branch only when kind == 'PING' is true; indentation marks which statements belong to it. |
| 139 | <code>channel.send('PONG', nonce=message.get('nonce'))</code> | Echo the receiver timestamp token so that receiver can measure a round trip with its own clock. |
| 140 | <code>elif kind == 'STAT':</code> | If earlier branches did not match, test kind == 'STAT' and run this branch when true. |
| 141 | <code>stats = message.get('stats', {})</code> | Set stats to the requested dictionary/GUI value, with any fallback shown; this holds the current receiver report dictionary. |
| 142 | <code>if isinstance(stats, dict):</code> | Take this branch only when isinstance(stats, dict) is true; indentation marks which statements belong to it. |
| 143 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 144 | <code>if channel in self.clients:</code> | Take this branch only when channel in self.clients is true; indentation marks which statements belong to it. |
| 145 | <code>self.clients[channel]['stats'] = stats</code> | Set self.clients[channel]['stats'] to stats. |
| 146 | <code>elif kind == 'INFO':</code> | If earlier branches did not match, test kind == 'INFO' and run this branch when true. |
| 147 | <code>channel.send('INFO', stream=self.stream, fps=self.source.fps, name=self.source.name)</code> | Send the shown typed JSON control message and named fields on TCP. |
| 148 | <code>elif kind == 'LEAVE':</code> | If earlier branches did not match, test kind == 'LEAVE' and run this branch when true. |
| 149 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 150 | <code>except (OSError, EOFError, ValueError, TypeError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 151 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 152 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 153 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 154 | <code>was_joined = self.clients.pop(channel, None)</code> | Remove the departing peer and remember whether it had completed JOIN. |
| 155 | <code>self.connections.discard(channel)</code> | Remove the shown tracking entry if present, without failing if it was already absent. |
| 156 | <code>channel.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 157 | <code>if was_joined:</code> | Take this branch only when was_joined is true; indentation marks which statements belong to it. |
| 158 | <code>self.on_event(f'Peer left: {address[0]}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 160 | <code>def _discover(self):</code> | Define Sender._discover(). Reply to the app discovery request with source name and TCP port. |
| 161 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 162 | <code>self.discovery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)</code> | Set self.discovery to a new UDP IPv4 socket. |
| 163 | <code>self.discovery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)</code> | Set the socket option shown: reuse permits address rebinding; broadcast enables discovery; receive buffer requests OS queue capacity. |
| 164 | <code>self.discovery.bind(('', DISCOVERY_PORT))</code> | Bind this network socket to the shown local IP/port tuple; an empty host listens on local interfaces and port 0 requests an OS-assigned port. |
| 165 | <code>self.discovery.settimeout(.3)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 166 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 167 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 168 | <code>data, address = self.discovery.recvfrom(256)</code> | Set (data, address) to one UDP datagram and its source IP/port. |
| 169 | <code>if data == DISCOVERY_MAGIC:</code> | Take this branch only when data == DISCOVERY_MAGIC is true; indentation marks which statements belong to it. |
| 170 | <code>response = json.dumps(dict(app='LANStream', port=self.port, name=self.source.name)).encode()</code> | Set response to the result of json.dumps(dict(app='LANStream', port=self.port, name=self.source.name)).encode(). |
| 171 | <code>self.discovery.sendto(response, address)</code> | Send the given UDP bytes to the specified destination IP/port. |
| 172 | <code>except socket.timeout:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 173 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 174 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 175 | <code>if not self.stop_event.is_set():</code> | Take this branch only when not self.stop_event.is_set() is true; indentation marks which statements belong to it. |
| 176 | <code>self.on_event('Discovery unavailable; connect using IP and TCP port.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 177 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 178 | <code>if self.discovery:</code> | Take this branch only when self.discovery is true; indentation marks which statements belong to it. |
| 179 | <code>self.discovery.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 181 | <code>def _stream(self):</code> | Define Sender._stream(). Pace JPEG frames, apply artificial loss/delay per receiver, and send queued UDP copies when due. |
| 182 | <code>sequence, frame = 0, 0</code> | Start packet numbering and picture numbering separately at zero. |
| 183 | <code>queue = []</code> | Create the min-heap of delayed outgoing copies; this is not the receiver playback buffer. |
| 184 | <code>ticket = 0</code> | Set ticket to 0; this holds a unique tie-break number for scheduled packet copies. |
| 185 | <code>next_frame = time.monotonic()</code> | Set next_frame to the current local monotonic time in seconds; this holds the next scheduled source picture time. |
| 186 | <code>finished = False</code> | Set finished to False; this holds whether source EOF was reached and queued media should drain. |
| 187 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 188 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 189 | <code>now = time.monotonic()</code> | Set now to the current local monotonic time in seconds. |
| 190 | <code>while queue and queue[0][0] &lt;= now:</code> | Transmit scheduled copies whose earliest due time is no later than the current monotonic time. |
| 191 | <code>_, _, data, address = heapq.heappop(queue)</code> | Remove the earliest due tuple; its due-time/ticket have served their ordering purpose, leaving bytes and destination. |
| 192 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 193 | <code>self.udp.sendto(data, address)</code> | Send one media datagram to one receiver; a successful return does not prove delivery. |
| 194 | <code>self.sent_packets += 1</code> | Increase self.sent_packets by 1. |
| 195 | <code>self.sent_bytes += len(data)</code> | Increase self.sent_bytes by the number of elements/bytes in data. |
| 196 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 197 | <code>if self.stop_event.is_set():</code> | Take this branch only when self.stop_event.is_set() is true; indentation marks which statements belong to it. |
| 198 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 199 | <code>if finished:</code> | Take this branch only when finished is true; indentation marks which statements belong to it. |
| 200 | <code>if not queue:</code> | Take this branch only when not queue is true; indentation marks which statements belong to it. |
| 201 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 202 | <code>self.stop_event.wait(.002)</code> | Wait interruptibly for the specified seconds; an already-set stop event returns early. |
| 203 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 204 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 205 | <code>destinations = [client['address'] for client in self.clients.values()]</code> | Copy the current receiver destinations under the peer lock, then release the lock before media processing. |
| 206 | <code>if not destinations:</code> | Do not consume the source when there is nobody watching; reset source pacing while waiting. |
| 207 | <code>next_frame = now</code> | Set next_frame to now; this holds the next scheduled source picture time. |
| 208 | <code>self.stop_event.wait(.02)</code> | Wait interruptibly for the specified seconds; an already-set stop event returns early. |
| 209 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 210 | <code>if now &lt; next_frame:</code> | Wait until another frame is due instead of reading/encoding the source too quickly. |
| 211 | <code>self.stop_event.wait(min(.005, next_frame - now))</code> | Wait interruptibly for the specified seconds; an already-set stop event returns early. |
| 212 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 213 | <code>data = self.source.read()</code> | Read or generate the next JPEG picture as bytes. |
| 214 | <code>if data is None:</code> | Take this branch only when data is None is true; indentation marks which statements belong to it. |
| 215 | <code>finished = True</code> | Set finished to True; this holds whether source EOF was reached and queued media should drain. |
| 216 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 217 | <code>timestamp = time.monotonic()</code> | Set timestamp to the current local monotonic time in seconds. |
| 218 | <code>packets = list(packetize(data, self.stream, frame, sequence, timestamp))</code> | Split this JPEG into header-bearing datagrams with shared frame time/ID and successive packet numbers. |
| 219 | <code>for datagram in packets:</code> | Loop over packets, assigning each item to datagram. |
| 220 | <code>for address in destinations:</code> | Make a separate outgoing copy for each currently registered receiver. |
| 221 | <code>if random.random() * 100 &lt; self.loss:</code> | Draw an independent random percentage; discard this receiver copy when it is below the configured loss input. |
| 222 | <code>self.simulated_drops += 1</code> | Increase self.simulated_drops by 1. |
| 223 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 224 | <code>if len(queue) &gt;= 100000:</code> | Discard excess copies rather than allow the delayed-send heap to grow without bound. |
| 225 | <code>self.simulated_drops += 1</code> | Increase self.simulated_drops by 1. |
| 226 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 227 | <code>ticket += 1</code> | Increase ticket by 1. |
| 228 | <code>heapq.heappush(queue, (timestamp + random.uniform(0, self.jitter), ticket, datagram, address))</code> | Schedule the copy with uniform additional delay; a unique ticket breaks equal-time ties. Different due times can reorder packet numbers. |
| 229 | <code>sequence = (sequence + len(packets)) &amp; 0xffffffff</code> | Advance by the number of source datagrams, not by receiver count, and wrap into uint32 range. |
| 230 | <code>frame += 1</code> | Advance the picture ID once for the next JPEG, not once per packet. |
| 231 | <code>next_frame = max(next_frame + 1 / self.source.fps, timestamp)</code> | Move source pacing forward by one target frame interval without scheduling before the latest source timestamp. |
| 232 | <code>if finished:</code> | Take this branch only when finished is true; indentation marks which statements belong to it. |
| 233 | <code>self.on_event('Video finished.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 234 | <code>except Exception as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 235 | <code>self.on_event(f'Stream error: {exc}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 236 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 237 | <code>self.source.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 238 | <code>self.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 240 | <code>def snapshot(self):</code> | Define Sender.snapshot(). Copy peer reports and expose sender totals for the dashboard or CLI. |
| 241 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 242 | <code>peers = [dict(host=v['address'][0], port=v['address'][1], stats=dict(v['stats'])) for v in self.clients.values()]</code> | Set peers to [dict(host=v['address'][0], port=v['address'][1], stats=dict(v['stats'])) for v in self.clients.values()]. |
| 243 | <code>return dict(peers=peers, packets=self.sent_packets, bytes=self.sent_bytes,</code> | Return a dictionary containing the named fields shown in this call to the caller and leave this function. |
| 244 | <code>simulated_drops=self.simulated_drops, running=not self.stop_event.is_set())</code> | Continue the statement beginning on line 243. Return a dictionary containing the named fields shown in this call to the caller and leave this function. |
| 246 | <code>def stop(self):</code> | Define Sender.stop(). Signal stop, notify/close control connections, close sockets and wait briefly for workers. |
| 247 | <code>if self.stop_event.is_set():</code> | Take this branch only when self.stop_event.is_set() is true; indentation marks which statements belong to it. |
| 248 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 249 | <code>self.stop_event.set()</code> | Signal all workers that this session should stop. |
| 250 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 251 | <code>channels = list(self.connections)</code> | Set channels to the result of list(self.connections). |
| 252 | <code>for channel in channels:</code> | Loop over channels, assigning each item to channel. |
| 253 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 254 | <code>channel.send('END', message='Stream ended')</code> | Send the shown typed JSON control message and named fields on TCP. |
| 255 | <code>except (OSError, ValueError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 256 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 257 | <code>channel.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 258 | <code>for sock in (self.listener, self.udp, self.discovery):</code> | Loop over (self.listener, self.udp, self.discovery), assigning each item to sock. |
| 259 | <code>if sock:</code> | Take this branch only when sock is true; indentation marks which statements belong to it. |
| 260 | <code>sock.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 261 | <code>for thread in list(self.threads):</code> | Loop over list(self.threads), assigning each item to thread. |
| 262 | <code>if thread is not threading.current_thread():</code> | Take this branch only when thread is not threading.current_thread() is true; indentation marks which statements belong to it. |
| 263 | <code>thread.join(timeout=1)</code> | Wait up to the shown timeout for this worker thread to finish. |
| 264 | <code>self.source.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 267 | <code>class Receiver:</code> | Define the Receiver class, which groups its state and related methods. |
| 268 | <code>def __init__(self, host, port=5000, buffer_ms=120, on_frame=None, on_event=None, csv_path=None):</code> | Define Receiver.__init__(). Prepare receiver callbacks, metrics, frame assembler and shutdown state. |
| 269 | <code>self.host, self.port = host, port</code> | Set (self.host, self.port) to the values host, port. |
| 270 | <code>self.on_frame = on_frame or (lambda jpeg: None)</code> | Set self.on_frame to on_frame or (lambda jpeg: None); this holds the reconstructed-frame callback, with a no-op fallback. |
| 271 | <code>self.on_event = on_event or (lambda message: None)</code> | Set self.on_event to on_event or (lambda message: None); this holds the status callback, with a no-op fallback. |
| 272 | <code>self.metrics = Metrics()</code> | Set self.metrics to a new receiver statistics accumulator; this holds the receiver statistics accumulator. |
| 273 | <code>self.assembler = Assembler(self.metrics, buffer_ms)</code> | Set self.assembler to a timed frame assembler using the configured buffer; this holds the receiver timed frame reassembler. |
| 274 | <code>self.csv_path = csv_path</code> | Set self.csv_path to csv_path. |
| 275 | <code>self.stop_event = threading.Event()</code> | Set self.stop_event to a new interruptible stop event, initially unset; this holds the shared stop signal, allowing background waits/loops to end. |
| 276 | <code>self.threads = []</code> | Set self.threads to an empty list; this holds the list of worker threads to join during cleanup. |
| 277 | <code>self.udp = self.channel = None</code> | Set self.udp, self.channel to None. |
| 278 | <code>self.info = {}</code> | Set self.info to an empty dictionary; this holds the metadata advertised by the sender in INFO. |
| 279 | <code>self.end_at = None</code> | Set self.end_at to None; this holds the local deadline for finishing the end-of-stream buffer drain. |
| 280 | <code>self.recorder = None</code> | Set self.recorder to None; this holds the optional CSV writer (None means not enabled yet). |
| 282 | <code>def start(self):</code> | Define Receiver.start(). Bind UDP before JOIN, negotiate metadata over TCP and start media/control workers. |
| 283 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 284 | <code>self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)</code> | Set self.udp to a new UDP IPv4 socket. |
| 285 | <code>self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)</code> | Request a larger OS UDP receive buffer; the OS can adjust the actual allocated size. |
| 286 | <code>self.udp.bind(('', 0))</code> | Open the receiver UDP port before JOIN, binding to local IPv4 interfaces with an OS-assigned port. |
| 287 | <code>self.udp.settimeout(.01)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 288 | <code>sock = socket.create_connection((self.host, self.port), timeout=5)</code> | Set sock to the result of socket.create_connection((self.host, self.port), timeout=5). |
| 289 | <code>self.peer_ip = sock.getpeername()[0]</code> | Set self.peer_ip to sock.getpeername()[0]. |
| 290 | <code>self.channel = Channel(sock)</code> | Set self.channel to a newline-delimited JSON channel around the connected TCP socket; this holds the connected newline-delimited TCP control channel. |
| 291 | <code>self.channel.send('JOIN', udp_port=self.udp.getsockname()[1])</code> | Tell the source which already-bound local UDP port should receive the media. |
| 292 | <code>self.info = self.channel.receive()</code> | Set self.info to the next complete decoded TCP control message; this holds the metadata advertised by the sender in INFO. |
| 293 | <code>if self.info['type'] != 'INFO' or self.info.get('codec') != 'JPEG':</code> | Take this branch only when self.info['type'] != 'INFO' or self.info.get('codec') != 'JPEG' is true; indentation marks which statements belong to it. |
| 294 | <code>raise ValueError('Sender did not provide compatible stream metadata')</code> | Raise ValueError('Sender did not provide compatible stream metadata') to report failure to the caller. |
| 295 | <code>if not isinstance(self.info.get('stream'), int) or not isinstance(self.info.get('udp_port'), int):</code> | Take this branch only when not isinstance(self.info.get('stream'), int) or not isinstance(self.info.get('udp_port'), int) is true; indentation marks which statements belong to it. |
| 296 | <code>raise ValueError('Invalid sender metadata')</code> | Raise ValueError('Invalid sender metadata') to report failure to the caller. |
| 297 | <code>self.channel.sock.settimeout(.2)</code> | Set the maximum socket blocking wait (seconds) so the loop can periodically check its stop/deadline state. |
| 298 | <code>if self.csv_path:</code> | Take this branch only when self.csv_path is true; indentation marks which statements belong to it. |
| 299 | <code>self.recorder = CSVRecorder(self.csv_path)</code> | Set self.recorder to a CSV recorder for the chosen output path; this holds the optional CSV writer (None means not enabled yet). |
| 300 | <code>for target in (self._media, self._control):</code> | Loop over (self._media, self._control), assigning each item to target. |
| 301 | <code>thread = threading.Thread(target=target, daemon=True)</code> | Set thread to a worker thread configured with the shown target and arguments. |
| 302 | <code>self.threads.append(thread)</code> | Append the shown new entry to this list/deque for later processing or reporting. |
| 303 | <code>thread.start()</code> | Start the configured worker thread or session. |
| 304 | <code>self.on_event(f"Joined {self.info.get('name', 'stream')} at {self.peer_ip}:{self.port}")</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 305 | <code>except Exception:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 306 | <code>self.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 307 | <code>raise</code> | Raise the current exception again to report failure to the caller. |
| 308 | <code>return self</code> | Return self to the caller and leave this function. |
| 310 | <code>def _media(self):</code> | Define Receiver._media(). Validate arriving datagrams, update metrics, assemble/release JPEGs and drain at session end. |
| 311 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 312 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 313 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 314 | <code>data, address = self.udp.recvfrom(65535)</code> | Set (data, address) to one UDP datagram and its source IP/port. |
| 315 | <code>if address != (self.peer_ip, self.info['udp_port']):</code> | Ignore UDP datagrams not from the TCP peer IP and source media port advertised in INFO. |
| 316 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 317 | <code>packet = unpack(data)</code> | Set packet to the result of unpack(data). |
| 318 | <code>if packet.stream != self.info['stream']:</code> | Reject data from a different source session even if its IP and port match. |
| 319 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 320 | <code>now = time.monotonic()</code> | Set now to the current local monotonic time in seconds. |
| 321 | <code>if self.metrics.packet(packet, len(data), now):</code> | Update counters only for accepted unique packets; pass such packets on for frame assembly. |
| 322 | <code>self.assembler.add(packet, now)</code> | Store this chunk and its receive time for bounded, deadline-based frame reconstruction. |
| 323 | <code>except (socket.timeout, ValueError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 324 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 325 | <code>for jpeg in self.assembler.ready(time.monotonic()):</code> | Retrieve complete frames whose deadlines are due; partial expired frames are counted and skipped. |
| 326 | <code>self.on_frame(jpeg)</code> | Deliver reconstructed JPEG bytes to the GUI queue or CLI callback. |
| 327 | <code>if self.end_at and time.monotonic() &gt;= self.end_at:</code> | Stop media processing only after the end-of-session buffered-frame drain deadline. |
| 328 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 329 | <code>except OSError:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 330 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 331 | <code>except Exception as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 332 | <code>self.on_event(f'Playback error: {exc}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 333 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 334 | <code>self.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 336 | <code>def _control(self):</code> | Define Receiver._control(). Send PING/STAT about once per second, record CSV snapshots and measure matching PONG RTT. |
| 337 | <code>next_report = 0</code> | Set next_report to 0; this holds the next scheduled TCP heartbeat/statistics report time. |
| 338 | <code>pending_ping = None</code> | Set pending_ping to None; this holds the outstanding receiver-local PING timestamp token, or None when none is pending. |
| 339 | <code>last_reply = time.monotonic()</code> | Set last_reply to the current local monotonic time in seconds; this holds the latest received control-response time for timeout detection. |
| 340 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 341 | <code>while not self.stop_event.is_set():</code> | Repeat this block while not self.stop_event.is_set() remains true. |
| 342 | <code>now = time.monotonic()</code> | Set now to the current local monotonic time in seconds. |
| 343 | <code>if now &gt;= next_report:</code> | Take this branch only when now &gt;= next_report is true; indentation marks which statements belong to it. |
| 344 | <code>if pending_ping is None:</code> | Take this branch only when pending_ping is None is true; indentation marks which statements belong to it. |
| 345 | <code>pending_ping = now</code> | Record receiver-local send time and use it as the outstanding PING token. |
| 346 | <code>self.channel.send('PING', nonce=pending_ping)</code> | Send a timing token on TCP; no synchronized clock at the sender is needed. |
| 347 | <code>stats = self.metrics.snapshot()</code> | Set stats to a current copy of counters and computed statistics; this holds the current receiver report dictionary. |
| 348 | <code>self.channel.send('STAT', stats=stats)</code> | Send this receiver report to the source for the source peer list. |
| 349 | <code>if self.recorder:</code> | Take this branch only when self.recorder is true; indentation marks which statements belong to it. |
| 350 | <code>self.recorder.write(stats)</code> | Append the current statistics snapshot to the CSV recorder. |
| 351 | <code>next_report = now + 1</code> | Schedule another control report roughly one second later. |
| 352 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 353 | <code>message = self.channel.receive()</code> | Set message to the next complete decoded TCP control message. |
| 354 | <code>except socket.timeout:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 355 | <code>if time.monotonic() - last_reply &gt; 10:</code> | Consider the source unresponsive after ten seconds without any control reply. |
| 356 | <code>raise EOFError('Sender timed out')</code> | Raise EOFError('Sender timed out') to report failure to the caller. |
| 357 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 358 | <code>last_reply = time.monotonic()</code> | Set last_reply to the current local monotonic time in seconds; this holds the latest received control-response time for timeout detection. |
| 359 | <code>if message['type'] == 'PONG' and pending_ping == message.get('nonce'):</code> | Measure only a PONG matching the current outstanding PING token. |
| 360 | <code>with self.metrics.lock:</code> | Hold self.metrics.lock for this indented block, protecting shared state; release automatically on exit. |
| 361 | <code>self.metrics.rtt = (time.monotonic() - pending_ping) * 1000</code> | Compute receiver-local round-trip elapsed seconds and convert to milliseconds. |
| 362 | <code>pending_ping = None</code> | Set pending_ping to None; this holds the outstanding receiver-local PING timestamp token, or None when none is pending. |
| 363 | <code>elif message['type'] == 'END':</code> | If earlier branches did not match, test message['type'] == 'END' and run this branch when true. |
| 364 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 365 | <code>except (OSError, EOFError, ValueError, TypeError) as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 366 | <code>if not self.stop_event.is_set():</code> | Take this branch only when not self.stop_event.is_set() is true; indentation marks which statements belong to it. |
| 367 | <code>self.on_event(f'Control channel ended: {exc}')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 368 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 369 | <code>self.end_at = time.monotonic() + self.assembler.delay + .2</code> | Leave configured buffer time plus 200 ms for final frame draining after control ends. |
| 371 | <code>def stop(self):</code> | Define Receiver.stop(). Signal stop, send LEAVE where possible, close sockets, join workers and finalize the CSV. |
| 372 | <code>if self.stop_event.is_set():</code> | Take this branch only when self.stop_event.is_set() is true; indentation marks which statements belong to it. |
| 373 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 374 | <code>self.stop_event.set()</code> | Signal all workers that this session should stop. |
| 375 | <code>if self.channel:</code> | Take this branch only when self.channel is true; indentation marks which statements belong to it. |
| 376 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 377 | <code>self.channel.send('LEAVE')</code> | Send the shown typed JSON control message and named fields on TCP. |
| 378 | <code>except (OSError, ValueError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 379 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 380 | <code>self.channel.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 381 | <code>if self.udp:</code> | Take this branch only when self.udp is true; indentation marks which statements belong to it. |
| 382 | <code>self.udp.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 383 | <code>for thread in list(self.threads):</code> | Loop over list(self.threads), assigning each item to thread. |
| 384 | <code>if thread is not threading.current_thread():</code> | Take this branch only when thread is not threading.current_thread() is true; indentation marks which statements belong to it. |
| 385 | <code>thread.join(timeout=1)</code> | Wait up to the shown timeout for this worker thread to finish. |
| 386 | <code>if self.recorder:</code> | Take this branch only when self.recorder is true; indentation marks which statements belong to it. |
| 387 | <code>self.recorder.write(self.metrics.snapshot())</code> | Append the current statistics snapshot to the CSV recorder. |
| 388 | <code>self.recorder.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 389 | <code>self.on_event('Receiver stopped.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |

## lanstream/metrics.py

Measures accepted packets and reconstructs complete frames at timed playback deadlines.

[Open source](../lanstream/metrics.py)

### Function responsibilities

- **`Metrics.__init__()`**, line 9: Initialize the receiver counters, deduplication set, transit estimator and recent-byte window.
- **`Metrics.packet()`**, line 26: Accept one unique packet, update sequence/byte counts and smooth arrival variation.
- **`Metrics.increment()`**, line 52: Safely increase one named counter under the metrics lock.
- **`Metrics.snapshot()`**, line 56: Build a consistent report from counters, sequence gaps and the last second of received bytes.
- **`Assembler.__init__()`**, line 75: Validate the playout buffer and initialize bounded per-frame assembly state.
- **`Assembler.add()`**, line 84: Anchor playback, reject stale frames, and store a chunk under its frame and chunk indexes.
- **`Assembler.ready()`**, line 111: At due deadlines, return complete JPEGs in frame order and discard partial frames.
- **`CSVRecorder.__init__()`**, line 130: Create a CSV output directory/file and defer choosing columns until the first snapshot.
- **`CSVRecorder.write()`**, line 137: Write the header once, append a statistics row and flush it to disk.
- **`CSVRecorder.close()`**, line 144: Close the CSV file handle.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""Receiver metrics and bounded, reorder-tolerant JPEG frame assembly."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>import collections</code> | Import collections for an efficient deque for recent packet bytes. |
| 3 | <code>import csv</code> | Import csv for statistics CSV writing. |
| 4 | <code>import threading</code> | Import threading for background workers, events and locks. |
| 5 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 8 | <code>class Metrics:</code> | Define the Metrics class, which groups its state and related methods. |
| 9 | <code>def __init__(self):</code> | Define Metrics.__init__(). Initialize the receiver counters, deduplication set, transit estimator and recent-byte window. |
| 10 | <code>self.lock = threading.Lock()</code> | Set self.lock to a new mutual-exclusion lock; this holds the lock protecting shared peers or metric counters. |
| 11 | <code>self.started = time.monotonic()</code> | Record the local elapsed-time origin; this is not a wall-clock date. |
| 12 | <code>self.base = None</code> | No lowest observed packet number exists yet; it becomes known on first accepted packet. |
| 13 | <code>self.highest = None</code> | No highest observed packet number exists yet. |
| 14 | <code>self.unique = 0</code> | Set self.unique to 0; this holds the total number of accepted unique packet numbers. |
| 15 | <code>self.seen = set()</code> | Keep a bounded deduplication history of packet sequence numbers. |
| 16 | <code>self.bytes = 0</code> | Set self.bytes to 0; this holds the total number of accepted UDP application bytes. |
| 17 | <code>self.duplicates = 0</code> | Set self.duplicates to 0; this holds the duplicate-sequence counter. |
| 18 | <code>self.frames = 0</code> | Set self.frames to 0; this holds the complete-frame counter in Metrics, or newest-frame queue in App. |
| 19 | <code>self.dropped_frames = 0</code> | Set self.dropped_frames to 0; this holds the incomplete-frame expiration/eviction counter. |
| 20 | <code>self.late_frames = 0</code> | Set self.late_frames to 0; this holds the first-seen frames rejected for excessive lateness. |
| 21 | <code>self.jitter = 0.0</code> | Set self.jitter to 0.0; this holds the smoothed measured jitter in Metrics, or maximum artificial delay in Sender. |
| 22 | <code>self.previous = None</code> | Set self.previous to None; this holds the prior accepted arrival and sender-time pair for jitter. |
| 23 | <code>self.rtt = 0.0</code> | Set self.rtt to 0.0; this holds the latest measured TCP control RTT, in milliseconds. |
| 24 | <code>self.window = collections.deque()</code> | Store recent (arrival time, bytes) pairs so the oldest can be removed efficiently. |
| 26 | <code>def packet(self, packet, size, now):</code> | Define Metrics.packet(). Accept one unique packet, update sequence/byte counts and smooth arrival variation. |
| 27 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 28 | <code>seq = packet.sequence</code> | Extract this packet sequence number for duplicate checking and gap estimation. |
| 29 | <code>if self.base is None:</code> | Take this branch only when self.base is None is true; indentation marks which statements belong to it. |
| 30 | <code>self.base = self.highest = seq</code> | Anchor the observed sequence range to the first received packet; earlier unknown losses cannot be inferred. |
| 31 | <code>if seq in self.seen:</code> | Detect a duplicate in the retained sequence history; count it and do not add its bytes again. |
| 32 | <code>self.duplicates += 1</code> | Increase self.duplicates by 1. |
| 33 | <code>return False</code> | Reject this packet/condition so the caller does not assemble or double-count it. |
| 34 | <code># Very old packets are ignored after the deduplication horizon.</code> | Comment: Very old packets are ignored after the deduplication horizon. Comments explain intent and do not execute. |
| 35 | <code>if seq &lt; self.highest - 8192:</code> | Ignore packets older than the bounded tracking horizon rather than retain unlimited history. |
| 36 | <code>return False</code> | Reject this packet/condition so the caller does not assemble or double-count it. |
| 37 | <code>self.seen.add(seq)</code> | Add the shown channel, sequence number or frame ID to this tracking set. |
| 38 | <code>if len(self.seen) &gt; 16384:</code> | Periodically trim the deduplication set once it grows beyond its bound. |
| 39 | <code>self.seen = {x for x in self.seen if x &gt;= self.highest - 8192}</code> | Retain recent sequence numbers and discard old history. |
| 40 | <code>self.highest = max(self.highest, seq)</code> | Expand the highest observed sequence when a newer packet arrives. |
| 41 | <code>self.base = min(self.base, seq)</code> | Expand the lowest observed sequence if an earlier reordered packet arrives. |
| 42 | <code>self.unique += 1</code> | Count this accepted sequence number once. |
| 43 | <code>self.bytes += size</code> | Add accepted UDP application bytes, including the custom header but excluding lower network headers. |
| 44 | <code>self.window.append((now, size))</code> | Record arrival time and byte size for the sliding one-second throughput window. |
| 45 | <code>if self.previous:</code> | Take this branch only when self.previous is true; indentation marks which statements belong to it. |
| 46 | <code>arrival, sent = self.previous</code> | Recover the prior accepted packet arrival time and sender timestamp. |
| 47 | <code>delta = abs((now - arrival) - (packet.timestamp - sent)) * 1000</code> | Calculate absolute relative transit variation in milliseconds from consecutive accepted arrivals. |
| 48 | <code>self.jitter += (delta - self.jitter) / 16</code> | Move the smoothed jitter estimate 1/16 of the way toward the latest absolute variation. |
| 49 | <code>self.previous = (now, packet.timestamp)</code> | Remember this accepted arrival/sender-time pair for the next jitter update. |
| 50 | <code>return True</code> | Accept this packet so the caller can pass it on for assembly. |
| 52 | <code>def increment(self, name):</code> | Define Metrics.increment(). Safely increase one named counter under the metrics lock. |
| 53 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 54 | <code>setattr(self, name, getattr(self, name) + 1)</code> | Read a named numeric counter, add one, and write it back while locked. |
| 56 | <code>def snapshot(self):</code> | Define Metrics.snapshot(). Build a consistent report from counters, sequence gaps and the last second of received bytes. |
| 57 | <code>with self.lock:</code> | Hold self.lock for this indented block, protecting shared state; release automatically on exit. |
| 58 | <code>now = time.monotonic()</code> | Set now to the current local monotonic time in seconds. |
| 59 | <code>elapsed = max(.001, now - self.started)</code> | Calculate elapsed local seconds, with a small floor to avoid division by zero. |
| 60 | <code>while self.window and self.window[0][0] &lt; now - 1:</code> | Expire entries older than one second from the recent receive-byte window. |
| 61 | <code>self.window.popleft()</code> | Remove the oldest expired packet contribution in constant-time deque fashion. |
| 62 | <code>expected = 0 if self.base is None else self.highest - self.base + 1</code> | Compute the observed inclusive sequence range; it is unknown/zero before any packet arrives. |
| 63 | <code>missing = max(0, expected - self.unique)</code> | Estimate sequence gaps within the observed range; late arrivals can reduce this count. |
| 64 | <code>return dict(elapsed_s=round(elapsed, 2), packets=self.unique,</code> | Build a metrics report: elapsed seconds rounded to two places plus accepted-packet totals. |
| 65 | <code>missing=missing, loss_pct=round(100 * missing / max(1, expected), 2),</code> | Expose missing-count and cumulative gap percentage; use denominator 1 when no range exists to avoid zero division. |
| 66 | <code>duplicates=self.duplicates, frames=self.frames,</code> | Include duplicate-packet and complete-released-frame counts. |
| 67 | <code>dropped_frames=self.dropped_frames, late_frames=self.late_frames,</code> | Include expired/evicted partial frames and first-seen frames rejected as very late. |
| 68 | <code>jitter_ms=round(self.jitter, 2), rtt_ms=round(self.rtt, 2),</code> | Report smoothed jitter and latest TCP RTT in milliseconds rounded to two places. |
| 69 | <code>throughput_mbps=round(sum(x[1] for x in self.window) * 8 / 1e6, 3),</code> | Sum accepted application bytes still in the one-second window and convert to decimal megabits. |
| 70 | <code>average_mbps=round(self.bytes * 8 / elapsed / 1e6, 3),</code> | Divide all accepted bits by session seconds and one million for average Mb/s. |
| 71 | <code>fps=round(self.frames / elapsed, 1), bytes=self.bytes)</code> | Report session-average released-frame rate and total accepted application bytes. |
| 74 | <code>class Assembler:</code> | Define the Assembler class, which groups its state and related methods. |
| 75 | <code>def __init__(self, metrics, buffer_ms=120):</code> | Define Assembler.__init__(). Validate the playout buffer and initialize bounded per-frame assembly state. |
| 76 | <code>if not 0 &lt;= buffer_ms &lt;= 3000:</code> | Take this branch only when not 0 &lt;= buffer_ms &lt;= 3000 is true; indentation marks which statements belong to it. |
| 77 | <code>raise ValueError('Buffer must be 0–3000 ms')</code> | Raise ValueError('Buffer must be 0–3000 ms') to report failure to the caller. |
| 78 | <code>self.metrics, self.delay = metrics, buffer_ms / 1000</code> | Share the metrics object and convert receiver buffer milliseconds to seconds. |
| 79 | <code>self.pending = {}</code> | Map each partially assembled frame ID to its deadline, chunk count and received-index dictionary. |
| 80 | <code>self.anchor = None</code> | Wait for the first media packet before choosing receiver/sender relative clock anchors. |
| 81 | <code>self.last_played = -1</code> | No frame has been released yet; later this prevents older frames playing after newer ones. |
| 82 | <code>self.observed = set()</code> | Track recently first-seen frames so an expired frame is not reopened by later chunks. |
| 84 | <code>def add(self, packet, now):</code> | Define Assembler.add(). Anchor playback, reject stale frames, and store a chunk under its frame and chunk indexes. |
| 85 | <code>if self.anchor is None:</code> | Take this branch only when self.anchor is None is true; indentation marks which statements belong to it. |
| 86 | <code>self.anchor = (now, packet.timestamp)</code> | Anchor source-relative playback time to the first accepted packet local arrival. |
| 87 | <code>if packet.frame &lt;= self.last_played:</code> | Ignore chunks at or before the latest released frame to keep playback moving forward. |
| 88 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 89 | <code>entry = self.pending.get(packet.frame)</code> | Look up existing assembly state for this picture. |
| 90 | <code>if entry is None:</code> | Take this branch only when entry is None is true; indentation marks which statements belong to it. |
| 91 | <code>if packet.frame in self.observed:</code> | Reject an already handled/expired picture rather than recreating its buffer. |
| 92 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 93 | <code>self.observed.add(packet.frame)</code> | Add the shown channel, sequence number or frame ID to this tracking set. |
| 94 | <code>if len(self.observed) &gt; 512:</code> | Take this branch only when len(self.observed) &gt; 512 is true; indentation marks which statements belong to it. |
| 95 | <code>self.observed = {x for x in self.observed if x &gt;= packet.frame - 256}</code> | Bound recent frame-ID history by retaining only nearby frame numbers. |
| 96 | <code>deadline = self.anchor[0] + packet.timestamp - self.anchor[1] + self.delay</code> | Translate the source frame timestamp to a local deadline relative to the first packet and add receiver buffer time. |
| 97 | <code>if deadline &lt; now - .1:</code> | Reject a first-seen frame that is more than 100 ms beyond its intended playout deadline. |
| 98 | <code>self.metrics.increment('late_frames')</code> | Count a newly observed frame rejected by the lateness threshold. |
| 99 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 100 | <code>if len(self.pending) &gt;= 64:</code> | Cap the number of simultaneously buffered frames at 64. |
| 101 | <code>oldest = min(self.pending)</code> | Choose the lowest frame number for eviction when the pending frame cap is reached. |
| 102 | <code>del self.pending[oldest]</code> | Remove self.pending[oldest] from the frame/state container. |
| 103 | <code>self.metrics.increment('dropped_frames')</code> | Count a partial frame that expired or was evicted; this does not count every wholly unseen frame. |
| 104 | <code># Even a zero playout buffer needs a brief chunk assembly window.</code> | Comment: Even a zero playout buffer needs a brief chunk assembly window. Comments explain intent and do not execute. |
| 105 | <code>deadline = max(deadline, now + .015)</code> | Give a new frame at least 15 ms to collect chunks, including with Buffer=0. |
| 106 | <code>entry = self.pending[packet.frame] = [deadline, packet.count, {}]</code> | Create assembly state containing playout deadline, expected number of chunks and empty indexed payloads. |
| 107 | <code>if packet.count != entry[1]:</code> | Reject inconsistent total-chunk counts for one frame. |
| 108 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 109 | <code>entry[2][packet.index] = packet.payload</code> | Store payload by its chunk index so arrival order does not affect reconstruction. |
| 111 | <code>def ready(self, now):</code> | Define Assembler.ready(). At due deadlines, return complete JPEGs in frame order and discard partial frames. |
| 112 | <code>frames = []</code> | Set frames to an empty list; this holds the list of complete JPEGs released by this ready() call. |
| 113 | <code>for frame in sorted(list(self.pending)):</code> | Check a snapshot of pending frame IDs in ascending order while allowing entries to be removed. |
| 114 | <code>deadline, count, parts = self.pending[frame]</code> | Unpack one frame deadline, required chunk count and indexed payloads. |
| 115 | <code>if now &lt; deadline:</code> | Do not release or expire a frame until its calculated deadline arrives. |
| 116 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 117 | <code>del self.pending[frame]</code> | Remove self.pending[frame] from the frame/state container. |
| 118 | <code>if frame &lt;= self.last_played:</code> | Take this branch only when frame &lt;= self.last_played is true; indentation marks which statements belong to it. |
| 119 | <code>continue</code> | Skip the remainder of this loop iteration and start the next one. |
| 120 | <code>if len(parts) == count:</code> | Only reconstruct a JPEG when every valid chunk index has arrived. |
| 121 | <code>frames.append(b''.join(parts[i] for i in range(count)))</code> | Concatenate payloads by numeric index to reproduce the original JPEG bytes. |
| 122 | <code>self.last_played = frame</code> | Advance the newest released frame ID so later old arrivals cannot rewind playback. |
| 123 | <code>self.metrics.increment('frames')</code> | Count one complete JPEG released to the playback callback, not a guaranteed physical screen redraw. |
| 124 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 125 | <code>self.metrics.increment('dropped_frames')</code> | Count a partial frame that expired or was evicted; this does not count every wholly unseen frame. |
| 126 | <code>return frames</code> | Return frames to the caller and leave this function. |
| 129 | <code>class CSVRecorder:</code> | Define the CSVRecorder class, which groups its state and related methods. |
| 130 | <code>def __init__(self, path):</code> | Define CSVRecorder.__init__(). Create a CSV output directory/file and defer choosing columns until the first snapshot. |
| 131 | <code>from pathlib import Path</code> | Import Path from pathlib for portable filesystem paths. |
| 132 | <code>path = Path(path)</code> | Set path to a portable Path object for the given filename. |
| 133 | <code>path.parent.mkdir(parents=True, exist_ok=True)</code> | Ensure the output directory exists, including parents when requested. |
| 134 | <code>self.file = path.open('w', newline='')</code> | Set self.file to the result of path.open('w', newline=''). |
| 135 | <code>self.writer = None</code> | Set self.writer to None; this holds the CSV writer initialized after the first report defines its columns. |
| 137 | <code>def write(self, stats):</code> | Define CSVRecorder.write(). Write the header once, append a statistics row and flush it to disk. |
| 138 | <code>if self.writer is None:</code> | Take this branch only when self.writer is None is true; indentation marks which statements belong to it. |
| 139 | <code>self.writer = csv.DictWriter(self.file, fieldnames=list(stats))</code> | Set self.writer to a CSV dictionary writer with columns in the shown order; this holds the CSV writer initialized after the first report defines its columns. |
| 140 | <code>self.writer.writeheader()</code> | Write the CSV column names once at the top of the file. |
| 141 | <code>self.writer.writerow(stats)</code> | Append one dictionary of measurements to the CSV. |
| 142 | <code>self.file.flush()</code> | Flush Python output buffers so current CSV data is written promptly. |
| 144 | <code>def close(self):</code> | Define CSVRecorder.close(). Close the CSV file handle. |
| 145 | <code>self.file.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |

## lanstream/gui.py

Builds the desktop window and connects buttons, worker queues, playback, counters and the chart.

[Open source](../lanstream/gui.py)

### Function responsibilities

- **`App.__init__()`**, line 20: Create Tk state, queues and default controls, build the window and schedule periodic callbacks.
- **`App._style()`**, line 52: Configure Tk widget colors, fonts, padding and active/disabled appearance.
- **`App.label()`**, line 68: Construct a label with the project font and the parent background color.
- **`App._layout()`**, line 72: Build and position the source controls, playback canvas, cards, graph, log and footer.
- **`App.field()`**, line 151: Place a caption and editable entry linked to a Tk variable.
- **`App.choose()`**, line 155: Ask for a video path and show its filename in the source label.
- **`App.demo()`**, line 161: Select the generated test source instead of a file.
- **`App.event()`**, line 165: Queue a text status event for the main Tk thread without blocking if the queue is full.
- **`App.frame()`**, line 171: Keep at most the newest received JPEG for the next GUI refresh.
- **`App.background()`**, line 181: Temporarily disable session buttons and run a start/stop/discovery task outside the GUI thread.
- **`App.background.run()`**, line 188: Execute that worker task and queue either its error or its completion notification.
- **`App.start_sender()`**, line 197: Read and validate sender controls, then build/start a VideoSource and Sender in a worker.
- **`App.start_sender.task()`**, line 211: Open the chosen source, start networking, and retain the sender unless the window was closed.
- **`App.start_receiver()`**, line 224: Read destination/buffer controls, choose a timestamped CSV path and connect in a worker.
- **`App.start_receiver.task()`**, line 236: Connect a receiver with frame/status callbacks and store it if the app is still open.
- **`App.scan()`**, line 245: Run sender discovery asynchronously.
- **`App.scan.task()`**, line 246: Collect discovery results and queue them for the main thread.
- **`App.stop()`**, line 251: Schedule shutdown of both roles in a background worker.
- **`App.stop.task()`**, line 252: Stop the receiver and sender, then queue a completion status.
- **`App.tick()`**, line 260: Process worker events, show the latest frame and schedule another GUI poll in 40 ms.
- **`App.draw_frame()`**, line 297: Decode the received JPEG, fit it inside the playback canvas and display a retained Tk image.
- **`App.resize()`**, line 310: Redraw the image or recenter the placeholder when canvas geometry changes.
- **`App.update_stats()`**, line 316: Refresh receiver cards/throughput history and sender peer totals, then reschedule after 500 ms.
- **`App.save_frame()`**, line 345: Save the last received JPEG to a user-selected file.
- **`App.close()`**, line 356: Mark the app closed, destroy its window and stop remaining sessions.
- **`App.run()`**, line 364: Enter the Tk event loop so button and timer callbacks can execute.
- **`launch()`**, line 368: Construct the desktop App and enter its event loop.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""Tk desktop dashboard; network and decode work stay off the UI thread."""</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>import io</code> | Import io for in-memory image byte buffers. |
| 3 | <code>import queue</code> | Import queue for bounded thread-safe worker/UI communication. |
| 4 | <code>import threading</code> | Import threading for background workers, events and locks. |
| 5 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 6 | <code>import tkinter as tk</code> | Import tkinter for the desktop GUI. |
| 7 | <code>from tkinter import ttk, filedialog, messagebox</code> | Import ttk, filedialog, messagebox from tkinter for the desktop GUI. |
| 8 | <code>from pathlib import Path</code> | Import Path from pathlib for portable filesystem paths. |
| 9 | <code>from .media import VideoSource</code> | Import VideoSource from media for project helpers used in this file. |
| 10 | <code>from .network import Sender, Receiver, discover, local_ip</code> | Import Sender, Receiver, discover, local_ip from network for project helpers used in this file. |
| 12 | <code>BG = '#0b1220'</code> | Set BG to '#0b1220'. |
| 13 | <code>PANEL = '#142035'</code> | Set PANEL to '#142035'. |
| 14 | <code>TEXT = '#e7effc'</code> | Set TEXT to '#e7effc'. |
| 15 | <code>MUTED = '#8fa4bf'</code> | Set MUTED to '#8fa4bf'. |
| 16 | <code>GREEN = '#39dcb1'</code> | Set GREEN to '#39dcb1'. |
| 19 | <code>class App:</code> | Define the App class, which groups its state and related methods. |
| 20 | <code>def __init__(self):</code> | Define App.__init__(). Create Tk state, queues and default controls, build the window and schedule periodic callbacks. |
| 21 | <code>self.root = tk.Tk()</code> | Set self.root to the top-level Tk application window. |
| 22 | <code>self.root.title('LANStream • Computer Networks Lab')</code> | Set the text in the desktop window title bar. |
| 23 | <code>self.root.geometry('1220x850')</code> | Set the initial desktop window size in pixels. |
| 24 | <code>self.root.minsize(1000, 760)</code> | Prevent the window from being resized below these dimensions. |
| 25 | <code>self.root.configure(bg=BG)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 26 | <code>self.sender = self.receiver = None</code> | Set self.sender, self.receiver to None. |
| 27 | <code>self.busy = False</code> | Set self.busy to False; this holds whether an asynchronous start/stop/discovery operation is in progress. |
| 28 | <code>self.closed = False</code> | Set self.closed to False; this holds whether the GUI has been closed and periodic callbacks should stop. |
| 29 | <code>self.messages = queue.Queue(maxsize=200)</code> | Bound status/result messages passed from workers to the main Tk thread. |
| 30 | <code>self.frames = queue.Queue(maxsize=1)</code> | Limit pending GUI pictures to one; a newer received frame replaces a stale queued frame. |
| 31 | <code>self.photo = None</code> | Set self.photo to None; this holds the retained Tk image reference for the playback canvas. |
| 32 | <code>self.last_jpeg = None</code> | Set self.last_jpeg to None; this holds the most recently displayed/pending received JPEG bytes. |
| 33 | <code>self.history = []</code> | Set self.history to an empty list; this holds the retained receive-throughput samples for the green chart. |
| 34 | <code>self.status = tk.StringVar(value='Ready to connect')</code> | Set self.status to a Tk-linked text value initialized as shown. |
| 35 | <code>self.file = tk.StringVar(value='Animated demo (no video file needed)')</code> | Set self.file to a Tk-linked text value initialized as shown. |
| 36 | <code>self.host = tk.StringVar(value='127.0.0.1')</code> | Set self.host to a Tk-linked text value initialized as shown. |
| 37 | <code>self.port = tk.StringVar(value='5000')</code> | Set self.port to a Tk-linked text value initialized as shown. |
| 38 | <code>self.fps = tk.StringVar(value='20')</code> | Set self.fps to a Tk-linked text value initialized as shown. |
| 39 | <code>self.quality = tk.StringVar(value='70')</code> | Set self.quality to a Tk-linked text value initialized as shown. |
| 40 | <code>self.width = tk.StringVar(value='640')</code> | Set self.width to a Tk-linked text value initialized as shown. |
| 41 | <code>self.loss = tk.StringVar(value='0')</code> | Set self.loss to a Tk-linked text value initialized as shown. |
| 42 | <code>self.jitter = tk.StringVar(value='0')</code> | Set self.jitter to a Tk-linked text value initialized as shown; this holds the smoothed measured jitter in Metrics, or maximum artificial delay in Sender. |
| 43 | <code>self.buffer = tk.StringVar(value='120')</code> | Set self.buffer to a Tk-linked text value initialized as shown. |
| 44 | <code>self.loop = tk.BooleanVar(value=True)</code> | Set self.loop to a Tk-linked boolean value initialized as shown. |
| 45 | <code>self.video_path = None</code> | Set self.video_path to None; this holds the selected source path; None means generated demo. |
| 46 | <code>self._style()</code> | Call self._style(); see the function summary above for its role in this stage. |
| 47 | <code>self._layout()</code> | Call self._layout(); see the function summary above for its role in this stage. |
| 48 | <code>self.root.protocol('WM_DELETE_WINDOW', self.close)</code> | Route the window close action through session cleanup. |
| 49 | <code>self.root.after(40, self.tick)</code> | Request the next GUI event/frame poll in 40 ms; Tk scheduling is approximate. |
| 50 | <code>self.root.after(500, self.update_stats)</code> | Request the next cards/chart/peer update in 500 ms, approximately two samples per second. |
| 52 | <code>def _style(self):</code> | Define App._style(). Configure Tk widget colors, fonts, padding and active/disabled appearance. |
| 53 | <code>style = ttk.Style(self.root)</code> | Set style to the themed-widget style manager. |
| 54 | <code>style.theme_use('clam')</code> | Set the themed widget appearance/state rules shown in this style call. |
| 55 | <code>style.configure('.', background=BG, foreground=TEXT, font=('Helvetica', 11))</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 56 | <code>style.configure('TFrame', background=BG)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 57 | <code>style.configure('Card.TFrame', background=PANEL)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 58 | <code>style.configure('TLabel', background=BG, foreground=TEXT)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 59 | <code>style.configure('Muted.TLabel', foreground=MUTED)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 60 | <code>style.configure('TButton', background='#253b58', foreground=TEXT, padding=(12, 9), borderwidth=0)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 61 | <code>style.map('TButton', background=[('active', '#345170'), ('disabled', '#182438')])</code> | Set the themed widget appearance/state rules shown in this style call. |
| 62 | <code>style.configure('Accent.TButton', background='#146f62', foreground='white')</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 63 | <code>style.configure('TEntry', fieldbackground='#1c2c43', foreground=TEXT, insertcolor=TEXT, padding=6)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 64 | <code>style.configure('TCheckbutton', background=BG, foreground=TEXT)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 65 | <code>style.map('TCheckbutton', background=[('active', BG)])</code> | Set the themed widget appearance/state rules shown in this style call. |
| 66 | <code>style.configure('TCombobox', fieldbackground='#1c2c43', foreground=TEXT, padding=5)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 68 | <code>def label(self, parent, text, size=11, color=TEXT, **kwargs):</code> | Define App.label(). Construct a label with the project font and the parent background color. |
| 69 | <code>return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,</code> | Return a GUI caption/value label with the shown text and styling to the caller and leave this function. |
| 70 | <code>font=('Helvetica', size), **kwargs)</code> | Continue the statement beginning on line 69. Return a GUI caption/value label with the shown text and styling to the caller and leave this function. |
| 72 | <code>def _layout(self):</code> | Define App._layout(). Build and position the source controls, playback canvas, cards, graph, log and footer. |
| 73 | <code>header = tk.Frame(self.root, bg=BG)</code> | Set header to a container for grouping and positioning GUI widgets. |
| 74 | <code>header.pack(fill='x', padx=26, pady=(22, 14))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 75 | <code>self.label(header, '◉  LANStream', 25, GREEN).pack(side='left')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 76 | <code>self.label(header, 'PEER-TO-PEER VIDEO  /  NETWORK LAB', 10, MUTED).pack(side='left', padx=25)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 77 | <code>self.label(header, f'Local IP  {local_ip()}', 11, MUTED).pack(side='right')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 78 | <code>body = tk.Frame(self.root, bg=BG)</code> | Set body to a container for grouping and positioning GUI widgets. |
| 79 | <code>body.pack(fill='both', expand=True, padx=26)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 80 | <code>sidebar = tk.Frame(body, bg=BG, width=300)</code> | Set sidebar to a container for grouping and positioning GUI widgets. |
| 81 | <code>sidebar.pack(side='left', fill='y', padx=(0, 20))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 82 | <code>sidebar.pack_propagate(False)</code> | Disable automatic container shrinking so the sidebar keeps its requested width. |
| 83 | <code>main = tk.Frame(body, bg=BG)</code> | Set main to a container for grouping and positioning GUI widgets. |
| 84 | <code>main.pack(side='left', fill='both', expand=True)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 85 | <code>self.label(sidebar, '01   SOURCE &amp; SESSION', 11, GREEN).pack(anchor='w', pady=(0, 10))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 86 | <code>self.label(sidebar, 'Video source', 10, MUTED).pack(anchor='w')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 87 | <code>self.source_label = tk.Label(sidebar, textvariable=self.file, bg=BG, fg=TEXT,</code> | Set self.source_label to a GUI caption/value label with the shown text and styling. |
| 88 | <code>wraplength=290, justify='left', font=('Helvetica', 11))</code> | Continue the statement beginning on line 87. Set self.source_label to a GUI caption/value label with the shown text and styling. |
| 89 | <code>self.source_label.pack(anchor='w', pady=7)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 90 | <code>row = ttk.Frame(sidebar)</code> | Set row to a container for grouping and positioning GUI widgets. |
| 91 | <code>row.pack(fill='x')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 92 | <code>ttk.Button(row, text='Choose video', command=self.choose).pack(side='left')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 93 | <code>ttk.Button(row, text='Use demo', command=self.demo).pack(side='left', padx=7)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 94 | <code>ttk.Checkbutton(sidebar, text='Loop video', variable=self.loop).pack(anchor='w', pady=8)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 95 | <code>self.field(sidebar, 'Sender IP / hostname', self.host)</code> | Call self.field(sidebar, 'Sender IP / hostname', self.host); see the function summary above for its role in this stage. |
| 96 | <code>self.field(sidebar, 'TCP control port', self.port)</code> | Call self.field(sidebar, 'TCP control port', self.port); see the function summary above for its role in this stage. |
| 97 | <code>ttk.Button(sidebar, text='Discover LAN senders', command=self.scan).pack(fill='x', pady=7)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 98 | <code>self.label(sidebar, '02   MEDIA &amp; NETWORK', 11, GREEN).pack(anchor='w', pady=(16, 8))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 99 | <code>grid = tk.Frame(sidebar, bg=BG)</code> | Set grid to a container for grouping and positioning GUI widgets. |
| 100 | <code>grid.pack(fill='x')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 101 | <code>settings = [('FPS', self.fps), ('Width (px)', self.width), ('JPEG quality', self.quality),</code> | Set settings to [('FPS', self.fps), ('Width (px)', self.width), ('JPEG quality', self.quality), ('Loss (%)', self.loss), ('Jitter (ms)', self.jitter), ('Buffer (ms)', self.buffer)]. |
| 102 | <code>('Loss (%)', self.loss), ('Jitter (ms)', self.jitter), ('Buffer (ms)', self.buffer)]</code> | Continue the statement beginning on line 101. Set settings to [('FPS', self.fps), ('Width (px)', self.width), ('JPEG quality', self.quality), ('Loss (%)', self.loss), ('Jitter (ms)', self.jitter), ('Buffer (ms)', self.buffer)]. |
| 103 | <code>for i, (name, var) in enumerate(settings):</code> | Loop over enumerate(settings), assigning each item to (i, (name, var)). |
| 104 | <code>cell = tk.Frame(grid, bg=BG)</code> | Set cell to a container for grouping and positioning GUI widgets. |
| 105 | <code>cell.grid(row=i//2, column=i%2, sticky='ew', padx=(0, 10), pady=4)</code> | Place this GUI widget at the specified grid row/column, with the shown spacing. |
| 106 | <code>self.label(cell, name, 10, MUTED).pack(anchor='w')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 107 | <code>ttk.Entry(cell, textvariable=var, width=11).pack(fill='x', pady=3)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 108 | <code>grid.columnconfigure(0, weight=1)</code> | Give this layout column expansion weight so widgets can share available width. |
| 109 | <code>grid.columnconfigure(1, weight=1)</code> | Give this layout column expansion weight so widgets can share available width. |
| 110 | <code>self.label(sidebar, 'Loss/jitter apply at sender; buffer at receiver.\nSettings apply when starting a new session.', 9, MUTED,</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 111 | <code>justify='left').pack(anchor='w', pady=8)</code> | Continue the statement beginning on line 110. Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 112 | <code>self.send_button = ttk.Button(sidebar, text='Start sender', style='Accent.TButton', command=self.start_sender)</code> | Set self.send_button to the result of ttk.Button(sidebar, text='Start sender', style='Accent.TButton', command=self.start_sender). |
| 113 | <code>self.send_button.pack(fill='x', pady=(7, 4))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 114 | <code>self.receive_button = ttk.Button(sidebar, text='Join stream', style='Accent.TButton', command=self.start_receiver)</code> | Set self.receive_button to the result of ttk.Button(sidebar, text='Join stream', style='Accent.TButton', command=self.start_receiver). |
| 115 | <code>self.receive_button.pack(fill='x', pady=4)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 116 | <code>self.stop_button = ttk.Button(sidebar, text='Stop all sessions', command=self.stop)</code> | Set self.stop_button to the result of ttk.Button(sidebar, text='Stop all sessions', command=self.stop). |
| 117 | <code>self.stop_button.pack(fill='x', pady=4)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 118 | <code>self.label(main, 'LIVE PLAYBACK', 10, MUTED).pack(anchor='w')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 119 | <code>self.canvas = tk.Canvas(main, bg='#070c15', highlightthickness=1, highlightbackground='#253650', height=325)</code> | Set self.canvas to a drawing canvas for playback or the chart, with the shown appearance. |
| 120 | <code>self.canvas.pack(fill='both', expand=True, pady=(8, 12))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 121 | <code>self.canvas.create_text(300, 150, text='Your stream will appear here\nStart a sender, then join its IP address.',</code> | Draw the shown caption/placeholder on a canvas with the specified position and style. |
| 122 | <code>fill=MUTED, font=('Helvetica', 14), justify='center', tags='placeholder')</code> | Continue the statement beginning on line 121. Draw the shown caption/placeholder on a canvas with the specified position and style. |
| 123 | <code>self.canvas.bind('&lt;Configure&gt;', self.resize)</code> | Connect the shown Tk event to its handler callback. |
| 124 | <code>cards = tk.Frame(main, bg=BG)</code> | Set cards to a container for grouping and positioning GUI widgets. |
| 125 | <code>cards.pack(fill='x')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 126 | <code>self.values = {}</code> | Set self.values to an empty dictionary. |
| 127 | <code>for i, (key, title, unit) in enumerate([('throughput_mbps', 'THROUGHPUT', 'Mb/s'), ('loss_pct', 'PACKET LOSS', '%'),</code> | Loop over enumerate([('throughput_mbps', 'THROUGHPUT', 'Mb/s'), ('loss_pct', 'PACKET LOSS', '%'), ('jitter_ms', 'JITTER', 'ms'), ('rtt_ms', 'CONTROL RTT', 'ms')]), assigning each item to (i, (key, title, unit)). |
| 128 | <code>('jitter_ms', 'JITTER', 'ms'), ('rtt_ms', 'CONTROL RTT', 'ms')]):</code> | Continue the statement beginning on line 127. Loop over enumerate([('throughput_mbps', 'THROUGHPUT', 'Mb/s'), ('loss_pct', 'PACKET LOSS', '%'), ('jitter_ms', 'JITTER', 'ms'), ('rtt_ms', 'CONTROL RTT', 'ms')]), assigning each item to (i, (key, title, unit)). |
| 129 | <code>card = tk.Frame(cards, bg=PANEL, padx=12, pady=10)</code> | Set card to a container for grouping and positioning GUI widgets. |
| 130 | <code>card.grid(row=0, column=i, sticky='ew', padx=(0, 7))</code> | Place this GUI widget at the specified grid row/column, with the shown spacing. |
| 131 | <code>cards.columnconfigure(i, weight=1)</code> | Give this layout column expansion weight so widgets can share available width. |
| 132 | <code>self.label(card, title, 9, MUTED).pack(anchor='w')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 133 | <code>value = self.label(card, f'0 {unit}', 19, GREEN)</code> | Set value to a GUI caption/value label with the shown text and styling. |
| 134 | <code>value.pack(anchor='w', pady=(6, 0))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 135 | <code>self.values[key] = (value, unit)</code> | Set self.values[key] to the values value, unit. |
| 136 | <code>self.detail = self.label(main, 'No active session • JPEG video over UDP • TCP signalling', 10, MUTED)</code> | Set self.detail to a GUI caption/value label with the shown text and styling. |
| 137 | <code>self.detail.pack(anchor='w', pady=(10, 6))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 138 | <code>self.chart = tk.Canvas(main, height=65, bg=PANEL, highlightthickness=0)</code> | Set self.chart to a drawing canvas for playback or the chart, with the shown appearance. |
| 139 | <code>self.chart.pack(fill='x', pady=(0, 8))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 140 | <code>self.peers = self.label(main, 'Connected receivers: 0', 10, MUTED, anchor='w', justify='left')</code> | Set self.peers to a GUI caption/value label with the shown text and styling. |
| 141 | <code>self.peers.pack(fill='x', pady=3)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 142 | <code>self.log = tk.Text(main, height=5, bg='#0e1929', fg=MUTED, font=('Courier', 10),</code> | Set self.log to a scrollable text area used for status logging. |
| 143 | <code>relief='flat', state='disabled', wrap='word')</code> | Continue the statement beginning on line 142. Set self.log to a scrollable text area used for status logging. |
| 144 | <code>self.log.pack(fill='x', pady=(5, 0))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 145 | <code>footer = tk.Frame(self.root, bg=BG)</code> | Set footer to a container for grouping and positioning GUI widgets. |
| 146 | <code>footer.pack(fill='x', padx=26, pady=12)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 147 | <code>tk.Label(footer, textvariable=self.status, bg=BG, fg=GREEN, font=('Helvetica', 10)).pack(side='left')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 148 | <code>ttk.Button(footer, text='Save current frame', command=self.save_frame).pack(side='right')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 149 | <code>self.label(footer, 'CSV reports saved to captures/', 10, MUTED).pack(side='right', padx=16)</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 151 | <code>def field(self, parent, label, variable):</code> | Define App.field(). Place a caption and editable entry linked to a Tk variable. |
| 152 | <code>self.label(parent, label, 10, MUTED).pack(anchor='w', pady=(7, 3))</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 153 | <code>ttk.Entry(parent, textvariable=variable).pack(fill='x')</code> | Place this GUI widget in its parent with the shown direction, fill, expansion and padding. |
| 155 | <code>def choose(self):</code> | Define App.choose(). Ask for a video path and show its filename in the source label. |
| 156 | <code>path = filedialog.askopenfilename(filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv *.webm'), ('All files', '*')])</code> | Set path to the result of filedialog.askopenfilename(filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv *.webm'), ('All files', '*')]). |
| 157 | <code>if path:</code> | Take this branch only when path is true; indentation marks which statements belong to it. |
| 158 | <code>self.video_path = path</code> | Set self.video_path to path; this holds the selected source path; None means generated demo. |
| 159 | <code>self.file.set(Path(path).name)</code> | Update the linked Tk value or event state with the argument shown. |
| 161 | <code>def demo(self):</code> | Define App.demo(). Select the generated test source instead of a file. |
| 162 | <code>self.video_path = None</code> | Set self.video_path to None; this holds the selected source path; None means generated demo. |
| 163 | <code>self.file.set('Animated demo (no video file needed)')</code> | Update the linked Tk value or event state with the argument shown. |
| 165 | <code>def event(self, message):</code> | Define App.event(). Queue a text status event for the main Tk thread without blocking if the queue is full. |
| 166 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 167 | <code>self.messages.put_nowait(('event', str(message)))</code> | Pass the shown frame or event/result tuple to a thread-safe queue for the main GUI thread. |
| 168 | <code>except queue.Full:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 169 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 171 | <code>def frame(self, jpeg):</code> | Define App.frame(). Keep at most the newest received JPEG for the next GUI refresh. |
| 172 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 173 | <code>self.frames.get_nowait()</code> | Discard a stale queued GUI picture without blocking; the replacement follows below. |
| 174 | <code>except queue.Empty:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 175 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 176 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 177 | <code>self.frames.put_nowait(jpeg)</code> | Offer the newest JPEG to the one-picture queue for the GUI thread. |
| 178 | <code>except queue.Full:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 179 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 181 | <code>def background(self, task):</code> | Define App.background(). Temporarily disable session buttons and run a start/stop/discovery task outside the GUI thread. |
| 182 | <code>if self.busy:</code> | Take this branch only when self.busy is true; indentation marks which statements belong to it. |
| 183 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 184 | <code>self.busy = True</code> | Set self.busy to True; this holds whether an asynchronous start/stop/discovery operation is in progress. |
| 185 | <code>self.send_button.state(['disabled'])</code> | Change the button state as shown; disabled blocks actions and !disabled restores them. |
| 186 | <code>self.receive_button.state(['disabled'])</code> | Change the button state as shown; disabled blocks actions and !disabled restores them. |
| 187 | <code>self.stop_button.state(['disabled'])</code> | Change the button state as shown; disabled blocks actions and !disabled restores them. |
| 188 | <code>def run():</code> | Define App.background.run(). Execute that worker task and queue either its error or its completion notification. |
| 189 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 190 | <code>task()</code> | Call task(); see the function summary above for its role in this stage. |
| 191 | <code>except Exception as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 192 | <code>self.messages.put(('error', str(exc)))</code> | Pass the shown frame or event/result tuple to a thread-safe queue for the main GUI thread. |
| 193 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 194 | <code>self.messages.put(('done', ''))</code> | Tell the GUI thread the worker has finished so it can re-enable controls. |
| 195 | <code>threading.Thread(target=run, daemon=True).start()</code> | Start the configured worker thread or session. |
| 197 | <code>def start_sender(self):</code> | Define App.start_sender(). Read and validate sender controls, then build/start a VideoSource and Sender in a worker. |
| 198 | <code>if self.sender and not self.sender.stop_event.is_set():</code> | Take this branch only when self.sender and (not self.sender.stop_event.is_set()) is true; indentation marks which statements belong to it. |
| 199 | <code>self.event('Sender already running. Join it here or on another computer.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 200 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 201 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 202 | <code>port = int(self.port.get())</code> | Read the TCP port entry and convert its text to an integer for validation. |
| 203 | <code>if not 1 &lt;= port &lt;= 65535:</code> | Take this branch only when not 1 &lt;= port &lt;= 65535 is true; indentation marks which statements belong to it. |
| 204 | <code>raise ValueError('Port must be 1–65535')</code> | Raise ValueError('Port must be 1–65535') to report failure to the caller. |
| 205 | <code>options = dict(path=self.video_path, width=int(self.width.get()), fps=int(self.fps.get()),</code> | Set options to a dictionary containing the named fields shown in this call. |
| 206 | <code>quality=int(self.quality.get()), loop=self.loop.get())</code> | Continue the statement beginning on line 205. Set options to a dictionary containing the named fields shown in this call. |
| 207 | <code>impairment = dict(loss=float(self.loss.get()), jitter_ms=float(self.jitter.get()))</code> | Read source artificial-loss probability and maximum-delay settings; existing sessions are unaffected. |
| 208 | <code>except ValueError as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 209 | <code>messagebox.showerror('Invalid settings', str(exc))</code> | Display the shown information/error dialog to the user. |
| 210 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 211 | <code>def task():</code> | Define App.start_sender.task(). Open the chosen source, start networking, and retain the sender unless the window was closed. |
| 212 | <code>source = VideoSource(**options)</code> | Set source to a video source configured from the selected options. |
| 213 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 214 | <code>sender = Sender(source, port=port, on_event=self.event, **impairment).start()</code> | Set sender to the result of Sender(source, port=port, on_event=self.event, **impairment).start(). |
| 215 | <code>except Exception:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 216 | <code>source.close()</code> | Close/release this socket, source, channel or output handle; consult the current function context for the resource. |
| 217 | <code>raise</code> | Raise the current exception again to report failure to the caller. |
| 218 | <code>if self.closed:</code> | Take this branch only when self.closed is true; indentation marks which statements belong to it. |
| 219 | <code>sender.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 220 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 221 | <code>self.sender = sender</code> | Set self.sender to sender; this holds the sender role held by this GUI instance. |
| 222 | <code>self.background(task)</code> | Schedule this task outside the Tk thread so network operations do not freeze the window. |
| 224 | <code>def start_receiver(self):</code> | Define App.start_receiver(). Read destination/buffer controls, choose a timestamped CSV path and connect in a worker. |
| 225 | <code>if self.receiver and not self.receiver.stop_event.is_set():</code> | Take this branch only when self.receiver and (not self.receiver.stop_event.is_set()) is true; indentation marks which statements belong to it. |
| 226 | <code>self.event('Already receiving a stream.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 227 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 228 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 229 | <code>host, port, buffer = self.host.get().strip(), int(self.port.get()), int(self.buffer.get())</code> | Set (host, port, buffer) to the values self.host.get().strip(), int(self.port.get()), int(self.buffer.get()). |
| 230 | <code>if not host or not 1 &lt;= port &lt;= 65535:</code> | Take this branch only when not host or not 1 &lt;= port &lt;= 65535 is true; indentation marks which statements belong to it. |
| 231 | <code>raise ValueError('Enter a sender IP and port 1–65535')</code> | Raise ValueError('Enter a sender IP and port 1–65535') to report failure to the caller. |
| 232 | <code>except ValueError as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 233 | <code>messagebox.showerror('Invalid settings', str(exc))</code> | Display the shown information/error dialog to the user. |
| 234 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 235 | <code>stamp = time.strftime('%Y%m%d-%H%M%S')</code> | Choose a wall-clock timestamp for this receiver CSV filename; not used in network timing calculations. |
| 236 | <code>def task():</code> | Define App.start_receiver.task(). Connect a receiver with frame/status callbacks and store it if the app is still open. |
| 237 | <code>receiver = Receiver(host, port, buffer_ms=buffer, on_frame=self.frame,</code> | Set receiver to the result of Receiver(host, port, buffer_ms=buffer, on_frame=self.frame, on_event=self.event, csv_path=f'captures/receiver-{stamp}.csv').start(). |
| 238 | <code>on_event=self.event, csv_path=f'captures/receiver-{stamp}.csv').start()</code> | Continue the statement beginning on line 237. Set receiver to the result of Receiver(host, port, buffer_ms=buffer, on_frame=self.frame, on_event=self.event, csv_path=f'captures/receiver-{stamp}.csv').start(). |
| 239 | <code>if self.closed:</code> | Take this branch only when self.closed is true; indentation marks which statements belong to it. |
| 240 | <code>receiver.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 241 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 242 | <code>self.receiver = receiver</code> | Set self.receiver to receiver; this holds the receiver role held by this GUI instance. |
| 243 | <code>self.background(task)</code> | Schedule this task outside the Tk thread so network operations do not freeze the window. |
| 245 | <code>def scan(self):</code> | Define App.scan(). Run sender discovery asynchronously. |
| 246 | <code>def task():</code> | Define App.scan.task(). Collect discovery results and queue them for the main thread. |
| 247 | <code>results = discover()</code> | Set results to the result of discover(). |
| 248 | <code>self.messages.put(('discovered', results))</code> | Pass the shown frame or event/result tuple to a thread-safe queue for the main GUI thread. |
| 249 | <code>self.background(task)</code> | Schedule this task outside the Tk thread so network operations do not freeze the window. |
| 251 | <code>def stop(self):</code> | Define App.stop(). Schedule shutdown of both roles in a background worker. |
| 252 | <code>def task():</code> | Define App.stop.task(). Stop the receiver and sender, then queue a completion status. |
| 253 | <code>if self.receiver:</code> | Take this branch only when self.receiver is true; indentation marks which statements belong to it. |
| 254 | <code>self.receiver.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 255 | <code>if self.sender:</code> | Take this branch only when self.sender is true; indentation marks which statements belong to it. |
| 256 | <code>self.sender.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 257 | <code>self.event('All sessions stopped.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 258 | <code>self.background(task)</code> | Schedule this task outside the Tk thread so network operations do not freeze the window. |
| 260 | <code>def tick(self):</code> | Define App.tick(). Process worker events, show the latest frame and schedule another GUI poll in 40 ms. |
| 261 | <code>if self.closed:</code> | Take this branch only when self.closed is true; indentation marks which statements belong to it. |
| 262 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 263 | <code>for _ in range(100):</code> | Loop over range(100), assigning each item to _. |
| 264 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 265 | <code>kind, value = self.messages.get_nowait()</code> | Set (kind, value) to the result of self.messages.get_nowait(). |
| 266 | <code>except queue.Empty:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 267 | <code>break</code> | Exit the nearest enclosing loop immediately. |
| 268 | <code>if kind == 'event':</code> | Take this branch only when kind == 'event' is true; indentation marks which statements belong to it. |
| 269 | <code>self.status.set(value)</code> | Update the linked Tk value or event state with the argument shown. |
| 270 | <code>self.log.configure(state='normal')</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 271 | <code>self.log.insert('end', f'{time.strftime("%H:%M:%S")}  {value}\n')</code> | Append a timestamped status message to the visible log. |
| 272 | <code>if int(self.log.index('end-1c').split('.')[0]) &gt; 200:</code> | Take this branch only when int(self.log.index('end-1c').split('.')[0]) &gt; 200 is true; indentation marks which statements belong to it. |
| 273 | <code>self.log.delete('1.0', '50.0')</code> | Remove the indicated old canvas objects, text lines or frame-buffer entry as shown. |
| 274 | <code>self.log.see('end')</code> | Scroll the log to its most recent entry. |
| 275 | <code>self.log.configure(state='disabled')</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 276 | <code>elif kind == 'error':</code> | If earlier branches did not match, test kind == 'error' and run this branch when true. |
| 277 | <code>self.status.set(value)</code> | Update the linked Tk value or event state with the argument shown. |
| 278 | <code>messagebox.showerror('LANStream', value)</code> | Display the shown information/error dialog to the user. |
| 279 | <code>elif kind == 'done':</code> | If earlier branches did not match, test kind == 'done' and run this branch when true. |
| 280 | <code>self.busy = False</code> | Set self.busy to False; this holds whether an asynchronous start/stop/discovery operation is in progress. |
| 281 | <code>for button in (self.send_button, self.receive_button, self.stop_button):</code> | Loop over (self.send_button, self.receive_button, self.stop_button), assigning each item to button. |
| 282 | <code>button.state(['!disabled'])</code> | Change the button state as shown; disabled blocks actions and !disabled restores them. |
| 283 | <code>elif kind == 'discovered':</code> | If earlier branches did not match, test kind == 'discovered' and run this branch when true. |
| 284 | <code>if value:</code> | Take this branch only when value is true; indentation marks which statements belong to it. |
| 285 | <code>self.host.set(value[0]['host'])</code> | Fill the destination IP from the first discovery result without automatically joining. |
| 286 | <code>self.port.set(str(value[0]['port']))</code> | Fill the TCP port from the first discovery result. |
| 287 | <code>self.event('Found: ' + ', '.join(f"{x['host']}:{x['port']} ({x.get('name', 'stream')})" for x in value))</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 288 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 289 | <code>self.event('No senders found. Enter the sender IP manually.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 290 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 291 | <code>self.last_jpeg = self.frames.get_nowait()</code> | Take the newest pending complete frame for this GUI refresh, if any. |
| 292 | <code>self.draw_frame()</code> | Decode and draw the latest received JPEG using the GUI thread. |
| 293 | <code>except queue.Empty:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 294 | <code>pass</code> | Do nothing for this handled condition; the enclosing loop/cleanup path decides what happens next. |
| 295 | <code>self.root.after(40, self.tick)</code> | Request the next GUI event/frame poll in 40 ms; Tk scheduling is approximate. |
| 297 | <code>def draw_frame(self):</code> | Define App.draw_frame(). Decode the received JPEG, fit it inside the playback canvas and display a retained Tk image. |
| 298 | <code>if not self.last_jpeg:</code> | Take this branch only when not self.last_jpeg is true; indentation marks which statements belong to it. |
| 299 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 300 | <code>from PIL import Image, ImageTk</code> | Import Image, ImageTk from PIL for Pillow image drawing, encoding and display. |
| 301 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 302 | <code>image = Image.open(io.BytesIO(self.last_jpeg))</code> | Decode the latest received JPEG from memory for GUI display. |
| 303 | <code>image.thumbnail((max(1, self.canvas.winfo_width()-4), max(1, self.canvas.winfo_height()-4)))</code> | Resize this image to fit the available canvas while preserving its aspect ratio. |
| 304 | <code>self.photo = ImageTk.PhotoImage(image)</code> | Convert to a Tk display image and retain a Python reference to keep it visible. |
| 305 | <code>self.canvas.delete('all')</code> | Remove the indicated old canvas objects, text lines or frame-buffer entry as shown. |
| 306 | <code>self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.photo)</code> | Draw the resized picture centered on the playback canvas. |
| 307 | <code>except (OSError, ValueError):</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 308 | <code>self.event('Could not decode a received frame.')</code> | Emit the shown human-readable session status; the GUI routes it through its event queue. |
| 310 | <code>def resize(self, _event):</code> | Define App.resize(). Redraw the image or recenter the placeholder when canvas geometry changes. |
| 311 | <code>if self.last_jpeg:</code> | Take this branch only when self.last_jpeg is true; indentation marks which statements belong to it. |
| 312 | <code>self.draw_frame()</code> | Decode and draw the latest received JPEG using the GUI thread. |
| 313 | <code>else:</code> | Run this alternative block when the preceding conditional branch was not taken. |
| 314 | <code>self.canvas.coords('placeholder', self.canvas.winfo_width()/2, self.canvas.winfo_height()/2)</code> | Move the canvas item to the shown updated coordinates. |
| 316 | <code>def update_stats(self):</code> | Define App.update_stats(). Refresh receiver cards/throughput history and sender peer totals, then reschedule after 500 ms. |
| 317 | <code>if self.closed:</code> | Take this branch only when self.closed is true; indentation marks which statements belong to it. |
| 318 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 319 | <code>if self.receiver:</code> | Take this branch only when self.receiver is true; indentation marks which statements belong to it. |
| 320 | <code>stats = self.receiver.metrics.snapshot()</code> | Set stats to a current copy of counters and computed statistics; this holds the current receiver report dictionary. |
| 321 | <code>for key, (widget, unit) in self.values.items():</code> | Loop over self.values.items(), assigning each item to (key, (widget, unit)). |
| 322 | <code>widget.configure(text=f'{stats[key]} {unit}')</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 323 | <code>self.detail.configure(text=f"{stats['frames']} frames played • {stats['dropped_frames']} incomplete • "</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 324 | <code>f"{stats['late_frames']} late • {stats['fps']} avg FPS • {stats['packets']} packets")</code> | Continue the statement beginning on line 323. Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 325 | <code>self.history.append(stats['throughput_mbps'])</code> | Append one sample of received one-second application throughput; this is the green chart data. |
| 326 | <code>self.history = self.history[-100:]</code> | Keep the most recent 100 samples, nominally about 50 seconds at 500 ms updates. History persists across sessions. |
| 327 | <code>self.chart.delete('all')</code> | Clear the previous chart drawing before rendering retained history at the current scale. |
| 328 | <code>w, h = self.chart.winfo_width(), 65</code> | Read current chart width and use the configured 65-pixel height for coordinate mapping. |
| 329 | <code>self.chart.create_text(10, 10, text='RECEIVE THROUGHPUT · LAST 50s', fill=MUTED, anchor='nw', font=('Helvetica', 8))</code> | Draw the shown caption/placeholder on a canvas with the specified position and style. |
| 330 | <code>if len(self.history) &gt; 1:</code> | Take this branch only when len(self.history) &gt; 1 is true; indentation marks which statements belong to it. |
| 331 | <code>scale = max(.1, max(self.history))</code> | Use the current history peak as vertical scale with a 0.1 Mb/s floor; absolute axis height can change. |
| 332 | <code>points = []</code> | Set points to an empty list; this holds the list of alternating chart x/y pixel coordinates. |
| 333 | <code>for i, value in enumerate(self.history):</code> | Loop over enumerate(self.history), assigning each item to (i, value). |
| 334 | <code>points.extend((i * (w-10) / 99 + 5, h-5-value/scale*(h-25)))</code> | Map sample index to horizontal position and relative throughput to inverted vertical pixels; larger rates appear higher. |
| 335 | <code>self.chart.create_line(*points, fill=GREEN, width=2)</code> | Connect throughput samples with a green polyline; there are no numeric axis ticks. |
| 336 | <code>if self.sender:</code> | Take this branch only when self.sender is true; indentation marks which statements belong to it. |
| 337 | <code>snapshot = self.sender.snapshot()</code> | Get outgoing totals and current peer reports separately from receiver-card metrics. |
| 338 | <code>peers = snapshot['peers']</code> | Set peers to snapshot['peers']. |
| 339 | <code>text = f"Connected receivers: {len(peers)}  •  Sent: {snapshot['packets']} packets  •  Simulated drops: {snapshot['simulated_drops']}"</code> | Set text to f"Connected receivers: {len(peers)}  •  Sent: {snapshot['packets']} packets  •  Simulated drops: {snapshot['simulated_drops']}". |
| 340 | <code>if peers:</code> | Take this branch only when peers is true; indentation marks which statements belong to it. |
| 341 | <code>text += '\n' + '  &#124;  '.join(f"{p['host']}:{p['port']}  loss {p['stats'].get('loss_pct', 0)}%" for p in peers[:3])</code> | Increase text by '\n' + '  &#124;  '.join((f"{p['host']}:{p['port']}  loss {p['stats'].get('loss_pct', 0)}%" for p in peers[:3])). |
| 342 | <code>self.peers.configure(text=text)</code> | Update the widget/window/style properties shown here; text changes refresh the visible display. |
| 343 | <code>self.root.after(500, self.update_stats)</code> | Request the next cards/chart/peer update in 500 ms, approximately two samples per second. |
| 345 | <code>def save_frame(self):</code> | Define App.save_frame(). Save the last received JPEG to a user-selected file. |
| 346 | <code>if not self.last_jpeg:</code> | Take this branch only when not self.last_jpeg is true; indentation marks which statements belong to it. |
| 347 | <code>messagebox.showinfo('Save frame', 'Join a stream first.')</code> | Display the shown information/error dialog to the user. |
| 348 | <code>return</code> | Exit this function now without a result; skip its remaining statements on this path. |
| 349 | <code>path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG image', '*.jpg')])</code> | Set path to the result of filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG image', '*.jpg')]). |
| 350 | <code>if path:</code> | Take this branch only when path is true; indentation marks which statements belong to it. |
| 351 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 352 | <code>Path(path).write_bytes(self.last_jpeg)</code> | Write the encoded JPEG bytes to the chosen output file. |
| 353 | <code>except OSError as exc:</code> | Handle only the exception type(s) listed here; run the following indented recovery/cleanup statements. |
| 354 | <code>messagebox.showerror('Save failed', str(exc))</code> | Display the shown information/error dialog to the user. |
| 356 | <code>def close(self):</code> | Define App.close(). Mark the app closed, destroy its window and stop remaining sessions. |
| 357 | <code>self.closed = True</code> | Set self.closed to True; this holds whether the GUI has been closed and periodic callbacks should stop. |
| 358 | <code>self.root.destroy()</code> | Destroy the Tk window and its child widgets. |
| 359 | <code>if self.receiver:</code> | Take this branch only when self.receiver is true; indentation marks which statements belong to it. |
| 360 | <code>self.receiver.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 361 | <code>if self.sender:</code> | Take this branch only when self.sender is true; indentation marks which statements belong to it. |
| 362 | <code>self.sender.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 364 | <code>def run(self):</code> | Define App.run(). Enter the Tk event loop so button and timer callbacks can execute. |
| 365 | <code>self.root.mainloop()</code> | Run the Tk event loop; timers, button actions and screen updates are handled here. |
| 368 | <code>def launch():</code> | Define launch(). Construct the desktop App and enter its event loop. |
| 369 | <code>App().run()</code> | Call App().run(); see the function summary above for its role in this stage. |

## experiments/run_local.py

Runs six actual loopback conditions and writes their measured statistics to a comparison CSV.

[Open source](../experiments/run_local.py)

### Function responsibilities

- **`main()`**, line 13: Parse experiment duration/output options, run each condition, then write the comparison CSV.

### Every nonblank source line

| Line | Actual source | Explanation |
|---:|---|---|
| 1 | <code>"""Run reproducible LANStream loss/jitter experiments on loopback.</code> | Documentation string describing this module/class/function; it is not a transmitted message. |
| 2 | <code>Usage: python -m experiments.run_local --seconds 6 --output captures/experiment.csv</code> | Continue the statement beginning on line 1. Documentation string describing this module/class/function; it is not a transmitted message. |
| 3 | <code>"""</code> | Continue the statement beginning on line 1. Documentation string describing this module/class/function; it is not a transmitted message. |
| 4 | <code>import argparse</code> | Import argparse for command-line options and subcommands. |
| 5 | <code>import csv</code> | Import csv for statistics CSV writing. |
| 6 | <code>import random</code> | Import random for artificial packet drop and delay choices. |
| 7 | <code>import time</code> | Import time for monotonic elapsed time and/or timestamped filenames. |
| 8 | <code>from pathlib import Path</code> | Import Path from pathlib for portable filesystem paths. |
| 9 | <code>from lanstream.media import VideoSource</code> | Import VideoSource from lanstream.media for project helpers used in this file. |
| 10 | <code>from lanstream.network import Sender, Receiver</code> | Import Sender, Receiver from lanstream.network for project helpers used in this file. |
| 13 | <code>def main():</code> | Define main(). Parse experiment duration/output options, run each condition, then write the comparison CSV. |
| 14 | <code>parser = argparse.ArgumentParser(description=__doc__)</code> | Set parser to a command-line argument parser with the shown description. |
| 15 | <code>parser.add_argument('--seconds', type=float, default=6)</code> | Register --seconds as an optional flag, converted using float, defaulting to 6.  |
| 16 | <code>parser.add_argument('--output', default='captures/experiment.csv')</code> | Register --output as an optional flag, defaulting to 'captures/experiment.csv'.  |
| 17 | <code>args = parser.parse_args()</code> | Set args to the parsed command-line options. |
| 18 | <code>rows = []</code> | Set rows to an empty list. |
| 19 | <code>for loss, jitter, buffer in [(0, 0, 120), (2, 0, 120), (5, 0, 120), (0, 80, 120), (0, 160, 40), (0, 160, 250)]:</code> | Run baseline, two loss levels, moderate jitter, then high jitter with short and long buffers. |
| 20 | <code>random.seed(42)</code> | Fix the artificial random-choice seed for comparison; thread and OS timing can still vary. |
| 21 | <code>sender = Sender(VideoSource(width=320, fps=15), host='127.0.0.1', port=0, loss=loss, jitter_ms=jitter)</code> | Set sender to the result of Sender(VideoSource(width=320, fps=15), host='127.0.0.1', port=0, loss=loss, jitter_ms=jitter). |
| 22 | <code>receiver = None</code> | Set receiver to None. |
| 23 | <code>try:</code> | Attempt this block; the following except/finally clauses handle failures and cleanup. |
| 24 | <code>sender.start()</code> | Start the configured worker thread or session. |
| 25 | <code>receiver = Receiver('127.0.0.1', sender.port, buffer_ms=buffer).start()</code> | Set receiver to the result of Receiver('127.0.0.1', sender.port, buffer_ms=buffer).start(). |
| 26 | <code>receiver.stop_event.wait(args.seconds)</code> | Let this condition run for the requested seconds, or end early if the receiver stops. |
| 27 | <code>stats = receiver.metrics.snapshot()</code> | Take the condition endpoint report while the stream is still active; some delayed packets can remain in flight. |
| 28 | <code>row = dict(configured_loss_pct=loss, max_jitter_ms=jitter, buffer_ms=buffer, **stats)</code> | Attach the experiment inputs to the observed receiver statistics for comparison. |
| 29 | <code>rows.append(row)</code> | Append the shown new entry to this list/deque for later processing or reporting. |
| 30 | <code>print(row, flush=True)</code> | Print the shown status/result to the terminal; flush=True makes it visible immediately. |
| 31 | <code>finally:</code> | Run the following cleanup block whether the try block succeeded, failed, or returned. |
| 32 | <code>if receiver:</code> | Take this branch only when receiver is true; indentation marks which statements belong to it. |
| 33 | <code>receiver.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 34 | <code>sender.stop()</code> | Request cleanup/shutdown of this sender or receiver role. |
| 35 | <code>path = Path(args.output)</code> | Set path to a portable Path object for the given filename. |
| 36 | <code>path.parent.mkdir(parents=True, exist_ok=True)</code> | Ensure the output directory exists, including parents when requested. |
| 37 | <code>with path.open('w', newline='') as handle:</code> | Enter path.open('w', newline='') as a managed resource, automatically exiting/closing it after this block. |
| 38 | <code>writer = csv.DictWriter(handle, fieldnames=list(rows[0]))</code> | Set writer to a CSV dictionary writer with columns in the shown order. |
| 39 | <code>writer.writeheader()</code> | Write the CSV column names once at the top of the file. |
| 40 | <code>writer.writerows(rows)</code> | Write all collected experiment rows to the CSV. |
| 41 | <code>print(f'Saved {path}')</code> | Print the shown status/result to the terminal; flush=True makes it visible immediately. |
| 44 | <code>if __name__ == '__main__':</code> | Run the following entry-point call only when this file/module is executed directly, not merely imported. |
| 45 | <code>main()</code> | Call main(); see the function summary above for its role in this stage. |

## Connect the files during a viva

1. Start at `main.py` and explain why it calls the package entry function.
2. Follow `App.start_sender()` to `VideoSource` and `Sender.start()`.
3. Follow `App.start_receiver()` to UDP bind, TCP JOIN and INFO.
4. Trace one JPEG through `VideoSource.read()` → `packetize()` → `Sender._stream()` → UDP → `unpack()`.
5. Trace the receiver through `Metrics.packet()` → `Assembler.add()/ready()` → `App.frame()/tick()/draw_frame()`.
6. Explain the independent path from `Metrics.snapshot()` to `App.update_stats()` and the throughput chart.
7. Point to the random drop condition, delayed-send heap, buffer deadline, and packet-gap formula when showing experiments.

If source code is edited later, line numbers and explanations in this document may need to be updated. This is a study reference, not an additional application runtime dependency.
