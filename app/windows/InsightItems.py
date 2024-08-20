import os
from pathlib import Path
from typing import Union

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import QuicksandBold, QuicksandRegular
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

class InsightItem(QFrame):
    def __init__(self, imagePathOrUrl: Union[Path, str] = None, title:str = None, text: str = None, parent=None):
        super(InsightItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", 'UI', 'insightItem.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
           raise FileNotFoundError(f"{path} not found")

        self.title = title
        self.text = text
        self.imagePathOrUrl = imagePathOrUrl

        # Set a unique object name
        self.setObjectName("InsightItem")

        self.initUI()


    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.style()
        self.setFonts()

    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    def setContents(self):
        #self.insightImage.setPixmap(imagePath)
        self.insightTitle.setText(self.title)
        self.insightPreview.setText(self.text)

    def setFonts(self):
        boldFont = QuicksandBold(12) or QFont("Arial", 12)
        regularFont = QuicksandRegular(10) or QFont("Arial", 10)
        self.insightTitle.setFont(boldFont)
        self.insightPreview.setFont(regularFont)

    def style(self):
        pass






if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    window = InsightItem('', 'Hello', 'Hello World')
    window.show()
    app.exec_()