import tkinter as tk
from tkinter import ttk
class TopBar(ttk.Frame):
    def __init__(self, master, on_toggle_online):
        super().__init__(master)
        self.online_var = tk.BooleanVar(value=True)
        self._on_toggle = on_toggle_online
        ttk.Label(self, text="Online / Offline").grid(row=0, column=0, padx=(0,8))
        self.switch = ttk.Checkbutton(self, variable=self.online_var, command=self._toggled, text="")
        self.switch.grid(row=0, column=1)
        self.dot = tk.Canvas(self, width=14, height=14, highlightthickness=0)
        self.dot.grid(row=0, column=2, padx=(10,6))
        self.status_lbl = ttk.Label(self, text="OFFLINE")
        self.status_lbl.grid(row=0, column=3)
        self.set_status("offline")
    def _toggled(self):
        if callable(self._on_toggle):
            self._on_toggle(bool(self.online_var.get()))
    def set_status(self, state: str):
        self.dot.delete("all")
        color = {"offline":"#808080","red":"#d9534f","green":"#5cb85c"}.get(state, "#808080")
        self.dot.create_oval(2,2,12,12, fill=color, outline="")
        self.status_lbl.config(text=("OFFLINE" if state=="offline" else ("DMX OK" if state=="green" else "DMX ERR")))
