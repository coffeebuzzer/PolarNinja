import tkinter as tk
from tkinter import ttk

ACCENT = "#16a34a"
BG     = "#0b0b0b"
PANEL  = "#111111"
FG     = "#e6e6e6"
MUTED  = "#9aa0a6"

def apply_classic(root: tk.Tk):
    root.configure(bg=BG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=BG, foreground=FG, fieldbackground=BG)

    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("TButton", background="#1f1f1f", foreground=FG, padding=(12,6))
    style.map("TButton",
              background=[("active", "#2a2a2a")],
              foreground=[("disabled", "#6b7280")])

    style.configure("Transport.TButton", padding=(16,10), font=("Segoe UI", 12, "bold"))
    style.configure("Cue.TButton", padding=(12,8), font=("Segoe UI", 11, "bold"))
    style.configure("Reset.TButton", padding=(10,6), font=("Segoe UI", 11, "bold"))

    return style
