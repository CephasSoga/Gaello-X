import os
from typing import Union
from pathlib import Path


from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, pyqtSignal

from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

# import resources
import app.config.resources

class Attachment(QFrame):
    isDeleted = pyqtSignal()
    def __init__(self, filePath: Union[str, Path], parent=None):
        super().__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "attachment.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.filePath = filePath
        self.initUI()


    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setContents(self):
        self.attachmentLabel.setText(self.filePath)
    
    def connectSlots(self):
        self.removeButton.clicked.connect(self.selfDelete)
    
    def selfDelete(self):
        self.isDeleted.emit()
        self.deleteLater()
