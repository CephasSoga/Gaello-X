import os

from PyQt5 import uic

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont
from PyQt5 import uic

from app.config.fonts import RobotoRegular, FontSizePoint
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

# Load the UI file into a QUiLoader object
class ProjectHome(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "plusWidget.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    
    def setFonts(self):
        size = FontSizePoint
        font = RobotoRegular(size.BIGGER) or QFont("Arial", size.BIGGER)
        self.setFont(font)
        for item in self.children():
            item.setFont(font)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)

    def eventFilter(self, obj, event):
        if event.type() == Qt.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)