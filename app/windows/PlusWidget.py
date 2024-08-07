import os

from PyQt5 import uic

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont
from PyQt5 import uic

from app.windows.Fonts import loadFont

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

# Load the UI file into a QUiLoader object
class ProjectHome(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if os.path.exists("UI/plusWidget.ui"):
            uic.loadUi("UI/plusWidget.ui", self)
        else:
            exit()
        
        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    
    def setFonts(self):
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Regular.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(14)
        else:
            font = QFont("Arial", 14)
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