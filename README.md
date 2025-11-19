# Polar Ninja 🎄🐧

**Polar Ninja** is a show-control app built in Python for a Polar Express–style roundhouse experience.

It’s designed to sit in front of a human operator and make three critical moments of the show **bullet-proof**:

- **CUE 19 – UNLOADING**  
- **CUE 20 – HEAD ELF SCENE**  
- **CUE 21 – ROCKIN’**  

with synchronized audio, DMX status feedback, and a simple, dark UI that’s easy to see in low light.

---

## Status

> **Version:** `Beta 0.8` (successor to `v0.7-golden`)  
> **Use case:** Show-ready build for live operation  
> **Platform:** Windows (tested on Python 3.11)

This repo now represents the **Beta 0.8** build, which builds on `v0.7-golden` by:

- Adding a smooth, **no-gap 19 → 20 audio handoff** (20 comes in instantly while 19 tails out).
- Tightening **CUE 21’s “All White Low Power”** timing to a specific musical moment.
- Ensuring **Pause** always freezes audio, timer, and DMX together – even during the special 19 → 20 transition.

---

## Features

### 🎧 Cue Control (19 / 20 / 21)

Three big cue buttons across the top:

- **CUE 19 – UNLOADING**
  - Plays the unloading track.
  - Drives a **smooth alternating red/green fade** across the dot bar to match the scene.

- **CUE 20 – HEAD ELF**
  - When triggered on its own:
    - Starts immediately and runs like a normal cue.
  - When triggered while **CUE 19 is already playing**:
    - **CUE 20 starts instantly at full volume** on a dedicated overlay channel.
    - **CUE 19 keeps playing underneath**, then fades out smoothly over about **2 seconds**.
    - There is **no “dead air” gap** between the cues.
  - DMX timeline for the show:
    - Red / Green side splits (left red / right green, then swapped).
    - Two **WOW** moments where the lights **fade over ~2 seconds** from split looks into a full red/green alternating pattern.
    - At ~3:07 the lights perform a **smooth 3-second fade to All White Low Power**.

- **CUE 21 – ROCKIN’**
  - Simple, beat-inspired **red/green “rockin” pattern** across 38 DMX “pixels”.
  - Pattern rocks back and forth at a **slower, more musical tempo** (about 2 flips per second).
  - At **~2:30.5**, the dot bar flips to **All White Low Power**:
    - Stays all white even after the track ends.
    - Remains white until the operator presses **RESET**.

All cue buttons:

- Highlight green when active.
- Are big enough to confidently hit in the dark with cold fingers and a radio in the other hand.

---

### 💡 DMX Status (Top Right)

Top-right of the UI shows:

`DMX ●`

- **Red dot** – No DMX interface detected / COM port not open.
- **Green dot** – DMX USB interface detected and COM port open.

Under the hood:

- Uses `pyserial` to open the configured COM port (e.g., a DMXKing UltraDMX Micro).
- Periodically pokes the port to detect unplug / error conditions and flip back to red if the device disappears.

This is intended as a **pre-show sanity check** so the operator can see at a glance whether the DMX dongle is alive and talking.

---

### 🌈 Dot Bar Visualization

A 38-“pixel” dot bar along the bottom represents your DMX universe visually:

- **CUE 19**  
  → Smooth red/green sine-wave fade across all dots.

- **CUE 20**  
  → Lighting choreography that follows the Head Elf script:
  - Side-split looks (all left red, all right green, and vice versa).
  - WOW moments: **2-second fades into the full red/green alternating look**.
  - Long fade into All White Low Power at the end.

- **CUE 21**  
  → Red/green pattern that shifts back and forth in time with the track, then:
  - At ~2:30.5, the bar flips to **All White Low Power**.
  - White is held until **RESET**, even after the audio stops.

The bar is purely **visual feedback** for the operator in this build; DMX output itself is handled by the DMX engine + external fixtures.

---

### ⏯ Transport & Seek

Below the cue buttons:

- **Seek bar** with time labels (elapsed / total).
- **Transport controls:**
  - Play
  - Pause
  - Stop

You can:

- Use the **seek bar** to jump within a track.
- See run time clearly in a dark environment via the bright time readouts.

In Beta 0.8, **Pause**:

- Freezes audio for both the main cue and any overlay cue.
- Freezes the timeline and DMX dot-bar animation.
- Resumes cleanly from the same moment when un-paused.

---

### 🔁 RESET (End-of-Show Button)

A big **RESET** button on the bottom right:

When pressed:

- Stops audio.
- Clears all lights (dot bar goes black).
- De-highlights all cue buttons.
- Resets internal state so the system is ready to run **CUE 19** for the next train.

End of show → press RESET → system returns to a known, safe **“ready”** state.

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
