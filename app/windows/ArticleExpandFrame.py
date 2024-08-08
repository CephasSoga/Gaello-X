
import os

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import *
from app.windows.Styles import chatScrollBarStyle

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

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
        path = os.path.join('UI', 'articleExpand.ui')
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
        font = RobotoRegular(10) or QFont("Arial", 10)
        for obj in [self.mainTextEdit]:
            obj.setFont(font)

        titleFont = RobotoSemiBold(12) or QFont("Arial", 12)
        if self.title:
            self.titleLabel.setFont(titleFont)

        tinyFont = Exo2Light(9) or QFont("Arial", 9)
        for obj in [self.authorLabel, self.sourceLabel, self.dateLabel, self.tagLabel]:
            obj.setFont(tinyFont)



