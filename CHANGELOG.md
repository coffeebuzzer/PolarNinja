# Changelog

All notable changes to **Polar Ninja** will be documented in this file.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) with simple, human-readable notes.

---

## [Unreleased]

_Planning / ideas for future builds:_

- Configurable timing / length for the CUE 19 → 20 tail fade.
- Configurable DMX fixture patch / mapping for the dot bar.
- Optional advanced beat-driven RockinModes patterns for CUE 21.
- Operator log / event view for tracking show runs.
- Additional cues and layouts for other scenes.

---

## [v0.8.1-beta] – 2025-11-19

> **Status:** Small but important bugfix on top of `v0.8-beta`. This is the version you actually want on the show laptop.

### Fixed

- **CUE 20 seeking from RESET causing “double audio” (19 + 20 together)**  
  - Scenario:
    - Press **RESET** (system goes to a clean slate, with 19 “selected” but not playing).
    - Press **CUE 20** (Head Elf) directly from reset.
    - Then click somewhere in the **seek bar** (e.g., middle of the track).
  - In `v0.8-beta`:
    - The app mistakenly treated this as a “19 → 20 special handoff” even though **19 never actually played**.
    - Result: scrubbing during CUE 20 could cause:
      - **CUE 19 to start playing** on the main channel from the seek time.
      - **CUE 20 to keep playing** on the overlay channel.
      - The **dot bar timeline** to not jump forward the way 19 and 21 do.
  - In `v0.8.1-beta`:
    - The special 19 → 20 overlay logic now only runs if:
      - `prev == "19"` **and**
      - `cid == "20"` **and**
      - the main audio engine has actually started playback (i.e., 19 was really playing).
    - From RESET:
      - Clicking **CUE 20** now loads and plays 20 as a **normal single cue** on the main channel.
      - Scrubbing the seek bar:
        - Plays **only CUE 20**, no hidden 19 audio.
        - Advances the dot bar and time display as expected.

### Behavior confirmed in v0.8.1-beta

- **CUE 19 – UNLOADING**
  - Play / pause / stop all work normally.
  - Scrubbing the seek bar jumps audio and DMX where expected.

- **CUE 20 – HEAD ELF**
  - From RESET → CUE 20:
    - Plays only CUE 20.
    - Scrubbing behaves like CUE 19 and CUE 21 (no double audio, dot bar jumps).
  - From live **CUE 19 → CUE 20**:
    - CUE 20 starts instantly at full volume on an overlay channel.
    - CUE 19 fades out smoothly over ~2 seconds on the main channel.
    - Pause freezes audio, timer, and DMX together; unpause resumes cleanly.

- **CUE 21 – ROCKIN**
  - Red/green “rockin” pattern runs as designed.
  - At **~2:30.5**, dot bar flips to **All White Low Power** and **stays white** until RESET is pressed.

---

## [v0.8-beta] – 2025-11-18

> **Status:** Successor to **v0.7-golden** – adds a smooth 19→20 overlay handoff and tightens CUE 21’s “all white” ending. Superseded by `v0.8.1-beta` for show use.

### Added

- **Dual-path audio engine for special cue transitions**
  - `AudioEngine` now runs:
    - The **main track** on `pygame.mixer.music`.
    - A dedicated **overlay channel** (Channel 7) for special cases like CUE 20 over CUE 19.
  - Simple **sound cache** warms (pre-decodes) the audio for CUE 19 / 20 / 21 at startup to avoid hiccups the first time a cue is hit.
- **Overlay-aware pause / resume**
  - Pause now freezes:
    - The main track.
    - Any active overlay track (e.g., CUE 20 when it’s running on top of 19).
    - The **timeline and DMX dot-bar**.
  - Resume correctly advances both clocks so audio + visuals stay locked together.

### Changed

- **CUE 19 → CUE 20 audio behavior (when 19 is playing)**
  - Pressing **CUE 20 while CUE 19 is already playing** now:
    - Starts **CUE 20 instantly at full volume** on the overlay channel.
    - Keeps **CUE 19 playing underneath**, then fades it out smoothly over **~2 seconds**.
    - Eliminates the brief “dead air” / mute feeling from earlier betas.
  - Pressing **CUE 20 while CUE 19 is *not* playing** still behaves like a normal single-cue start (no overlay needed in 0.8).

- **Pause / resume with overlays**
  - In previous builds, pausing during a 19 → 20 transition could:
    - Stop the audio, but
    - Allow the **status timer and DMX dots to keep running**, as if the track were still playing.
  - In v0.8:
    - Pause freezes both the **audio** and the **visual timeline**, even when CUE 20 is running as an overlay.
    - Resume picks up **audio + timer + DMX** from the same moment, no drift.

