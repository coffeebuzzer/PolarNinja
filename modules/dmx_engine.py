import threading
import time

try:
    import serial
except Exception:
    serial = None


class DMXEngine:
    """Lightweight DMX presence checker with online/offline gate.

    - Opens a given COM port at 57,600 baud.
    - Periodically checks that the port is still alive.
    - Emits simple status strings via the callback:
        "green" -> DMX interface present / port open
        "red"   -> DMX missing / error / offline
    """

    def __init__(self, com_port, status_cb=lambda s: None):
        self.com_port = com_port
        self.status_cb = status_cb
        self.online = True

        self._stop = threading.Event()
        self._thread = None
        self._ser = None

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def start(self):
        """Start the background monitoring thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop monitoring and close the port."""
        self._stop.set()
        self._close()

    def set_online(self, online: bool):
        """Enable/disable DMX checking (legacy hook)."""
        self.online = bool(online)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, state: str):
        try:
            self.status_cb(state)
        except Exception:
            # Never let DMX status kill the app
            pass

    def _open(self) -> bool:
        """Try to open the COM port. Returns True on success."""
        if serial is None:
            return False
        try:
            # DMXKing UltraDMX Micro uses 57,600 baud in DMX-USB Pro mode.
            self._ser = serial.Serial(f"COM{self.com_port}", 57600, timeout=0)
            return True
        except Exception:
            self._ser = None
            return False

    def _close(self):
        """Close the COM port if it is open."""
        try:
            if self._ser and getattr(self._ser, "is_open", False):
                self._ser.close()
        except Exception:
            # Ignore any OS/USB errors on shutdown
            pass
        finally:
            self._ser = None

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run(self):
        """Background loop: keep an eye on the COM port and emit status."""
        was_ok = False

        while not self._stop.is_set():
            if not self.online:
                # Offline mode: treat as red and don't touch the port
                if was_ok:
                    was_ok = False
                    self._emit("red")
                time.sleep(0.25)
                continue

            # If we think we have a port but it's been closed, drop it
            if self._ser and hasattr(self._ser, "is_open") and not self._ser.is_open:
                self._close()
                if was_ok:
                    was_ok = False
                    self._emit("red")

            # No open port: try to open it
            if not self._ser and not self._open():
                if was_ok:
                    was_ok = False
                    self._emit("red")
                time.sleep(0.5)
                continue

            # At this point we have an open port. Poke it lightly.
            try:
                # Writing empty bytes is effectively a no-op but will throw
                # if the USB/COM device disappeared.
                if self._ser:
                    self._ser.write(b"")
                if not was_ok:
                    was_ok = True
                    self._emit("green")
            except Exception:
                # Something went wrong (likely unplugged) -> mark red.
                self._close()
                if was_ok:
                    was_ok = False
                    self._emit("red")

            time.sleep(0.2)

        # Thread is shutting down
        self._close()
