import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QFrame

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class Warning(QFrame):
    def __init__(self, parent=None):
        super(Warning, self).__init__(parent)
        uic.loadUi(r"UI/warnings.ui", self)
        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.setupAppearance()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setupAppearance(self):
        pass

    def warning(self, title, message):
        self.title.setText(title)
        self.text.setText(message)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)