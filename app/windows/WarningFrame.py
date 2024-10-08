import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QFrame

from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

# import resources
import app.config.resources

class Warning(QFrame):
    def __init__(self, parent=None):
        super(Warning, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "warnings.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()

    def initUI(self):
        adjustForDPI(self)
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