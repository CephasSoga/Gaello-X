import os
from pathlib import Path
from typing import Union

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from dataclasses import dataclass

from app.config.fonts import QuicksandBold, QuicksandRegular, FontSizePoint
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

@dataclass
class Insight:
    title: str
    description: str
    date: str
    description: str
    content: str
    image_url: str | list[str]
    urls: list[str]
    labels: list[str]
    tags: list[str]

class InsightItem(QFrame):
    def __init__(self, insight: Insight, parent=None):
        self.insight = insight
        super(InsightItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", 'UI', 'insightItem.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
           raise FileNotFoundError(f"{path} not found")

        self.title = self.insight.title
        self.text = self.insight.content
        self.imageUrl = self.insight.image_url

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
        size = FontSizePoint
        boldFont = QuicksandBold(size.BIG) or QFont("Arial", size.BIG)
        regularFont = QuicksandRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
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