
import os

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import loadFont
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
        path = os.path.join(r'UI/articleExpand.ui')
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

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
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Regular.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(10)
        else:
            font = QFont("Arial", 10)

        for obj in [self.mainTextEdit]:
            obj.setFont(font)

        titleFontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-SemiBold.ttf")
        if titleFontFam:
            titleFont = QFont(titleFontFam)
            titleFont.setPointSize(12)
        else:
            titleFont = QFont("Arial", 12)

        if self.title:
            font.setPointSize(12)
            self.titleLabel.setFont(titleFont)

        tinyFontFam = loadFont(r"rsrc/fonts/Exo_2/static/Exo2-Light.ttf")
        if tinyFontFam:
            tinyFont = QFont(tinyFontFam)
            tinyFont.setPointSize(9)
        else:
            tinyFont = QFont("Arial", 9)
        
        for obj in [self.authorLabel, self.sourceLabel, self.dateLabel, self.tagLabel]:
            obj.setFont(tinyFont)



