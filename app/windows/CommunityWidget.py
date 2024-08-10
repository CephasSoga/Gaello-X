import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import uic

from app.windows.Fonts import RobotoRegular
from utils.paths import getPath

class JanineCommunity(QWidget):
    def __init__(self, parent=None):
        super(JanineCommunity, self).__init__(parent)
        path = getPath(os.path.join("assets", "UI", "community.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()
    
    def initUI(self):
       self.setWFlags()
       self.setFonts()
       self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def setFonts(self):
        font = RobotoRegular(14) or QFont("Arial", 14)
        for item in self.children():
            item.setFont(font)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)

    def eventFilter(self, obj, event):
        if event.type() == Qt.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)

