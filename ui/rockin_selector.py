import tkinter as tk
from tkinter import ttk
class RockinSelector(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self.mode = tk.IntVar(value=1)
        for i, label in enumerate(("Example 1","Example 2","Example 3"), start=1):
            l = ttk.Label(self, text=label, cursor="hand2")
            l.grid(row=0, column=i-1, padx=(0 if i==1 else 16,0))
            l.bind("<Button-1>", lambda e, m=i: self._pick(m))
        self._apply_style()
    def _apply_style(self):
        for i, child in enumerate(self.winfo_children(), start=1):
            if i == self.mode.get():
                child.configure(foreground="#14a34a", font=("TkDefaultFont", 10, "underline"))
            else:
                child.configure(foreground="", font=("TkDefaultFont", 10, "normal"))
    def _pick(self, m:int):
        self.mode.set(m); self._apply_style()
        if callable(self.on_select): self.on_select(m)