- **CUE 21 – ROCKIN end-of-track behavior**
  - The red/green “Rockin” pattern remains as in v0.7-golden.
  - The switch to **All White Low Power** is now tied to a **specific musical moment**:
    - `0:00.0 → 2:30.4` – Rockin red/green pattern across all 38 dots.
    - At **`2:30.5`**, the dot bar flips to **All White Low Power** and stays there.
  - Once in All White:
    - The bar **stays white** even after the audio ends.
    - It remains that way until the operator hits **RESET**.
  - This replaces the older “near end-of-track” detection, which could be slightly fuzzy depending on runtime timing.

### Fixed

- **Audio gap when jumping from CUE 19 → CUE 20**
  - Earlier betas could momentarily mute or “hiccup” all audio when pressing CUE 20 while 19 was already playing, due to MP3 decoding overhead at button press.
  - v0.8 fixes this by:
    - Pre-warming the sounds at launch.
    - Running CUE 20 on a separate overlay channel.
    - Keeping CUE 19 alive long enough to perform a clean 2-second tail fade.

- **Paused CUE 20 timeline continuing in the background**
  - When coming from 19 → 20, pausing could stop the music but leave the on-screen timer and DMX timeline moving.
  - Now, **pause truly pauses everything** – both clocks, both channels, and the dot bar visuals.

---

## [v0.7-golden] – 2025-11-17

> **Status:** Show-ready, pinned as the **Golden Beta .07** build. Superseded by v0.8+.

### Added
- **DMX status dot** in the top-right:
  - Shows `DMX ●` in **red** when no interface / COM port is detected.
  - Turns **green** when the DMX USB interface is present and the COM port is open.
  - Uses a lightweight DMX engine that periodically pokes the port and reacts to errors.

- **RESET** button behavior finalized:
  - Stops audio playback.
  - Clears all cue highlights.
  - Turns all dot-bar LEDs “off” (black).
  - Resets internal state so the system is ready to start again on **CUE 19** for the next train.

### Changed
- **CUE 19 → CUE 20 audio behavior**
  - Removed all attempted audio “crossfade” logic.
  - Pressing **CUE 20** now starts that track **instantly** (hard, intentional cut) for predictable show operation.

- **CUE 20 lighting timeline**
  - Implemented clean, explicit timing based on show notes:
    - `0:38.9`  – Red Side Left  
    - `0:40.2`  – Green Side Right  
    - `0:41.9`  – Red Side Left  
    - `0:43.2`  – Green Side Right  
    - `0:45.0`  – Red Side Left  
    - `0:46.1`  – Green Side Right  
  - Two **WOW** moments now have proper 2-second fades:
    - `0:48.0 → 0:50.0` – fade from “Green Side Right” into full red/green alternating pattern.  
    - `0:76.1 → 0:78.1` – fade from “Red Side Left” into full red/green alternating pattern.
  - Preserved the long, smooth **3-second fade into All White Low Power** starting at `3:07.0`.

- **CUE 21 – ROCKIN pattern**
  - Replaced previous beat-dependent logic with a **simple, deterministic pattern**:
    - 38-dot bar alternates red/green in a “rocking” back-and-forth motion.
    - Tempo slowed to feel more musical (approx. **2 flips per second** instead of hyper-fast flashing).
  - At the end of the track, the pattern snaps to **All White Low Power** and holds until reset.

- **UI polish**
  - Confirmed layout for:
    - Title bar with version string.
    - CUE 19 / 20 / 21 buttons row directly under the title.
    - Seek bar + elapsed / total time labels.
    - Circular Play / Pause / Stop transport controls.
    - Dot bar along the bottom.
    - Large red **RESET** button bottom-right.
  - Ensured all controls render correctly in **dark mode** and are clearly legible in a low-light environment.

### Fixed
- Intermittent issues with:
  - Missing / invisible cue buttons on startup in some earlier layouts.
  - RESET not fully clearing cue highlights or dot-bar state.
  - ROCKIN (CUE 21) sometimes leaving the dot bar black due to dependency on external beat files.
- Cleaned up unused and legacy code paths (old `app/` structure, unused modes, logs, and cache folders) in the working tree prior to tagging `v0.7-golden`.

---

## [Earlier Betas] – Pre-golden history (high level)

These versions were internal / experimental and are not individually tagged in this repo. Highlights include:

- Initial PySide6 dark-mode UI.
- Basic CUE 19 / 20 / 21 playback wiring.
- First versions of the dot-bar visualizer.
- Early DMX connection indicator using an “Online/Offline” pill instead of a simple dot.
- Prototype RockinModes beat-based patterns and tools for waveform/beat analysis.

These builds informed the final layout and behavior of `v0.7-golden` but are not recommended for live show use.
