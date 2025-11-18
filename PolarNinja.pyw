import tkinter as tk
from tkinter import ttk, messagebox
import os
from modules.settings import load_settings, save_settings
from modules.dmx_engine import DMXEngine
from modules.ui_topbar_online import TopBar
from util.wave_assets import load_waveform, load_beats
from ui.wave_view import WaveView
from modes.rockin_modes import RockinModes
from ui.style_classic import apply_classic

APP_TITLE = "Polar Ninja - Beta .03"

ASSETS = {
    "19": ("CUE_19_-_UNLOADING_waveform.json", None),
    "20": ("CUE_20_-_HEAD_ELF_SCENE_waveform.json", None),
    "21": ("CUE_21_-_ROCKIN_waveform.json", "CUE_21_-_ROCKIN_beats.json"),
}

class DotBar(ttk.Frame):
    def __init__(self, master, count=38):
        super().__init__(master, style="Panel.TFrame")
        self.count = count
        self.c = tk.Canvas(self, height=50, bg="#111111", highlightthickness=0, bd=0); self.c.pack(fill="x")
        self._layout()
    def _layout(self):
        self.c.delete("all")
        w = max(self.c.winfo_width(), 900)
        pad = 18
        spacing = (w - 2*pad) / (self.count-1)
        self.oval_ids = []
        for i in range(self.count):
            x = pad + i*spacing
            oid = self.c.create_oval(x-10,25-10,x+10,25+10, outline="#888", width=1, fill="#000")
            self.oval_ids.append(oid)
    def set_colors(self, rgbs):
        for oid, rgb in zip(self.oval_ids, rgbs):
            self.c.itemconfig(oid, fill="#%02x%02x%02x" % rgb)

