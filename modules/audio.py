
import pygame, os, json, time
print("Polar Ninja AudioEngine v0.5 (set_assets_dir, low-latency)")

# Low-latency mixer settings to speed up start/seek
pygame.mixer.pre_init(44100, -16, 2, 256)  # freq, size, channels, buffer (smaller = lower latency)
pygame.mixer.init()

def _duration_from_assets(song_path, assets_dir):
    if not assets_dir:
        return 0.0
    name = os.path.basename(song_path).upper()
    guess = None
    if "UNLOADING" in name:
        guess = os.path.join(assets_dir, "CUE_19_-_UNLOADING_waveform.json")
    elif "HEAD ELF" in name:
        guess = os.path.join(assets_dir, "CUE_20_-_HEAD_ELF_SCENE_waveform.json")
    elif "ROCKIN" in name:
        guess = os.path.join(assets_dir, "CUE_21_-_ROCKIN_waveform.json")
    if guess and os.path.exists(guess):
        try:
            with open(guess, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            dur = float(data.get("duration", 0.0))
            if dur > 0.0:
                return dur
        except Exception:
            return 0.0
    return 0.0

class AudioEngine(object):
    """Keep a virtual clock so the UI seek bar updates instantly."""
    def __init__(self):
        self.path = None
        self.length = 0.0
        self.paused = False
        self.assets_dir = None
        self._anchor_t = None
        self._anchor_off = 0.0
        self._pause_t = None
        self._ramp_until = 0.0

    def set_assets_dir(self, assets_dir):
        self.assets_dir = assets_dir

    def load(self, path):
        self.stop()
        self.path = path
        pygame.mixer.music.load(path)
        try:
            snd = pygame.mixer.Sound(path)
            self.length = snd.get_length()
        except Exception:
            self.length = 0.0
        if (not self.length) and self.assets_dir:
            self.length = _duration_from_assets(path, self.assets_dir) or 0.0
        self.paused = False
        self._anchor_t = None
        self._anchor_off = 0.0
        self._pause_t = None

    def _apply_ramp(self):
        if self._ramp_until > 0.0:
            now = time.time()
            if now < self._ramp_until:
                amt = max(0.0, min(1.0, 1.0 - (self._ramp_until - now)))
                pygame.mixer.music.set_volume(amt)
            else:
                pygame.mixer.music.set_volume(1.0)
                self._ramp_until = 0.0

    def play(self, start_sec=0.0, ramp_in_sec=0.0):
        if self.path is None:
            return
        try:
            pygame.mixer.music.play(start=float(start_sec))
        except TypeError:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
        self.paused = False
        self._anchor_t = time.time()
        self._anchor_off = float(start_sec)
        self._pause_t = None
        if ramp_in_sec and ramp_in_sec > 0.0:
            pygame.mixer.music.set_volume(0.0)
            self._ramp_until = time.time() + float(ramp_in_sec)
        else:
            pygame.mixer.music.set_volume(1.0)
            self._ramp_until = 0.0

    def quick_fadeout(self, ms=800):
        try:
            pygame.mixer.music.fadeout(int(ms))
        except Exception:
            pygame.mixer.music.stop()

    def pause(self):
        if pygame.mixer.music.get_busy() and (not self.paused):
            pygame.mixer.music.pause()
            self.paused = True
            self._pause_t = time.time()

    def unpause(self):
        if self.paused:
            pygame.mixer.music.unpause()
            if self._pause_t is not None and self._anchor_t is not None:
                paused_dur = time.time() - self._pause_t
                self._anchor_t += paused_dur
            self.paused = False
            self._pause_t = None

    def stop(self):
        pygame.mixer.music.stop()
        self.paused = False
        self._anchor_t = None
        self._pause_t = None
        self._ramp_until = 0.0

    def get_pos(self):
        if self._anchor_t is None:
            return 0.0
        if self.paused and (self._pause_t is not None):
            return self._anchor_off + (self._pause_t - self._anchor_t)
        pos = self._anchor_off + (time.time() - self._anchor_t)
        if (self.length > 0.0) and (pos > self.length):
            pos = self.length
        self._apply_ramp()
        return pos
