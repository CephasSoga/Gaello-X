import os

from PyQt5 import uic
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame
from utils.paths import getPath

class Help(QFrame):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        path = getPath(os.path.join("assets", "UI", "help.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)