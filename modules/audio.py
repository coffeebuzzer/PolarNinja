import pygame, os, json, time
print("Polar Ninja AudioEngine v0.7 (overlay cache + manual tail fade)")

# Low-latency mixer settings to speed up start/seek
pygame.mixer.pre_init(44100, -16, 2, 256)
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


class AudioEngine:
    """
    Audio engine with:
    - mixer.music for the "main" track (normally the current cue)
    - an overlay Channel for an additional track (used for CUE 20 while 19 tails)
    - a virtual clock for UI seek bar
    - manual tail-fade control for smooth 19 -> 20 transition
    - simple sound cache so overlay sounds are pre-decoded
    """

    def __init__(self):
        self.path = None
        self.length = 0.0
        self.assets_dir = None

        # Virtual clock for mixer.music
        self._anchor_t = None
        self._anchor_off = 0.0
        self._pause_t = None
        self.paused = False
        self._ramp_until = 0.0

        # Overlay channel for special cases (e.g. CUE 19 -> 20)
        self.overlay_channel = pygame.mixer.Channel(7)
        self.overlay_sound = None
        self.overlay_start_t = None
        self.overlay_active = False
        self._overlay_pause_t = None  # for proper pause timing

        # Manual tail fade for mixer.music (CUE 19 only)
        self.tail_fade_active = False
        self.tail_fade_t0 = None
        self.tail_fade_dur = 0.0

        # Simple cache of preloaded sounds
        self._sound_cache = {}

    # ------------- Setup / Loading -------------

    def set_assets_dir(self, assets_dir):
        self.assets_dir = assets_dir

    def warm_sound(self, path: str):
        """Pre-decode a sound into the cache without playing it."""
        if not path or (not os.path.exists(path)):
            return
        if path in self._sound_cache:
            return
        try:
            snd = pygame.mixer.Sound(path)
        except Exception:
            return
        self._sound_cache[path] = snd

    def load(self, path: str):
        """Load a file into mixer.music as the main track."""
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

        # Reset clock & flags
        self.paused = False
        self._anchor_t = None
        self._anchor_off = 0.0
        self._pause_t = None
        self._ramp_until = 0.0
        self.tail_fade_active = False
        self.tail_fade_t0 = None
        self.tail_fade_dur = 0.0

    # ------------- Main playback -------------

    def _apply_ramp(self):
        if self._ramp_until > 0.0:
            now = time.time()
            if now < self._ramp_until:
                amt = max(0.0, min(1.0, 1.0 - (self._ramp_until - now)))
                pygame.mixer.music.set_volume(amt)
            else:
                pygame.mixer.music.set_volume(1.0)
                self._ramp_until = 0.0

    def play(self, start_sec: float = 0.0, ramp_in_sec: float = 0.0):
        """Play the main track from a certain position."""
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
        self.tail_fade_active = False
        self.tail_fade_t0 = None
        self.tail_fade_dur = 0.0
        if ramp_in_sec and ramp_in_sec > 0.0:
            pygame.mixer.music.set_volume(0.0)
            self._ramp_until = time.time() + float(ramp_in_sec)
        else:
            pygame.mixer.music.set_volume(1.0)
            self._ramp_until = 0.0

    # ------------- Overlay (CUE 20) -------------

    def play_overlay(self, path: str):
        """
        Play an additional track on a separate channel at full volume.
        Used for CUE 20 while CUE 19 is fading out.
        """
        # Stop any existing overlay first
        if self.overlay_active:
            try:
                self.overlay_channel.stop()
            except Exception:
                pass
            self.overlay_active = False
            self.overlay_start_t = None
            self.overlay_sound = None
            self._overlay_pause_t = None

        if not path or (not os.path.exists(path)):
            return

        # Use cached sound if available, else load and cache
        snd = self._sound_cache.get(path)
        if snd is None:
            try:
                snd = pygame.mixer.Sound(path)
            except Exception:
                return
            self._sound_cache[path] = snd

        self.overlay_sound = snd
        self.overlay_start_t = time.time()
        self.overlay_active = True
        self._overlay_pause_t = None
        self.overlay_channel.play(snd)

        # For UI timeline, treat this overlay as the "current" track
        try:
            self.length = snd.get_length()
        except Exception:
            pass

    # ------------- Manual tail fade for 19 -------------

    def start_tail_fade(self, dur_sec: float = 2.0):
        """
        Start a manual fade-out of the main mixer.music channel over dur_sec seconds.
        This is used when CUE 19 is still playing and we trigger CUE 20.
        """
        self.tail_fade_active = True
        self.tail_fade_t0 = time.time()
        self.tail_fade_dur = max(0.1, float(dur_sec))
        # Disable any ramp-in that might still be running
        self._ramp_until = 0.0

    def _update_tail_fade(self):
        """Internal: called from update() to progress the tail fade."""
        if not self.tail_fade_active or self.tail_fade_t0 is None:
            return
        now = time.time()
        elapsed = now - self.tail_fade_t0
        if elapsed >= self.tail_fade_dur:
            # Fade complete: stop the main music channel
            pygame.mixer.music.stop()
            self.tail_fade_active = False
            self.tail_fade_t0 = None
            self.tail_fade_dur = 0.0
            return
        # Otherwise, scale volume linearly from 1.0 -> 0.0
        alpha = max(0.0, min(1.0, elapsed / self.tail_fade_dur))
        vol = 1.0 - alpha
        pygame.mixer.music.set_volume(vol)

    # ------------- Pause / Stop / Update -------------

    def pause(self):
        """Pause all playback (main + overlay) and freeze clocks."""
        if not self.paused:
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            self.paused = True
            now = time.time()
            self._pause_t = now
            if self.overlay_active and (self.overlay_start_t is not None):
                self._overlay_pause_t = now

    def unpause(self):
        """Unpause all playback (main + overlay) and resume clocks."""
        if self.paused:
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()
            now = time.time()
            if self._pause_t is not None and self._anchor_t is not None:
                paused_dur = now - self._pause_t
                self._anchor_t += paused_dur
            if (
                self.overlay_active
                and (self.overlay_start_t is not None)
                and (self._overlay_pause_t is not None)
            ):
                paused_dur_ov = now - self._overlay_pause_t
                self.overlay_start_t += paused_dur_ov
            self.paused = False
            self._pause_t = None
            self._overlay_pause_t = None

    def stop(self):
        """Stop all playback and reset state."""
        pygame.mixer.music.stop()
        try:
            self.overlay_channel.stop()
        except Exception:
            pass
        self.overlay_active = False
        self.overlay_start_t = None
        self.overlay_sound = None
        self._overlay_pause_t = None

        self.paused = False
        self._anchor_t = None
        self._pause_t = None
        self._ramp_until = 0.0
        self.tail_fade_active = False
        self.tail_fade_t0 = None
        self.tail_fade_dur = 0.0

    def update(self):
        """
        Call this periodically (e.g. from the GUI timer) to:
        - maintain any tail fade on the main channel
        - maintain any ramp-in on the main channel
        """
        if self.tail_fade_active:
            self._update_tail_fade()
        else:
            # Only apply ramp if we aren't running a tail fade
            self._apply_ramp()

    # ------------- Position reporting -------------

    def get_pos(self) -> float:
        """
        Return the "current position" in seconds, for the UI timeline.
        When an overlay is active (e.g. CUE 20), we report that position.
        Otherwise we report the virtual clock for the main mixer.music track.
        """
        # If overlay is active, that is the "current cue"
        if self.overlay_active and (self.overlay_start_t is not None):
            if not self.overlay_channel.get_busy():
                # Overlay finished naturally
                self.overlay_active = False
                self.overlay_start_t = None
                return self.length or 0.0

            # While paused, freeze the overlay clock (like the main clock)
            if self.paused and (self._overlay_pause_t is not None):
                pos = self._overlay_pause_t - self.overlay_start_t
            else:
                pos = time.time() - self.overlay_start_t

            if (self.length > 0.0) and (pos > self.length):
                pos = self.length
            return pos

        # Otherwise, use virtual clock for main music
        if self._anchor_t is None:
            return 0.0
        if self.paused and (self._pause_t is not None):
            return self._anchor_off + (self._pause_t - self._anchor_t)
        pos = self._anchor_off + (time.time() - self._anchor_t)
        if (self.length > 0.0) and (pos > self.length):
            pos = self.length
        return pos
