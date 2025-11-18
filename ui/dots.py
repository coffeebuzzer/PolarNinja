from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen

class DotBar(QWidget):
    def __init__(self, count=38):
        super().__init__()
        self.count=count
        self.colors=[(0,0,0)]*count
        self.setMinimumHeight(100)
    def set_colors(self, rgbs):
        self.colors=list(rgbs)+[(0,0,0)]*(self.count-len(rgbs))
        self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); pad=24; y=self.height()-40
        spacing=(w-2*pad)/(self.count-1)
        for i,(r,g,b) in enumerate(self.colors[:self.count]):
            x=pad+i*spacing
            p.setBrush(QColor(r,g,b))
            p.setPen(QPen(QColor("#eeeeee"),1))
            p.drawEllipse(int(x-12), int(y-12), 24,24)
        p.setPen(QColor("#d0d0d0"))
        for i in range(self.count):
            x=pad+i*spacing
            p.drawText(int(x-6), y+26, str(i+1))
