import os
from typing import Union
from pathlib import Path


from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt

from utils.paths import getFrozenPath

class Attachment(QFrame):

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
        self.setWFlags()
        self.setContents()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setContents(self):
        self.attachmentLabel.setText(self.filePath)
    
    def connectSlots(self):
        self.removeButton.clicked.connect(self.deleteLater)
