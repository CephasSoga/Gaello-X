import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog

from app.config.fonts import RobotoBold, FontSizePoint
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

class Warning(QDialog):
    def __init__(self, title: str, message: str,  parent=None):
        super().__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "warning.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.title = title
        self.message = message

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setFonts()
        self.connectSlots()
        self.setContents()


    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def connectSlots(self):
        self.OK.clicked.connect(self.close)

    def setContents(self):
        self.titleLabel.setText(self.title)
        self.messageLabel.setText(self.message)


    def setFonts(self):
        size = FontSizePoint
        font = RobotoBold(size.SMALL) or QFont("Arial", size.SMALL)
        for item in self.children():
            item.setFont(font)
