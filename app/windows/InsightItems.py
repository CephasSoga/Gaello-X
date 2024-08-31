import os
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Union
from dataclasses import dataclass

from PyQt5 import uic
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame

from app.windows.Styles import chatScrollBarStyle
from app.config.fonts import QuicksandBold, QuicksandRegular, RobotoBold, FontSizePoint
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI, setRelativeToMainWindow
from utils.asyncJobs import quickFetchBytes

@dataclass
class Insight:
    title: str
    description: str
    date: str
    content: str
    image: bytes
    urls: list[str]
    labels: list[str]
    tags: list[str]

class InsightExpand(QFrame):
    def __init__(self, insight: Insight, parent=None):
        
        super(InsightExpand, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", 'UI', 'insightExpand.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
           raise FileNotFoundError(f"{path} not found")

        self.insight = insight

        self.initUI()
        QTimer.singleShot(10, self.syncSetContents)

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setFonts()
        self.connectSlots()
    
    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    async def setContents(self):
        if self.insight.image is None:
            image_data = None
        else:
            image_data = self.insight.image
        
        imagePixmap = await self.getPixmapFromBytes(image_data)
        if imagePixmap:
            self.imageLabel.setPixmap(imagePixmap)
        else:
            fallbackPixmap = self.getFallbackPixmap()
            if not fallbackPixmap:
                self.imageLabel.setText("No Image")
            self.imageLabel.setPixmap(fallbackPixmap)

        self.titleEdit.setHtml(self.insight.title)
        self.titleEdit.setWordWrapMode(True)
        self.titleEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.titleEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.labelsEdit.setHtml("Labels: " + ", ".join(self.insight.labels))
        self.labelsEdit.setWordWrapMode(True)
        self.labelsEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.labelsEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.tagsEdit.setHtml("Tags: " + ", ".join(self.insight.tags))
        self.tagsEdit.setWordWrapMode(True)
        self.tagsEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.tagsEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.contentEdit.setHtml(self.insight.content)
        self.contentEdit.setWordWrapMode(True)
        self.contentEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.contentEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.descriptionEdit.setHtml(self.insight.description)
        self.descriptionEdit.setWordWrapMode(True)
        self.descriptionEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.descriptionEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    async def getPixmapFromBytes(self, bytes_array: Union[bytes, None]):
        def func(bytes_array: Union[bytes, None]):
            if not bytes_array:
                return None
            
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(bytes_array).read())
            return pixmap
        
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, bytes_array)
    
    def getFallbackPixmap(self):
        import random
        i = 0
        path = None

        pathTargets = [
            os.path.join("assets", "images", "fallback.jpg"),
            os.path.join("assets", "images", "fallback2.jpg"),
            os.path.join("assets", "images", "fallback3.jpg"),
            os.path.join("assets", "images", "fallback4.jpg"),
            os.path.join("assets", "images", "fallback5.jpg"),
            os.path.join("assets", "images", "fallback6.jpg"),
            os.path.join("assets", "images", "fallback7.jpg"),
            os.path.join("assets", "images", "fallback8.jpg"),
            os.path.join("assets", "images", "fallback9.jpg"),
            os.path.join("assets", "images", "fallback10.jpg"),
            os.path.join("assets", "images", "fallback11.jpg"),
            os.path.join("assets", "images", "fallback12.jpg"),
            os.path.join("assets", "images", "fallback13.jpg"),
            os.path.join("assets", "images", "fallback14.jpg"),
            os.path.join("assets", "images", "fallback15.jpg"),
            os.path.join("assets", "images", "fallback16.jpg"),  
        ]
        while path is None or not os.path.exists(path):
            path_ = random.choice(pathTargets)

            if os.path.exists(path_):
                path = path_
                break

            if i == len(pathTargets) - 1 and not path:
                return None
            
            i += 1

        pixmap = QPixmap(path)

        return pixmap

    def syncSetContents(self):
        asyncio.ensure_future(self.setContents())

    def connectSlots(self):
        self.close_.clicked.connect(self.close)
    
    def setFonts(self):
        size = FontSizePoint
        titleFont = RobotoBold(size.BIGGER) or QFont('Arial', size.BIGGER)
        contentFont = QuicksandRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        tinyFont = QuicksandRegular(size.TINY) or QFont("Arial", size.TINY)

        self.titleEdit.setFont(titleFont)
        self.contentEdit.setFont(contentFont)
        self.tagsEdit.setFont(tinyFont)
        self.labelsEdit.setFont(tinyFont)
        self.descriptionEdit.setFont(tinyFont)

class InsightItem(QFrame):
    def __init__(self, insight: Insight, parent=None):

        super(InsightItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", 'UI', 'insightItem.ui'))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
           raise FileNotFoundError(f"{path} not found")
        
        self.insight = insight

        self.title = self.insight.title
        self.text = self.insight.content
        self.image = self.insight.image

        # Set a unique object name
        self.setObjectName("Insight Expand")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.setFonts()
        self.connectSlots()

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

    def connectSlots(self):
        self.moreButton.clicked.connect(self.expand)

    def expand(self):
        parent_ = self.parent()
        expandItem = InsightExpand(
            self.insight
        )
        
        setRelativeToMainWindow(expandItem, parent_, 'center')
