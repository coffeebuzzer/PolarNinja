
import os, json

DEFAULTS = {
    "beta_label": "Polar Ninja - Beta .05",
    "online_mode": True,
    "dmx_com_port": 11,
    "music_dir": r"C:\PolarNinja\music",
    "assets_dir": r"C:\PolarNinja\assets",
    "songs": {},
}

FALLBACK_FILENAMES = {
    "19": "CUE 19 - UNLOADING.mp3",
    "20": "CUE 20 - HEAD ELF SCENE.mp3",
    "21": "CUE 21 - ROCKIN.mp3",
}

def _ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def _settings_path():
    here = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.abspath(os.path.join(here, os.pardir))
    return os.path.join(app_root, "settings.json")

def _autofill_songs(cfg):
    music_dir = cfg.get("music_dir") or DEFAULTS["music_dir"]
    songs = cfg.get("songs") or {}
    updated = False
    for cid, fname in FALLBACK_FILENAMES.items():
        want = os.path.join(music_dir, fname)
        cur = songs.get(cid, "")
        cur_dir = os.path.dirname(cur) if cur else ""
        if (not cur) or (cur_dir.lower() != music_dir.lower()):
            songs[cid] = want
            updated = True
    cfg["songs"] = songs
    return updated

def _maybe_migrate_old_paths(cfg):
    changed = False
    old_root = r"C:\polarexpressninja"
    if os.path.exists(old_root):
        assets = cfg.get("assets_dir", DEFAULTS["assets_dir"])
        if isinstance(assets, str) and assets.lower().startswith(old_root.lower()):
            cfg["assets_dir"] = DEFAULTS["assets_dir"]; changed = True
        for cid, p in list((cfg.get("songs") or {}).items()):
            if isinstance(p, str) and p.lower().startswith(old_root.lower()):
                cfg["songs"][cid] = os.path.join(DEFAULTS["music_dir"], FALLBACK_FILENAMES[cid]); changed = True
    return changed

def load_settings():
    cfg = DEFAULTS.copy()
    spath = _settings_path()
    if os.path.exists(spath):
        try:
            with open(spath, "r", encoding="utf-8") as f:
                on_disk = json.load(f)
            if isinstance(on_disk, dict):
                cfg.update(on_disk)
        except Exception:
            pass

    _ensure_dir(cfg.get("music_dir", DEFAULTS["music_dir"]))
    _ensure_dir(cfg.get("assets_dir", DEFAULTS["assets_dir"]))

    changed = _maybe_migrate_old_paths(cfg)
    changed = _autofill_songs(cfg) or changed

    if changed:
        try:
            with open(spath, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass
    return cfg

def save_settings(cfg):
    spath = _settings_path()
    try:
        with open(spath, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
