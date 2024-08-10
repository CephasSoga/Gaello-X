import os
from typing import Optional
from PyQt5 import uic
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import *
from app.windows.ArticleExpandFrame import ArticleExpand
from utils.appHelper import setRelativeToMainWindow
from utils.paths import getFrozenPath

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
        path = getFrozenPath(os.path.join("assets", 'UI', 'articleItem.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

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
        font = RobotoSemiBold(9) or QFont('Arial', 9)
        for obj in [self.titleLabel]:
            obj.setFont(font)
        
        tinyFont = Exo2Light(9) or QFont("Arial", 9)
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
