import json, csv, os, wave

def _duration_from_wav(wav_guess: str) -> float:
    try:
        with wave.open(wav_guess, 'rb') as wf:
            fr = wf.getframerate()
            n = wf.getnframes()
            return n / float(fr) if fr else 0.0
    except Exception:
        return 0.0

def load_waveform(path: str):
    """
    Robust loader for waveform JSON/CSV.
    - Accepts UTF-8 with or without BOM.
    - JSON: {"points":{"value":[...]}} or [{"t":..,"a":..}, ...] with optional "duration".
    - CSV: headers can be value / a, and optional t for duration.
    Returns: {"duration": float, "values": [float]}
    """
    values, duration = [], 0.0
    plower = path.lower()

    if plower.endswith(".json"):
        # Handle UTF-8 BOM safely
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        pts = data.get("points")
        if isinstance(pts, dict) and "value" in pts:
            values = list(pts["value"])
        elif isinstance(pts, list):
            values = [float(p.get("a", 0.0)) for p in pts]
            duration = float(data.get("duration", 0.0))
        else:
            # Fallback: if the JSON is a flat list of numbers
            if isinstance(data, list):
                values = [float(x) for x in data]
    else:
        # CSV (accept BOM)
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rd = csv.DictReader(f)
            # Normalize headers to lowercase
            field_map = {name.lower(): name for name in rd.fieldnames} if rd.fieldnames else {}
            val_key = field_map.get("value") or field_map.get("a")
            t_key = field_map.get("t")
            for row in rd:
                if val_key and row.get(val_key) not in (None, ""):
                    values.append(float(row[val_key]))
                elif "value" in row and row["value"] not in (None, ""):
                    values.append(float(row["value"]))
                elif "a" in row and row["a"] not in (None, ""):
                    values.append(float(row["a"]))
                if t_key and row.get(t_key):
                    try:
                        duration = float(row[t_key])
                    except Exception:
                        pass

    # Try sibling WAV for duration if present
    base_no_ext = path.rsplit("_waveform.", 1)[0]
    wav_guess = base_no_ext + ".wav"
    dur_wav = _duration_from_wav(wav_guess)
    if dur_wav > 0:
        duration = dur_wav

    return {"duration": float(duration), "values": [float(v) for v in values]}

def load_beats(path_json: str):
    # Handle UTF-8 with BOM safely
    with open(path_json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    bpm = float(data.get("tempo_bpm", 0.0))
    beats = [float(x) for x in data.get("beats_sec", [])]
    return {"tempo_bpm": bpm, "beats_sec": beats}
