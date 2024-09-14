
import os

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from app.config.fonts import RobotoRegular, RobotoSemiBold, Exo2Light, FontSizePoint
from app.windows.Styles import chatScrollBarStyle
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

# import resources
import app.config.resources

class ArticleExpand(QFrame):
    def __init__(self,
        title: str = None,
        author: str = None,
        source: str = None,
        date: str = None,
        content: str = None,
        link: str = None,
        tickers: str = None,
        parent = None
        ):
        super().__init__(parent)
        path = getFrozenPath(os.path.join("assets", 'UI', 'articleExpand.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.title = title
        self.author = author
        self.content = content
        self.date = date
        self.link = link
        self.tickers = tickers
        self.source = source

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)


    def setContents(self):
        self.mainTextEdit.setHtml(self.content)
        #self.mainTextEdit.setPlainText(mainText)
        self.mainTextEdit.setWordWrapMode(True)
        self.mainTextEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.mainTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.authorLabel.setText(self.author)
        self.titleLabel.setText(self.title)
        self.dateLabel.setText(self.date)
        self.sourceLabel.setText(self.source)

        self.refTextEdit.setHtml(self.link)
    
    def setFonts(self):
        size = FontSizePoint
        font = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        for obj in [self.mainTextEdit]:
            obj.setFont(font)

        titleFont = RobotoSemiBold(size.BIG) or QFont("Arial", size.BIG)
        if self.title:
            self.titleLabel.setFont(titleFont)

        tinyFont = Exo2Light(size.SMALL) or QFont("Arial", size.SMALL)
        for obj in [self.authorLabel, self.sourceLabel, self.dateLabel, self.tagLabel]:
            obj.setFont(tinyFont)



