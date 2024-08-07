import os
from typing import Optional
from PyQt5 import uic
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import loadFont
from app.windows.ArticleExpandFrame import ArticleExpand
from utils.appHelper import *

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class ArticleItem(QFrame):
    clicked = pyqtSignal()
    def __init__(self,
        title: str = None,
        imagePixmap: Optional[QPixmap] = None,
        author: str = None,
        source: str = None,
        date: str = None,
        content = None,
        link: str = None,
        tickers: str = None,
        parent = None
        ):
        super().__init__(parent)
        path = os.path.join(r'UI/articleItem.ui')
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.title = title
        self.imagePixmap = imagePixmap
        self.author = author
        self.content = content
        self.date = date
        self.link = link
        self.tickers = tickers
        self.source = source

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.setContents()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setContents(self):
        if self.imagePixmap:
            self.imageLabel.setPixmap(self.imagePixmap)

        self.titleLabel.setText(self.title)
        self.authorLabel.setText(self.author)
        self.sourceLabel.setText(self.source)
    
    def setFonts(self):
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Semibold.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(9)
        else:
            font = QFont("Arial", 9)

        for obj in [self.titleLabel]:
            obj.setFont(font)

        tinyFontFam = loadFont(r"rsrc/fonts/Exo_2/static/Exo2-Light.ttf")
        if tinyFontFam:
            tinyFont = QFont(tinyFontFam)
            tinyFont.setPointSize(9)
        else:
            tinyFont = QFont("Arial", 9)
        
        for obj in [self.authorLabel, self.sourceLabel]:
            obj.setFont(tinyFont)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # Emit the clicked signal

    def connectSlots(self):
        self.clicked.connect(self.expand)

    def expand(self):
        self.levelFourAncestor = self.parent().parent().parent().parent() # likely stands for MarketSummaryWindow
        expandItem = ArticleExpand(
        title=self.title,
        author=self.author,
        source=self.source,
        date=self.date,
        content=self.content,
        link=self.link,
        tickers=self.tickers)

        setRelativeToMainWindow(expandItem, self.levelFourAncestor, "center")
        #expandItem.show()
