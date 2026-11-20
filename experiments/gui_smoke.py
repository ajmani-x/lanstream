"""Open the desktop app, exercise start/join/render/stop, then close it.
Run manually on a machine with a graphical desktop:
    python -m experiments.gui_smoke
"""
import sys
import time
import traceback
from lanstream.gui import App


def main():
    app = App()
    started = time.monotonic()
    phase = 'sender'
    failed = []
    app.port.set('15900')

    def check():
        nonlocal phase
        try:
            if time.monotonic() - started > 20:
                raise AssertionError(f'GUI timed out during {phase}')
            if app.busy:
                app.root.after(100, check)
                return
            if phase == 'sender':
                app.start_sender()
                phase = 'join'
            elif phase == 'join':
                assert app.sender is not None, 'Sender failed to start'
                app.start_receiver()
                phase = 'render'
            elif phase == 'render':
                assert app.receiver is not None, 'Receiver failed to join'
                if app.receiver.metrics.snapshot()['frames'] >= 8 and app.photo is not None:
                    app.root.update_idletasks()
                    for button in (app.send_button, app.receive_button, app.stop_button):
                        bottom = button.winfo_rooty() + button.winfo_height()
                        root_bottom = app.root.winfo_rooty() + app.root.winfo_height()
                        assert bottom < root_bottom - 40, f'Clipped button: {button.cget("text")}'
                    print('GUI PASS: sender, receiver, JPEG rendering, controls, and live stats', flush=True)
                    app.stop()
                    phase = 'stop'
            elif phase == 'stop':
                assert app.sender.stop_event.is_set()
                assert app.receiver.stop_event.is_set()
                app.close()
                return
            app.root.after(100, check)
        except Exception:
            failed.append(traceback.format_exc())
            app.close()

    app.root.after(200, check)
    app.run()
    if failed:
        print(failed[0], file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