class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        style = apply_classic(root)

        self.cfg = load_settings()

        # ===== TOP BAR: title (left), Online/Offline + DMX dot (right)
        top = ttk.Frame(root); top.pack(fill="x", padx=14, pady=(10,8))
        ttk.Label(top, text="Polar Ninja — Beta .03", font=("Segoe UI", 13, "bold")).pack(side="left")
        def on_toggle_online(is_online: bool):
            self.cfg["online_mode"] = bool(is_online); save_settings(self.cfg); self.dmx.set_online(bool(is_online))
        self.topbar = TopBar(top, on_toggle_online); self.topbar.pack(side="right")

        # DMX engine
        self.dmx = DMXEngine(self.cfg.get("dmx_com_port", 11), status_callback=self.topbar.set_status)
        self.topbar.online_var.set(self.cfg.get("online_mode", True)); on_toggle_online(self.cfg.get("online_mode", True))
        self.dmx.start()

        # ===== MAIN PANEL
        body = ttk.Frame(root, style="Panel.TFrame"); body.pack(fill="both", expand=True, padx=14, pady=12)

        # Row 1: Cue buttons (left) + Reset (right)
        row1 = ttk.Frame(body, style="Panel.TFrame"); row1.pack(fill="x")
        self.btn19 = ttk.Button(row1, text="CUE 19", style="Cue.TButton", command=lambda: self.start_cue("19"))
        self.btn20 = ttk.Button(row1, text="CUE 20", style="Cue.TButton", command=lambda: self.start_cue("20"))
        self.btn21 = ttk.Button(row1, text="CUE 21", style="Cue.TButton", command=lambda: self.start_cue("21"))
        for b in (self.btn19, self.btn20, self.btn21):
            b.pack(side="left", padx=(0,10))
        self.reset_btn = ttk.Button(row1, text="RESET", style="Reset.TButton", command=self.stop)
        self.reset_btn.pack(side="right")

        # Row 2: Rockin selector (below CUE row, left aligned)
        row2 = ttk.Frame(body, style="Panel.TFrame"); row2.pack(fill="x", pady=(6,0))
        from ui.rockin_selector import RockinSelector
        self.rockin = RockinModes(fixture_count=38)
        ttk.Label(row2, text="Rockin shows:", style="Muted.TLabel").pack(side="left", padx=(0,8))
        self.selector = RockinSelector(row2, on_select=self.rockin.set_mode)
        self.selector.pack(side="left")

        # Row 3: Waveform (taller)
        self.wave = WaveView(body, height=110); self.wave.pack(fill="x", pady=(10,6))
        self.wave.bind("<<WaveSeek>>", self.on_seek)

        # Row 4: Transport
        row4 = ttk.Frame(body, style="Panel.TFrame"); row4.pack(fill="x")
        self.play_btn = ttk.Button(row4, text="▶  Play", style="Transport.TButton", command=self.play)
        self.pause_btn = ttk.Button(row4, text="⏸  Pause", style="Transport.TButton", command=self.pause)
        self.stop_btn = ttk.Button(row4, text="⏹  Stop", style="Transport.TButton", command=self.stop)
        for b in (self.play_btn, self.pause_btn, self.stop_btn):
            b.pack(side="left", padx=(0,10))

        # Row 5: Dots (straight line)
        self.dots = DotBar(body, count=38); self.dots.pack(fill="x", pady=(10,4))

        # State
        self.current_cue = None
        self.duration = 0.0
        self.values = []
        self.pos_ms = 0
        self.playing = False
        self.beats = {"tempo_bpm":0.0, "beats_sec":[]}

        # Default
        self.start_cue("19", auto_play=False)
        self.root.after(300, self.dots._layout)

    def on_seek(self, ev):
        try: sec = float(ev.data)
        except Exception: return
        self.pos_ms = int(sec*1000); self.wave.set_pos(self.pos_ms/1000.0)

    def start_cue(self, cue, auto_play=True):
        self.current_cue = cue
        assets_dir = self.cfg.get("assets_dir", "C:\\\\polarexpressninja\\\\polar_waveforms\\\\")
        wf_name, beats_name = ASSETS[cue]
        wf_json = os.path.join(assets_dir, wf_name)
        wf_csv  = wf_json.replace(".json",".csv")
        path = wf_json if os.path.exists(wf_json) else wf_csv
        if not os.path.exists(path):
            messagebox.showerror("Waveform missing", f"Cannot find waveform: {wf_json} or {wf_csv}")
            return
        wf = load_waveform(path); self.duration = float(wf["duration"]); self.values = list(wf["values"])
        self.wave.load(self.values, self.duration); self.pos_ms = 0
        if cue == "21" and beats_name:
            bpath = os.path.join(assets_dir, beats_name)
            self.beats = load_beats(bpath) if os.path.exists(bpath) else {"tempo_bpm":0.0, "beats_sec":[]}
        else:
            self.beats = {"tempo_bpm":0.0, "beats_sec":[]}
        if auto_play: self.play()

    def play(self):
        self.playing = True
        self._tick()

    def pause(self):
        self.playing = False

    def stop(self):
        self.playing = False
        self.pos_ms = 0
        self.wave.set_pos(0.0)
        self.rockin.finish_all_white_low()
        self.dots.set_colors(self.rockin.current_fixture_colors())

    def _tick(self):
        if not self.playing: return
        self.pos_ms += 33
        if self.pos_ms/1000.0 > self.duration:
            if self.current_cue == "21":
                self.rockin.finish_all_white_low()
                self.dots.set_colors(self.rockin.current_fixture_colors())
            self.playing = False
            return

        if self.current_cue == "21" and self.beats["beats_sec"]:
            now = self.pos_ms/1000.0; prev = (self.pos_ms-33)/1000.0
            for i, bt in enumerate(self.beats["beats_sec"]):
                if prev < bt <= now: self.rockin.on_beat(i, bt)

        if self.current_cue == "19":
            import math; t = self.pos_ms/1000.0; x = (math.sin(t*0.8)+1)/2
            cols = [(int(255*x), int(255*(1-x)), 0) if i%2==0 else (int(255*(1-x)), int(255*x), 0) for i in range(38)]
            self.dots.set_colors(cols)
        elif self.current_cue == "20":
            side = int((self.pos_ms//700)%2)
            cols = [(255,0,0) if side==0 else (0,255,0)]*19 + [(0,255,0) if side==0 else (255,0,0)]*19
            self.dots.set_colors(cols)
        else:
            self.dots.set_colors(self.rockin.current_fixture_colors())

        self.wave.set_pos(self.pos_ms/1000.0)
        self.root.after(33, self._tick)

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
