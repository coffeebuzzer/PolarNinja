import tkinter as tk

class WaveView(tk.Canvas):
    def __init__(self, master, **kw):
        # Provide safe defaults without colliding with caller overrides
        kw.setdefault("bg", "#0a0a0a")
        kw.setdefault("height", 80)
        kw.setdefault("highlightthickness", 0)
        super().__init__(master, **kw)
        self.values = []
        self.duration = 0.0
        self.pos_sec = 0.0
        self.bind("<Button-1>", self._seek_click)

    def load(self, values, duration):
        self.values = list(values)
        self.duration = float(duration)
        self.pos_sec = 0.0
        self.redraw()

    def set_pos(self, sec):
        self.pos_sec = max(0.0, min(self.duration, float(sec)))
        self.redraw()

    def _seek_click(self, ev):
        if self.duration <= 0:
            return
        x = ev.x / max(1, self.winfo_width())
        new_t = x * self.duration
        self.event_generate("<<WaveSeek>>", when="tail", data=str(new_t))

    def redraw(self):
        self.delete("all")
        w = self.winfo_width() or 600
        h = self.winfo_height() or 80
        mid = h // 2
        n = len(self.values)
        # Draw waveform in green bars
        if n > 1:
            for i, a in enumerate(self.values):
                x = int(i / (n - 1) * (w - 1))
                y = int(mid - a * (mid - 8))
                self.create_line(x, mid, x, y, fill="#27c24c")
        # Draw playhead
        if self.duration > 0:
            x = int((self.pos_sec / self.duration) * (w - 1))
            self.create_line(x, 0, x, h, fill="#66ff99")
