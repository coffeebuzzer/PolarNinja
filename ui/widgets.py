from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPolygon



class CircleButton(QWidget):
    clicked = Signal()

    def __init__(self, icon: str, tooltip: str = ""):
        super().__init__()
        self.icon = icon  # "play","pause","stop"
        self.setToolTip(tooltip)
        self.setFixedSize(120, 120)  # app will shrink to 90x90

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # outer circle
        r = self.rect().adjusted(6, 6, -6, -6)
        p.setBrush(QColor("#22c55e"))
        p.setPen(QPen(Qt.black, 2))
        p.drawEllipse(r)

        # icon
        p.setBrush(QBrush(Qt.black))
        p.setPen(Qt.NoPen)
        cx = r.center().x()
        cy = r.center().y()

        if self.icon == "play":
            # Classic play triangle, using QPoint + QPolygon (this is what PySide expects)
            pts = [
                QPoint(cx - 14, cy - 22),
                QPoint(cx + 24, cy),
                QPoint(cx - 14, cy + 22),
            ]
            poly = QPolygon(pts)
            p.drawPolygon(poly)

        elif self.icon == "pause":
            p.drawRect(cx - 20, cy - 26, 15, 52)
            p.drawRect(cx + 5,  cy - 26, 15, 52)

        elif self.icon == "stop":
            p.drawRect(cx - 22, cy - 22, 44, 44)


class SeekBar(QWidget):
    seek = Signal(float)  # ratio 0..1

    def __init__(self):
        super().__init__()
        self._progress = 0.0
        self.setFixedHeight(28)

    def set_progress(self, x: float):
        self._progress = max(0.0, min(1.0, x))
        self.update()

    def mousePressEvent(self, e):
        x = e.position().x() / max(1, self.width())
        self.seek.emit(float(x))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        # outer bar
        p.setPen(QPen(QColor("#0f172a"), 3))
        p.setBrush(QColor("#14532d"))
        p.drawRoundedRect(rect, 12, 12)

        # fill
        fill = QRectF(
            rect.left(),
            rect.top(),
            rect.width() * self._progress,
            rect.height(),
        )
        p.setBrush(QColor("#22c55e"))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(fill, 12, 12)

        # thumb
        x = rect.left() + rect.width() * self._progress
        p.setBrush(QColor("#b6ffb6"))
        p.setPen(QPen(Qt.black, 1))
        p.drawEllipse(QPointF(x, rect.center().y()), 10, 10)


class DMXStatus(QWidget):
    """
    Top-right DMX indicator + Online/Offline toggle.

    Public API used by app.py:
      - DMXStatus(toggle_cb)
      - set_online(bool)
      - set_status(state_str)

    DMXEngine currently emits states like: 'green', 'red', 'offline'
    We treat:
      - 'green', 'ok', 'connected', 'ready' -> GREEN dot
      - anything else -> RED dot
    """

    def __init__(self, toggle_cb=None, parent=None):
        super().__init__(parent)
        self._toggle_cb = toggle_cb
        self._online = True
        self._last_status = "offline"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl_off = QLabel("Offline")
        lbl_off.setStyleSheet("color:#ffffff; font-size:11px;")
        layout.addWidget(lbl_off)

        # Simple pill toggle based on QCheckBox
        self.switch = QCheckBox()
        self.switch.setChecked(True)
        self.switch.setCursor(Qt.PointingHandCursor)
        self.switch.stateChanged.connect(self._on_switch_state_changed)

        # NOTE: No 'content:' or ::before hacks – Qt style sheets don't support that.
        # This gives you a clean pill that flips color when toggled.
        self.switch.setStyleSheet("""
        QCheckBox::indicator {
            width: 40px;
            height: 20px;
        }
        QCheckBox::indicator:unchecked {
            border-radius: 10px;
            background: #444444;
        }
        QCheckBox::indicator:checked {
            border-radius: 10px;
            background: #16a34a;
        }
        """)
        layout.addWidget(self.switch)

        lbl_on = QLabel("Online")
        lbl_on.setStyleSheet("color:#ffffff; font-size:11px;")
        layout.addWidget(lbl_on)

        # Little status dot to mirror DMX health
        self.dot = QLabel()
        self.dot.setFixedSize(14, 14)
        self.dot.setStyleSheet("border-radius: 7px; background: #aa0000;")
        layout.addWidget(self.dot)

    # --- internal helpers ---

    def _set_dot_color(self, css_color: str):
        self.dot.setStyleSheet(
            f"border-radius: 7px; background: {css_color};"
        )

    def _on_switch_state_changed(self, state):
        online = (state == Qt.Checked)
        self._online = online

        # When going offline, force solid red and ignore DMX updates
        if not online:
            self._set_dot_color("#aa0000")
        else:
            # Going back online – restore last known DMX status meaning
            self.set_status(self._last_status)

        if self._toggle_cb is not None:
            self._toggle_cb(online)

    # --- API called from App ---

    def set_online(self, online: bool):
        """Called by App when loading settings / toggling programmatically."""
        self._online = bool(online)
        self.switch.blockSignals(True)
        self.switch.setChecked(self._online)
        self.switch.blockSignals(False)

        if not self._online:
            self._set_dot_color("#aa0000")
        else:
            self.set_status(self._last_status)

    def set_status(self, state: str):
        """
        state is a string from DMXEngine:
          - 'green' / 'red' / 'offline'
        plus we also allow 'ok' / 'connected' / 'ready' as 'green'.
        """
        self._last_status = state or "unknown"

        # In Offline mode we ignore DMX status – dot stays red.
        if not self._online:
            self._set_dot_color("#aa0000")
            return

        s = (state or "").lower()
        if s in ("green", "ok", "connected", "ready"):
            self._set_dot_color("#00ff66")
        else:
            self._set_dot_color("#aa0000")
