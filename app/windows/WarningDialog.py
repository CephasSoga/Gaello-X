import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog

from app.windows.Fonts import loadFont

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class Warning(QDialog):
    def __init__(self, title: str, message: str,  parent=None):
        super().__init__(parent)

        path = os.path.join(r"UI/warning.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.title = title
        self.message = message

        self.initUI()

    def initUI(self):
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
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Bold.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(9)
        else:
            font = QFont("Arial", 9)

        for item in self.children():
            item.setFont(font)
