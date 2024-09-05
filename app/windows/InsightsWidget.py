import os
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Callable

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

from app.config.fonts import RobotoRegular, MontserratRegular, FontSizePoint
from app.windows.InsightItems import InsightItem
from app.inferential.ExportInsights import insights
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI
from app.config.renderer import ViewController
from utils.databases import mongoGet
from utils.asyncJobs import asyncWrap, enumerate_async
from app.config.balancer import BatchBalance
from app.config.renderer import ViewController
from app.handlers.AuthHandler import  handleAuth
from utils.appHelper import stackOnCurrentWindow

@dataclass
class Insight:
    title: str
    date: str
    description: str
    content: str
    image: bytes
    urls: list[str]
    labels: list[str]
    tags: list[str]

class JanineInsights(QWidget):
    gatheredInsights = pyqtSignal(list)
    def __init__(self, connection: MongoClient, parent=None):
        super(JanineInsights, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "insightsWidget.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.initUI()
        QTimer.singleShot(10, self.syncSetContents)


    def initUI(self):
        adjustForDPI(self)
        self.setupWFlags()
        self.connectSlots()
        self.setupLayout()
        self.setFonts()

    def mousePressEvent(self, event):
        self.open()
        super().mousePressEvent(event)
        

    def open(self):
        asyncio.ensure_future(handleAuth(2, stackOnCurrentWindow, self))
        

    def setupLayout(self):
        self.insightslayout = QGridLayout()
        self.insightslayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.insightslayout.setAlignment(Qt.AlignTop)
        self.insightslayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.widget = QWidget()
        self.widget.setLayout(self.insightslayout)

        self.scrollArea.setWidget(self.widget)
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setupWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)


    def connectSlots(self):
        self.close_.clicked.connect(self.close)


    def eventFilter(self, obj, event):
        if event.type() == Qt.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def startLazyLoad(self, execFunc: Callable, timeout: int = BatchBalance.RELOADING_MSEC, *args, **kwargs):
        self.lazyLoadTimer = QTimer()
        self.lazyLoadTimer.singleShot(timeout, lambda: execFunc(*args, **kwargs))
        self.BatchSize = BatchBalance.MARKET_REMOTE_LOADING_SIZE
    
    @pyqtSlot()
    async def gatherInsights(self):
        async_mongGet = asyncWrap(mongoGet)
        today = datetime.now().date().isoformat()
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        latest_collection = today

        data = await async_mongGet(database='insights', collection=latest_collection, limit=int(1e6), connection=self.connection)
        if not data:
            latest_collection = yesterday
            data = await async_mongGet(database='insights', collection=latest_collection, limit=int(1e6), connection=self.connection)
            if not data:
                yield {}
        for doc in data:
            yield {
                "title": doc["title"],
                "description": doc["description"],
                "date": doc["date"],
                "content": doc["content"],
                "image": doc["image"],
                "urls": doc["urls"],
                "labels": doc["labels"],
                "tags": doc["tags"],

            }
    
    @pyqtSlot()
    async def setContents(self):
        async for idx, doc in enumerate_async(self.gatherInsights()):
            try:
                max_per_row = ViewController.DEFAULT_DISPLAY_ROWS
                row = idx // max_per_row
                col = idx % max_per_row
                insight = Insight(**doc)
                insight_widget = InsightItem(insight, self)
                self.insightslayout.addWidget(insight_widget, row, col)
            except TypeError: #  in case no  data was found
                return

    @pyqtSlot()
    def syncSetContents(self):
        asyncio.ensure_future(self.setContents())


    def setFonts(self):
        size = FontSizePoint
        regularFont = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        tinyFont = MontserratRegular(size.TINY) or QFont("Arial", size.TINY)
        self.filterLabel.setFont(regularFont)
        self.tuneLabel.setFont(regularFont)
        self.temperatureLabel.setFont(tinyFont)
        self.audacityLabel.setFont(tinyFont)
        self.cycleLabel.setFont(tinyFont)
        self.subjectsCombo.setFont(tinyFont)
        self.locationsCombo.setFont(tinyFont)
        self.assetsCombo.setFont(tinyFont)


if __name__ == "__main__":
    import sys
    from qasync import QApplication, QEventLoop

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = JanineInsights()
    window.show()

    with loop:
        loop.run_forever()