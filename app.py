from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
import sys, os, json, math

from modules.settings import load_settings
from modules.dmx_engine import DMXEngine
from modules.audio import AudioEngine
from modules.rockin_modes import RockinModes
from ui.widgets import CircleButton, SeekBar
from ui.dots import DotBar


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Polar Ninja - Beta .08-1 - Designed by Dustin")
        self.setStyleSheet(
            "QWidget{background:#000;color:#fff;}"
            "QLabel{color:#fff;}"
        )

        # ---- Core engines / config ----
        self.cfg = load_settings()

        self.audio = AudioEngine()
        if hasattr(self.audio, "set_assets_dir"):
            self.audio.set_assets_dir(self.cfg.get("assets_dir"))

        # Pre-warm core cue sounds so overlays don't glitch when we hit CUE 20
        for cid in ("19", "20", "21"):
            path = self.cfg["songs"].get(cid)
            if path and os.path.exists(path):
                self.audio.warm_sound(path)

        # DMX engine + status callback
        dmx_port = self.cfg.get("dmx_com_port", 11)
        self.dmx = DMXEngine(dmx_port, status_cb=self._set_dmx_status)
        self.dmx.start()

        self.rockin = RockinModes(38)
        self.rockin.set_mode(1)
        self.beats = []
        self.last_beat_index = -1

        # For smooth fade to white at end of CUE 20
        self.white_fade_t0 = None
        self.white_fade_dur = 3.0  # seconds
        self.white_target = (240, 240, 240)

        # For CUE 21 "All White Low Power" hold-to-reset
        self.c21_hold_white = False

        # Track cue state so we know when we’re doing 19 -> 20
        self.current_cue = None
        self.prev_cue = None

        # ------------------------------------------------------------------
        # TOP BAR: title + DMX status
        # ------------------------------------------------------------------
        top = QHBoxLayout()

        title = QLabel("Polar Ninja - Beta .08-1 - Designed by Dustin")
        title.setFont(QFont("Segoe UI", 12))
        top.addWidget(title)
        top.addStretch(1)

        self.dmx_label = QLabel("DMX")
        self.dmx_label.setStyleSheet("color:#ffffff; font-size:11px;")
        top.addWidget(self.dmx_label)

        self.dmx_dot = QLabel("●")
        self.dmx_dot.setStyleSheet("color:#aa0000; font-size:18px;")
        top.addWidget(self.dmx_dot)

        self.dmx.set_online(True)

        # ------------------------------------------------------------------
        # CUE BUTTON ROW
        # ------------------------------------------------------------------
        cue_row_widget = QWidget()
        cues = QHBoxLayout(cue_row_widget)
        cues.setContentsMargins(0, 8, 0, 8)
        cues.setSpacing(10)

        self.c19 = QPushButton("CUE 19 - UNLOADING")
        self.c20 = QPushButton("CUE 20 - HEAD ELF")
        self.c21 = QPushButton("CUE 21 - ROCKIN")

        for b in (self.c19, self.c20, self.c21):
            b.setMinimumHeight(56)
            b.setStyleSheet(
                "QPushButton{color:#fff;background:transparent;"
                "border:2px solid #aaa;padding:10px;}"
                "QPushButton:pressed{background:#222}"
            )

        self.c19.clicked.connect(lambda: self.load_cue("19", auto_play=True))
        self.c20.clicked.connect(lambda: self.load_cue("20", auto_play=True))
        self.c21.clicked.connect(lambda: self.load_cue("21", auto_play=True))

        cues.addWidget(self.c19)
        cues.addWidget(self.c20)
        cues.addWidget(self.c21)

        # ------------------------------------------------------------------
        # SEEK BAR + TIME LABELS
        # ------------------------------------------------------------------
        self.seek = SeekBar()
        self.seek.seek.connect(self._on_seek_ratio)

        trow = QHBoxLayout()
        self.lbl_l = QLabel("00:00")
        self.lbl_r = QLabel("00:00")
        trow.addWidget(self.lbl_l)
        trow.addStretch(1)
        trow.addWidget(self.lbl_r)

        # ------------------------------------------------------------------
        # TRANSPORT BUTTONS
        # ------------------------------------------------------------------
        trans = QHBoxLayout()
        self.btn_play = CircleButton("play", "Play")
        self.btn_pause = CircleButton("pause", "Pause")
        self.btn_stop = CircleButton("stop", "Stop")

        for btn in (self.btn_play, self.btn_pause, self.btn_stop):
            btn.setFixedSize(90, 90)

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)

        trans.addStretch(1)
        trans.addWidget(self.btn_play)
        trans.addSpacing(40)
        trans.addWidget(self.btn_pause)
        trans.addSpacing(40)
        trans.addWidget(self.btn_stop)
        trans.addStretch(1)

        # ------------------------------------------------------------------
        # DOT BAR + RESET
        # ------------------------------------------------------------------
        self.dots = DotBar(38)

        rrow = QHBoxLayout()
        rrow.addStretch(1)
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setFixedSize(220, 90)
        self.btn_reset.setStyleSheet(
            "QPushButton{background:#ff4033;color:#000;"
            "font: bold 22px 'Segoe UI';"
            "border:5px solid #eee;}"
            "QPushButton:pressed{background:#ff2a18;}"
        )
        self.btn_reset.clicked.connect(self.reset_all)
        rrow.addWidget(self.btn_reset)

        # ------------------------------------------------------------------
        # MAIN LAYOUT
        # ------------------------------------------------------------------
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 30, 20, 20)
        lay.setSpacing(14)

        lay.addLayout(top)
        lay.addWidget(cue_row_widget)
        lay.addWidget(self.seek)
        lay.addLayout(trow)
        lay.addLayout(trans)
        lay.addStretch(1)
        lay.addWidget(self.dots)
        lay.addLayout(rrow)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

        # Initial state
        self.current_cue = "19"
        self.prev_cue = None
        self._load_song_for_cue("19", auto_play=False)

    # ======================================================================
    # DMX STATUS
    # ======================================================================

    def _set_dmx_status(self, state):
        ok_states = {"green", "ok", "connected", "ready"}
        if state in ok_states:
            self.dmx_dot.setStyleSheet("color:#00b200; font-size:18px;")
        else:
            self.dmx_dot.setStyleSheet("color:#aa0000; font-size:18px;")

    # ======================================================================
    # GENERAL HELPERS / RESET
    # ======================================================================

    def _reset_cue_button_styles(self):
        base = (
            "QPushButton{color:#fff;background:transparent;"
            "border:2px solid #aaa;padding:10px;}"
            "QPushButton:pressed{background:#222}"
        )
        for b in (self.c19, self.c20, self.c21):
            b.setStyleSheet(base)

    def reset_all(self):
        """Full end-of-show reset."""
        self.stop()
        self.dots.set_colors([(0, 0, 0)] * 38)
        self._reset_cue_button_styles()
        self.white_fade_t0 = None
        self.c21_hold_white = False
        self.current_cue = "19"
        self.prev_cue = None
        self._load_song_for_cue("19", auto_play=False)

    def _on_seek_ratio(self, x: float):
        if self.audio.length > 0:
            sec = x * self.audio.length
            # restart playback at new position (main channel only)
            self.audio.play(start_sec=sec)
            if self.beats:
                self.last_beat_index = -1
                for i, bt in enumerate(self.beats):
                    if bt <= sec:
                        self.last_beat_index = i
                    else:
                        break

    def play(self):
        if self.audio.paused:
            self.audio.unpause()
        else:
            self.audio.play()

    def pause(self):
        if self.audio.paused:
            self.audio.unpause()
        else:
            self.audio.pause()

    def stop(self):
        self.audio.stop()

    # ======================================================================
    # CUES
    # ======================================================================

    def load_cue(self, cid: str, auto_play: bool = True):
        """
        Load and optionally start a cue.

        Special behavior:
        - When jumping from CUE 19 to CUE 20 while 19 is playing,
          keep 19 fading out for 2 seconds while 20 starts at full volume.
        """
        prev = self.current_cue
        self.prev_cue = prev
        self.current_cue = cid
        self.white_fade_t0 = None

        # --- Special case: CUE 19 -> CUE 20 tail fade + instant 20 ---
        if (prev == "19") and (cid == "20") and (self.audio._anchor_t is not None):
            # 1) Start CUE 20 on overlay channel at full volume
            path20 = self.cfg["songs"].get("20")
            self.audio.play_overlay(path20)

            # 2) Start a 2s manual tail fade on CUE 19 (main mixer.music)
            self.audio.start_tail_fade(2.0)

            # Update cue button styles to show 20 as active
            self._reset_cue_button_styles()
            {
                "19": self.c19,
                "20": self.c20,
                "21": self.c21,
            }[cid].setStyleSheet(
                "QPushButton{color:#000;background:#16a34a;"
                "border:2px solid #4ade80;padding:10px;}"
            )

            # Update right-hand duration label using overlay length
            dur = max(0.0, self.audio.length or 0.0)
            m = int(dur // 60)
            s = int(dur % 60)
            self.lbl_r.setText(f"{m:02d}:{s:02d}")

            # For CUE 20 we don't use beats; ensure it's clean
            self.beats = []
            self.last_beat_index = -1

            return

        # --- Normal path for all other cue loads (19, 20 standalone, 21) ---
        self._load_song_for_cue(cid, auto_play=False)

        self._reset_cue_button_styles()
        {
            "19": self.c19,
            "20": self.c20,
            "21": self.c21,
        }[cid].setStyleSheet(
            "QPushButton{color:#000;background:#16a34a;"
            "border:2px solid #4ade80;padding:10px;}"
        )

        if auto_play:
            try:
                self.audio.play(start_sec=0.0)
            except TypeError:
                self.audio.play()

        if cid == "21":
            self.last_beat_index = -1
            # Reset hold-white state whenever we start CUE 21
            self.c21_hold_white = False
            self.white_fade_t0 = None

    def _load_song_for_cue(self, cid: str, auto_play: bool = False):
        path = self.cfg["songs"].get(cid)
        if path and os.path.exists(path):
            self.audio.load(path)

        dur = max(0.0, self.audio.length or 0.0)
        m = int(dur // 60)
        s = int(dur % 60)
        self.lbl_r.setText(f"{m:02d}:{s:02d}")

        self.beats = []
        self.last_beat_index = -1
        assets = self.cfg.get("assets_dir")

        if cid == "21":
            if assets and os.path.isdir(assets):
                beats_json = os.path.join(assets, "CUE_21_-_ROCKIN_beats.json")
                if os.path.exists(beats_json):
                    try:
                        with open(beats_json, "r", encoding="utf-8") as f:
                            self.beats = json.load(f)
                    except Exception:
                        self.beats = []

    # ======================================================================
    # COLOR HELPERS
    # ======================================================================

    def _current_fade_cols(self, t: float):
        x = (math.sin(t * 1.0) + 1) / 2
        cols = []
        for i in range(38):
            if i % 2 == 0:
                cols.append((int(255 * x), int(255 * (1 - x)), 0))
            else:
                cols.append((int(255 * (1 - x)), int(255 * x), 0))
        return cols

    def _blend_cols(self, cols_a, cols_b, alpha: float):
        out = []
        a = max(0.0, min(1.0, float(alpha)))
        for (r1, g1, b1), (r2, g2, b2) in zip(cols_a, cols_b):
            r = int(round(r1 * (1 - a) + r2 * a))
            g = int(round(g1 * (1 - a) + g2 * a))
            b = int(round(b1 * (1 - a) + b2 * a))
            out.append((r, g, b))
        return out

    # ======================================================================
    # MAIN TICK
    # ======================================================================

    def _tick(self):
        # Let audio engine update fades/ramp first
        self.audio.update()

        dur = max(0.01, self.audio.length or 0.01)
        pos = max(0.0, self.audio.get_pos())

        self.seek.set_progress(min(1.0, pos / dur))
        m = int(pos // 60)
        s = int(pos % 60)
        self.lbl_l.setText(f"{m:02d}:{s:02d}")

        # ---- CUE 19 ----
        if self.current_cue == "19":
            cols = self._current_fade_cols(pos * 0.8)
            self.dots.set_colors(cols)

        # ---- CUE 20 ----
        elif self.current_cue == "20":
            cols = [(0, 0, 0)] * 38

            def red_left():
                return [(255, 0, 0)] * 19 + [(0, 0, 0)] * 19

            def green_right():
                return [(0, 0, 0)] * 19 + [(0, 255, 0)] * 19

            base_cols = self._current_fade_cols(pos)

            if pos < 38.9:
                cols = base_cols
            elif pos < 40.2:
                cols = red_left()
            elif pos < 41.9:
                cols = green_right()
            elif pos < 43.2:
                cols = red_left()
            elif pos < 45.0:
                cols = green_right()
            elif pos < 46.1:
                cols = red_left()
            elif pos < 48.0:
                cols = green_right()
            elif pos < 50.0:
                alpha = min(1.0, max(0.0, (pos - 48.0) / 2.0))
                start_cols = green_right()
                cols = self._blend_cols(start_cols, base_cols, alpha)
            elif pos < 67.5:
                cols = base_cols
            elif pos < 68.6:
                cols = green_right()
            elif pos < 70.1:
                cols = red_left()
            elif pos < 71.7:
                cols = green_right()
            elif pos < 73.1:
                cols = red_left()
            elif pos < 74.6:
                cols = green_right()
            elif pos < 76.1:
                cols = red_left()
            elif pos < 78.1:
                alpha = min(1.0, max(0.0, (pos - 76.1) / 2.0))
                start_cols = red_left()
                cols = self._blend_cols(start_cols, base_cols, alpha)
            elif pos < 187.0:
                cols = base_cols
            else:
                if self.white_fade_t0 is None:
                    self.white_fade_t0 = pos
                alpha = min(1.0, (pos - self.white_fade_t0) / self.white_fade_dur)
                target_cols = [self.white_target] * 38
                cols = self._blend_cols(base_cols, target_cols, alpha)

            self.dots.set_colors(cols)

        # ---- CUE 21 ----
        else:
            # CUE 21 (ROCKIN)
            if self.c21_hold_white:
                # Once we hit all white, stay here until RESET is pressed
                cols = [(240, 240, 240)] * 38
                self.dots.set_colors(cols)
            else:
                # 0:00.0 -> 2:30.4  Rockin Red/Green
                step = int(pos * 2.0) % 2

                cols = []
                for i in range(38):
                    if (i + step) % 2 == 0:
                        cols.append((255, 0, 0))
                    else:
                        cols.append((0, 255, 0))

                # Switch to all white at 2:30.5 and hold
                if pos >= 150.5:
                    self.c21_hold_white = True
                    cols = [(240, 240, 240)] * 38

                self.dots.set_colors(cols)


def main():
    app = QApplication(sys.argv)
    w = App()
    w.resize(1280, 760)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
