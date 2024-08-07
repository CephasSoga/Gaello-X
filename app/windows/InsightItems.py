import os
from pathlib import Path
from typing import Union

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import loadFont


currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class InsightItem(QFrame):
    def __init__(self, imagePathOrUrl: Union[Path, str] = None, title:str = None, text: str = None, parent=None):
        super(InsightItem, self).__init__(parent)
        path = os.path.join(r'UI/insightItem.ui')
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
           exit()

        self.title = title
        self.text = text
        self.imagePathOrUrl = imagePathOrUrl

        # Set a unique object name
        self.setObjectName("InsightItem")

        self.initUI()


    def initUI(self):
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
        regularFontFam = loadFont(r"rsrc/fonts/Quicksand/static/Quicksand-Regular.ttf")
        if regularFontFam:
            regularfont = QFont(regularFontFam)
            regularfont.setPointSize(10)
        else:
            regularfont = QFont("Arial", 10)

        boldFontFam = loadFont(r"rsrc/fonts/Quicksand/static/Quicksand-Bold.ttf")
        if boldFontFam:
            boldfont = QFont(boldFontFam)
            boldfont.setPointSize(12)
        else:
            boldfont = QFont("Arial", 12)


        self.insightTitle.setFont(boldfont)
        self.insightPreview.setFont(regularfont)

    def style(self):
        pass






if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    window = InsightItem('', 'Hello', 'Hello World')
    window.show()
    app.exec_()