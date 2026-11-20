"""Tk desktop dashboard; network and decode work stay off the UI thread."""
import io
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from .media import VideoSource
from .network import Sender, Receiver, discover, local_ip

BG = '#0b1220'
PANEL = '#142035'
TEXT = '#e7effc'
MUTED = '#8fa4bf'
GREEN = '#39dcb1'


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('LANStream • Computer Networks Lab')
        self.root.geometry('1220x850')
        self.root.minsize(1000, 760)
        self.root.configure(bg=BG)
        self.sender = self.receiver = None
        self.busy = False
        self.closed = False
        self.messages = queue.Queue(maxsize=200)
        self.frames = queue.Queue(maxsize=1)
        self.photo = None
        self.last_jpeg = None
        self.history = []
        self.status = tk.StringVar(value='Ready to connect')
        self.file = tk.StringVar(value='Animated demo (no video file needed)')
        self.host = tk.StringVar(value='127.0.0.1')
        self.port = tk.StringVar(value='5000')
        self.fps = tk.StringVar(value='20')
        self.quality = tk.StringVar(value='70')
        self.width = tk.StringVar(value='640')
        self.loss = tk.StringVar(value='0')
        self.jitter = tk.StringVar(value='0')
        self.buffer = tk.StringVar(value='120')
        self.loop = tk.BooleanVar(value=True)
        self.video_path = None
        self._style()
        self._layout()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.after(40, self.tick)
        self.root.after(500, self.update_stats)

    def _style(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('.', background=BG, foreground=TEXT, font=('Helvetica', 11))
        style.configure('TFrame', background=BG)
        style.configure('Card.TFrame', background=PANEL)
        style.configure('TLabel', background=BG, foreground=TEXT)
        style.configure('Muted.TLabel', foreground=MUTED)
        style.configure('TButton', background='#253b58', foreground=TEXT, padding=(12, 9), borderwidth=0)
        style.map('TButton', background=[('active', '#345170'), ('disabled', '#182438')])
        style.configure('Accent.TButton', background='#146f62', foreground='white')
        style.configure('TEntry', fieldbackground='#1c2c43', foreground=TEXT, insertcolor=TEXT, padding=6)
        style.configure('TCheckbutton', background=BG, foreground=TEXT)
        style.map('TCheckbutton', background=[('active', BG)])
        style.configure('TCombobox', fieldbackground='#1c2c43', foreground=TEXT, padding=5)

    def label(self, parent, text, size=11, color=TEXT, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                        font=('Helvetica', size), **kwargs)

    def _layout(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill='x', padx=26, pady=(22, 14))
        self.label(header, '◉  LANStream', 25, GREEN).pack(side='left')
        self.label(header, 'PEER-TO-PEER VIDEO  /  NETWORK LAB', 10, MUTED).pack(side='left', padx=25)
        self.label(header, f'Local IP  {local_ip()}', 11, MUTED).pack(side='right')
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill='both', expand=True, padx=26)
        sidebar = tk.Frame(body, bg=BG, width=300)
        sidebar.pack(side='left', fill='y', padx=(0, 20))
        sidebar.pack_propagate(False)
        main = tk.Frame(body, bg=BG)
        main.pack(side='left', fill='both', expand=True)
        self.label(sidebar, '01   SOURCE & SESSION', 11, GREEN).pack(anchor='w', pady=(0, 10))
        self.label(sidebar, 'Video source', 10, MUTED).pack(anchor='w')
        self.source_label = tk.Label(sidebar, textvariable=self.file, bg=BG, fg=TEXT,
                                     wraplength=290, justify='left', font=('Helvetica', 11))
        self.source_label.pack(anchor='w', pady=7)
        row = ttk.Frame(sidebar)
        row.pack(fill='x')
        ttk.Button(row, text='Choose video', command=self.choose).pack(side='left')
        ttk.Button(row, text='Use demo', command=self.demo).pack(side='left', padx=7)
        ttk.Checkbutton(sidebar, text='Loop video', variable=self.loop).pack(anchor='w', pady=8)
        self.field(sidebar, 'Sender IP / hostname', self.host)
        self.field(sidebar, 'TCP control port', self.port)
        ttk.Button(sidebar, text='Discover LAN senders', command=self.scan).pack(fill='x', pady=7)
        self.label(sidebar, '02   MEDIA & NETWORK', 11, GREEN).pack(anchor='w', pady=(16, 8))
        grid = tk.Frame(sidebar, bg=BG)
        grid.pack(fill='x')
        settings = [('FPS', self.fps), ('Width (px)', self.width), ('JPEG quality', self.quality),
                    ('Loss (%)', self.loss), ('Jitter (ms)', self.jitter), ('Buffer (ms)', self.buffer)]
        for i, (name, var) in enumerate(settings):
            cell = tk.Frame(grid, bg=BG)
            cell.grid(row=i//2, column=i%2, sticky='ew', padx=(0, 10), pady=4)
            self.label(cell, name, 10, MUTED).pack(anchor='w')
            ttk.Entry(cell, textvariable=var, width=11).pack(fill='x', pady=3)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        self.label(sidebar, 'Loss/jitter apply at sender; buffer at receiver.\nSettings apply when starting a new session.', 9, MUTED,
                   justify='left').pack(anchor='w', pady=8)
        self.send_button = ttk.Button(sidebar, text='Start sender', style='Accent.TButton', command=self.start_sender)
        self.send_button.pack(fill='x', pady=(7, 4))
        self.receive_button = ttk.Button(sidebar, text='Join stream', style='Accent.TButton', command=self.start_receiver)
        self.receive_button.pack(fill='x', pady=4)
        self.stop_button = ttk.Button(sidebar, text='Stop all sessions', command=self.stop)
        self.stop_button.pack(fill='x', pady=4)
        self.label(main, 'LIVE PLAYBACK', 10, MUTED).pack(anchor='w')
        self.canvas = tk.Canvas(main, bg='#070c15', highlightthickness=1, highlightbackground='#253650', height=325)
        self.canvas.pack(fill='both', expand=True, pady=(8, 12))
        self.canvas.create_text(300, 150, text='Your stream will appear here\nStart a sender, then join its IP address.',
                                fill=MUTED, font=('Helvetica', 14), justify='center', tags='placeholder')
        self.canvas.bind('<Configure>', self.resize)
        cards = tk.Frame(main, bg=BG)
        cards.pack(fill='x')
        self.values = {}
        for i, (key, title, unit) in enumerate([('throughput_mbps', 'THROUGHPUT', 'Mb/s'), ('loss_pct', 'PACKET LOSS', '%'),
                                               ('jitter_ms', 'JITTER', 'ms'), ('rtt_ms', 'CONTROL RTT', 'ms')]):
            card = tk.Frame(cards, bg=PANEL, padx=12, pady=10)
            card.grid(row=0, column=i, sticky='ew', padx=(0, 7))
            cards.columnconfigure(i, weight=1)
            self.label(card, title, 9, MUTED).pack(anchor='w')
            value = self.label(card, f'0 {unit}', 19, GREEN)
            value.pack(anchor='w', pady=(6, 0))
            self.values[key] = (value, unit)
        self.detail = self.label(main, 'No active session • JPEG video over UDP • TCP signalling', 10, MUTED)
        self.detail.pack(anchor='w', pady=(10, 6))
        self.chart = tk.Canvas(main, height=65, bg=PANEL, highlightthickness=0)
        self.chart.pack(fill='x', pady=(0, 8))
        self.peers = self.label(main, 'Connected receivers: 0', 10, MUTED, anchor='w', justify='left')
        self.peers.pack(fill='x', pady=3)
        self.log = tk.Text(main, height=5, bg='#0e1929', fg=MUTED, font=('Courier', 10),
                           relief='flat', state='disabled', wrap='word')
        self.log.pack(fill='x', pady=(5, 0))
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill='x', padx=26, pady=12)
        tk.Label(footer, textvariable=self.status, bg=BG, fg=GREEN, font=('Helvetica', 10)).pack(side='left')
        ttk.Button(footer, text='Save current frame', command=self.save_frame).pack(side='right')
        self.label(footer, 'CSV reports saved to captures/', 10, MUTED).pack(side='right', padx=16)

    def field(self, parent, label, variable):
        self.label(parent, label, 10, MUTED).pack(anchor='w', pady=(7, 3))
        ttk.Entry(parent, textvariable=variable).pack(fill='x')

    def choose(self):
        path = filedialog.askopenfilename(filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv *.webm'), ('All files', '*')])
        if path:
            self.video_path = path
            self.file.set(Path(path).name)

    def demo(self):
        self.video_path = None
        self.file.set('Animated demo (no video file needed)')

    def event(self, message):
        try:
            self.messages.put_nowait(('event', str(message)))
        except queue.Full:
            pass

    def frame(self, jpeg):
        try:
            self.frames.get_nowait()
        except queue.Empty:
            pass
        try:
            self.frames.put_nowait(jpeg)
        except queue.Full:
            pass

    def background(self, task):
        if self.busy:
            return
        self.busy = True
        self.send_button.state(['disabled'])
        self.receive_button.state(['disabled'])
        self.stop_button.state(['disabled'])
        def run():
            try:
                task()
            except Exception as exc:
                self.messages.put(('error', str(exc)))
            finally:
                self.messages.put(('done', ''))
        threading.Thread(target=run, daemon=True).start()

    def start_sender(self):
        if self.sender and not self.sender.stop_event.is_set():
            self.event('Sender already running. Join it here or on another computer.')
            return
        try:
            port = int(self.port.get())
            if not 1 <= port <= 65535:
                raise ValueError('Port must be 1–65535')
            options = dict(path=self.video_path, width=int(self.width.get()), fps=int(self.fps.get()),
                           quality=int(self.quality.get()), loop=self.loop.get())
            impairment = dict(loss=float(self.loss.get()), jitter_ms=float(self.jitter.get()))
        except ValueError as exc:
            messagebox.showerror('Invalid settings', str(exc))
            return
        def task():
            source = VideoSource(**options)
            try:
                sender = Sender(source, port=port, on_event=self.event, **impairment).start()
            except Exception:
                source.close()
                raise
            if self.closed:
                sender.stop()
            else:
                self.sender = sender
        self.background(task)

    def start_receiver(self):
        if self.receiver and not self.receiver.stop_event.is_set():
            self.event('Already receiving a stream.')
            return
        try:
            host, port, buffer = self.host.get().strip(), int(self.port.get()), int(self.buffer.get())
            if not host or not 1 <= port <= 65535:
                raise ValueError('Enter a sender IP and port 1–65535')
        except ValueError as exc:
            messagebox.showerror('Invalid settings', str(exc))
            return
        stamp = time.strftime('%Y%m%d-%H%M%S')
        def task():
            receiver = Receiver(host, port, buffer_ms=buffer, on_frame=self.frame,
                                on_event=self.event, csv_path=f'captures/receiver-{stamp}.csv').start()
            if self.closed:
                receiver.stop()
            else:
                self.receiver = receiver
        self.background(task)

    def scan(self):
        def task():
            results = discover()
            self.messages.put(('discovered', results))
        self.background(task)

    def stop(self):
        def task():
            if self.receiver:
                self.receiver.stop()
            if self.sender:
                self.sender.stop()
            self.event('All sessions stopped.')
        self.background(task)

    def tick(self):
        if self.closed:
            return
        for _ in range(100):
            try:
                kind, value = self.messages.get_nowait()
            except queue.Empty:
                break
            if kind == 'event':
                self.status.set(value)
                self.log.configure(state='normal')
                self.log.insert('end', f'{time.strftime("%H:%M:%S")}  {value}\n')
                if int(self.log.index('end-1c').split('.')[0]) > 200:
                    self.log.delete('1.0', '50.0')
                self.log.see('end')
                self.log.configure(state='disabled')
            elif kind == 'error':
                self.status.set(value)
                messagebox.showerror('LANStream', value)
            elif kind == 'done':
                self.busy = False
                for button in (self.send_button, self.receive_button, self.stop_button):
                    button.state(['!disabled'])
            elif kind == 'discovered':
                if value:
                    self.host.set(value[0]['host'])
                    self.port.set(str(value[0]['port']))
                    self.event('Found: ' + ', '.join(f"{x['host']}:{x['port']} ({x.get('name', 'stream')})" for x in value))
                else:
                    self.event('No senders found. Enter the sender IP manually.')
        try:
            self.last_jpeg = self.frames.get_nowait()
            self.draw_frame()
        except queue.Empty:
            pass
        self.root.after(40, self.tick)

    def draw_frame(self):
        if not self.last_jpeg:
            return
        from PIL import Image, ImageTk
        try:
            image = Image.open(io.BytesIO(self.last_jpeg))
            image.thumbnail((max(1, self.canvas.winfo_width()-4), max(1, self.canvas.winfo_height()-4)))
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.delete('all')
            self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.photo)
        except (OSError, ValueError):
            self.event('Could not decode a received frame.')

    def resize(self, _event):
        if self.last_jpeg:
            self.draw_frame()
        else:
            self.canvas.coords('placeholder', self.canvas.winfo_width()/2, self.canvas.winfo_height()/2)

    def update_stats(self):
        if self.closed:
            return
        if self.receiver:
            stats = self.receiver.metrics.snapshot()
            for key, (widget, unit) in self.values.items():
                widget.configure(text=f'{stats[key]} {unit}')
            self.detail.configure(text=f"{stats['frames']} frames played • {stats['dropped_frames']} incomplete • "
                                  f"{stats['late_frames']} late • {stats['fps']} avg FPS • {stats['packets']} packets")
            self.history.append(stats['throughput_mbps'])
            self.history = self.history[-100:]
            self.chart.delete('all')
            w, h = self.chart.winfo_width(), 65
            self.chart.create_text(10, 10, text='RECEIVE THROUGHPUT · LAST 50s', fill=MUTED, anchor='nw', font=('Helvetica', 8))
            if len(self.history) > 1:
                scale = max(.1, max(self.history))
                points = []
                for i, value in enumerate(self.history):
                    points.extend((i * (w-10) / 99 + 5, h-5-value/scale*(h-25)))
                self.chart.create_line(*points, fill=GREEN, width=2)
        if self.sender:
            snapshot = self.sender.snapshot()
            peers = snapshot['peers']
            text = f"Connected receivers: {len(peers)}  •  Sent: {snapshot['packets']} packets  •  Simulated drops: {snapshot['simulated_drops']}"
            if peers:
                text += '\n' + '  |  '.join(f"{p['host']}:{p['port']}  loss {p['stats'].get('loss_pct', 0)}%" for p in peers[:3])
            self.peers.configure(text=text)
        self.root.after(500, self.update_stats)

    def save_frame(self):
        if not self.last_jpeg:
            messagebox.showinfo('Save frame', 'Join a stream first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG image', '*.jpg')])
        if path:
            try:
                Path(path).write_bytes(self.last_jpeg)
            except OSError as exc:
                messagebox.showerror('Save failed', str(exc))

    def close(self):
        self.closed = True
        self.root.destroy()
        if self.receiver:
            self.receiver.stop()
        if self.sender:
            self.sender.stop()

    def run(self):
        self.root.mainloop()


def launch():
    App().run()
