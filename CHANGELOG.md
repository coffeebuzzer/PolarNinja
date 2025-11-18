# Changelog

All notable changes to **Polar Ninja** will be documented in this file.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) with simple, human-readable notes.

---

## [Unreleased]

_Planning / ideas for future builds:_

- True dual-channel DJ-style crossfade between CUE 19 and CUE 20.
- Configurable DMX fixture patch / mapping for the dot bar.
- Optional advanced beat-driven RockinModes patterns for CUE 21.
- Operator log / event view for tracking show runs.
- Additional cues and layouts for other scenes.

---

## [v0.7-golden] – 2025-11-17

> **Status:** Show-ready, pinned as the **Golden Beta .07** build.

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
    - `1:16.1 → 1:18.1` – fade from “Red Side Left” into full red/green alternating pattern.
  - Preserved the long, smooth **3-second fade into All White Low Power** starting at `3:07.0`.

- **CUE 21 – ROCKIN pattern**
  - Replaced previous beat-dependent logic with a **simple, deterministic pattern**:
    - 38-dot bar alternates red/green in a “rocking” back-and-forth motion.
    - Tempo slowed to feel more musical (approx. **2 flips per second** instead of hyper-fast flashing).
  - At the end of the track, the pattern snaps to **All White Low Power** and holds until reset.

- **UI polish**
  - Confirmed layout for:
    - Title bar with version string: `Polar Ninja - Beta .07 - Designed by Dustin`.
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

- **Beta 0.6 and earlier**
  - Initial PySide6 dark-mode UI.
  - Basic CUE 19 / 20 / 21 playback wiring.
  - First versions of the dot-bar visualizer.
  - Early DMX connection indicator using an “Online/Offline” pill instead of a simple dot.
  - Prototype RockinModes beat-based patterns and tools for waveform/beat analysis.

These builds informed the final layout and behavior of `v0.7-golden` but are not recommended for live show use.

---

## Notes

- This changelog is focused on **operator-visible behavior** and **show safety**.
- Internal refactors, minor style tweaks, and comment changes may not be listed unless they affect how the app is used during a live show.
