import argparse
import json
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='LANStream: peer-to-peer LAN video and network analysis')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('gui', help='Launch the desktop dashboard (default)')
    sub.add_parser('discover', help='Find active LAN senders')
    send = sub.add_parser('send', help='Stream JPEG video over UDP')
    send.add_argument('--file', help='Video path; omit for an animated demo')
    send.add_argument('--bind', default='0.0.0.0')
    send.add_argument('--port', type=int, default=5000)
    send.add_argument('--fps', type=int, default=20)
    send.add_argument('--width', type=int, default=640)
    send.add_argument('--quality', type=int, default=70)
    send.add_argument('--loop', action='store_true')
    send.add_argument('--loss', type=float, default=0, help='Simulated packet loss percent')
    send.add_argument('--jitter', type=float, default=0, help='Maximum random packet delay in ms')
    send.add_argument('--duration', type=float, default=0)
    receive = sub.add_parser('receive', help='Join a stream; GUI is optional')
    receive.add_argument('host')
    receive.add_argument('--port', type=int, default=5000)
    receive.add_argument('--buffer', type=int, default=120, help='Playout buffer in ms')
    receive.add_argument('--csv', default='captures/receiver.csv')
    receive.add_argument('--save-frames', help='Optional directory for received JPEG frames')
    receive.add_argument('--duration', type=float, default=0)
    args = parser.parse_args()
    if args.command in (None, 'gui'):
        from .gui import launch
        launch()
        return
    from .network import Sender, Receiver, discover
    if args.command == 'discover':
        print(json.dumps(discover(), indent=2))
        return
    session = None
    try:
        if args.command == 'send':
            from .media import VideoSource
            source = VideoSource(args.file, args.width, args.fps, args.quality, args.loop)
            session = Sender(source, args.bind, args.port, args.loss, args.jitter, print)
            session.start()
        else:
            count = 0
            def frame(jpeg):
                nonlocal count
                if args.save_frames:
                    directory = Path(args.save_frames)
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / f'frame-{count:06d}.jpg').write_bytes(jpeg)
                count += 1
            session = Receiver(args.host, args.port, args.buffer, frame, print, args.csv)
            session.start()
        started = time.monotonic()
        while not session.stop_event.wait(1):
            stats = session.snapshot() if args.command == 'send' else session.metrics.snapshot()
            print(json.dumps(stats), flush=True)
            if args.duration > 0 and time.monotonic() - started >= args.duration:
                break
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError, ImportError) as exc:
        parser.exit(1, f'LANStream: {exc}\n')
    finally:
        if session:
            session.stop()


if __name__ == '__main__':
    main()
