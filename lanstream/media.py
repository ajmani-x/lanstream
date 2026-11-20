"""JPEG video frames. Each frame is independently decodable after packet loss."""
import io
import math
import time


class VideoSource:
    def __init__(self, path=None, width=640, fps=20, quality=70, loop=False):
        if not 160 <= width <= 1920 or not 1 <= fps <= 60 or not 10 <= quality <= 95:
            raise ValueError('Width 160–1920, FPS 1–60, JPEG quality 10–95 required')
        self.path, self.width, self.fps, self.quality, self.loop = path, width, fps, quality, loop
        self.name = 'Animated demo' if not path else __import__('pathlib').Path(path).name
        self.capture = None
        if path:
            import cv2
            self.capture = cv2.VideoCapture(str(path))
            if not self.capture.isOpened():
                self.capture.release()
                raise ValueError('Cannot open video. Choose a supported MP4, AVI, MOV or MKV file.')
            self.native_fps = self.capture.get(cv2.CAP_PROP_FPS) or fps
        self.index = 0

    def read(self):
        from PIL import Image, ImageDraw
        if self.capture is not None:
            import cv2
            # Sample by presentation time to preserve file playback speed at target FPS.
            self.capture.set(cv2.CAP_PROP_POS_MSEC, self.index * 1000 / self.fps)
            ok, array = self.capture.read()
            if not ok and self.loop:
                self.index = 0
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, array = self.capture.read()
            if not ok:
                return None
            image = Image.fromarray(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))
            height = max(2, round(image.height * self.width / image.width))
            image = image.resize((self.width, height))
        else:
            w, h = self.width, round(self.width * 9 / 16)
            image = Image.new('RGB', (w, h), '#101e31')
            draw = ImageDraw.Draw(image)
            for x in range(0, w, 40):
                draw.line((x, 0, x, h), fill='#1c3048')
            for y in range(0, h, 40):
                draw.line((0, y, w, y), fill='#1c3048')
            phase = self.index / self.fps
            cx = int(w / 2 + math.sin(phase * 1.4) * w * .32)
            cy = int(h / 2 + math.cos(phase * 1.9) * h * .24)
            draw.ellipse((cx-24, cy-24, cx+24, cy+24), fill='#31dfb6')
            draw.text((20, 20), 'LANSTREAM / LIVE NETWORK DEMO', fill='white')
            draw.text((20, h-40), f'Frame {self.index:06d}   |   {phase:07.2f}s   |   {self.fps} FPS', fill='#90b4d6')
        self.index += 1
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=self.quality)
        return output.getvalue()

    def close(self):
        if self.capture:
            self.capture.release()
