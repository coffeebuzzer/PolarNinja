# Polar Ninja 🎄🐧

**Polar Ninja** is a show-control app built in Python for a Polar Express–style roundhouse experience.

It’s designed to sit in front of a human operator and make three critical moments of the show **bullet-proof**:

- **CUE 19 – UNLOADING**  
- **CUE 20 – HEAD ELF SCENE**  
- **CUE 21 – ROCKIN’**  

with synchronized audio, DMX status feedback, and a simple, dark UI that’s easy to see in low light.

---

## Status

> **Version:** `Beta 0.8.1`  
> **Lineage:** `v0.7-golden` → `v0.8-beta` → `v0.8.1-beta`  
> **Use case:** Show-ready build for live operation on Windows  
> **Platform:** Tested on Python 3.11

`v0.8.1-beta` is a small but important fix on top of `v0.8-beta`:

- Keeps the **smooth 19 → 20 overlay crossfade** (20 in instantly, 19 tails out over ~2s).
- Keeps **CUE 21 all-white timing** (around 2:30.5, stays white until RESET).
- Fixes a bug where **scrubbing CUE 20 from RESET** could cause CUE 19 and CUE 20 to play at the same time.

For detailed history, see [`CHANGELOG.md`](CHANGELOG.md).

---

## Features

### 🎧 Cue Control (19 / 20 / 21)

Three big cue buttons across the top:

- **CUE 19 – UNLOADING**
  - Plays the unloading track.
  - Drives a **smooth alternating red/green fade** across the dot bar to match the scene.
  - Seek bar jumps cleanly if you scrub forward/backward.

- **CUE 20 – HEAD ELF**
  - When triggered on its own (e.g., from RESET):
    - Starts as a normal single cue on the main audio channel.
    - Scrubbing the seek bar jumps the audio and DMX timeline correctly.
  - When triggered while **CUE 19 is already playing**:
    - **CUE 20 starts instantly at full volume** on a dedicated overlay channel.
    - **CUE 19 continues underneath**, then fades out smoothly over about **2 seconds**.
    - No “dead air” between cues.
  - The lighting timeline:
    - Alternates **Red Side Left** / **Green Side Right** looks at specific timestamps.
    - Has two **WOW fades** where we blend those side looks into a full red/green alternating pattern over ~2 seconds.
    - Finishes with a **3-second fade to All White Low Power** near the end of the track.

- **CUE 21 – ROCKIN’**
  - Simple, beat-inspired **red/green “rockin” pattern** across 38 DMX “pixels.”
  - Pattern rocks back and forth at a **comfortable, musical tempo** (about 2 flips per second).
  - At **~2:30.5**, the dot bar flips to **All White Low Power**:
    - Stays white even after the track ends.
    - Remains white until the operator presses **RESET**.

All cue buttons:

- Highlight green when active.
- Are large and easy to hit confidently in low light.

---

### 💡 DMX Status (Top Right)

Top-right of the UI shows:

`DMX ●`

- **Red dot** – No DMX interface detected / COM port not open.
- **Green dot** – DMX USB interface detected and COM port open.

Under the hood:

- Uses `pyserial` to open the configured COM port (e.g., a DMXKing UltraDMX Micro).
- Periodically talks to the port and flips the dot back to red if the device disappears.

This gives the operator a quick **pre-show “is DMX alive?”** check.

---

### 🌈 Dot Bar Visualization

A 38-“pixel” dot bar along the bottom represents your DMX universe visually:

- **CUE 19**
  - Smooth red/green sine-wave fade across all dots (ambient unloading look).

- **CUE 20**
  - Lighting choreography that follows the Head Elf script:
    - Side-split red/green looks (all left red, all right green, and vice versa).
    - WOW moments with **2-second fades** into the full red/green alternating look.
    - A long **fade to All White Low Power** at the end.

- **CUE 21**
  - Red/green pattern that shifts back and forth in time with the track.
  - At ~2:30.5, flips to **All White Low Power** and holds until RESET.

The dot bar is meant as **visual feedback** for the operator; actual DMX output is handled by the DMX engine and your real fixtures.

---

### ⏯ Transport & Seek

Below the cue buttons:

- **Seek bar** with time labels (elapsed / total).
- Circular **Play**, **Pause**, and **Stop** transport controls.

Behavior:

- **Play** – Starts or resumes playback.
- **Pause** – Freezes:
  - Audio (main + overlay if present),
  - The timeline,
  - The DMX dot-bar animation.
- **Stop** – Stops audio and returns the transport to the beginning of the current cue.

Scrubbing the seek bar:

- Works for all three cues.
- In `v0.8.1-beta`, scrubbing during CUE 20 works correctly whether you:
  - Came straight from RESET, or
  - Came from a true 19 → 20 transition.

---

### 🔁 RESET (End-of-Show Button)

A big **RESET** button on the bottom right:

- Stops any playing audio.
- Clears all lights (dot bar goes black).
- De-highlights all cue buttons.
- Resets internal state so the system is ready to start **CUE 19** for the next train.

This is your **“end-of-show, prepare for next train”** button.

---

## Installation & Setup

### 1. Requirements

- **Windows**
- **Python 3.11** installed and available as `py` or `python` in your PATH.
- A supported **DMX USB interface** (e.g., DMXKing UltraDMX Micro) if you want live DMX status.

### 2. Clone the repo

```bash
git clone https://github.com/coffeebuzzer/PolarNinja.git
cd PolarNinja
