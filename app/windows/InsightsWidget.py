import os
import re
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Callable

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

from app.config.fonts import RobotoRegular, MontserratRegular, FontSizePoint
from app.windows.InsightItems import InsightItem
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI, clearLayout
from utils.databases import mongoGet
from utils.asyncJobs import asyncWrap, enumerate_async
from utils.logs import timer
from app.config.balancer import BatchBalance
from app.config.renderer import ViewController
from app.config.scheduler import Schedule

# import resources
import app.config.resources

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
    filterMessage = pyqtSignal(str)
    def __init__(self, connection: MongoClient, async_tasks: list[asyncio.Task], parent=None):
        super(JanineInsights, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "insightsWidget.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.async_tasks = async_tasks

        self.debouncerTimer = QTimer()  # Initialize the debounce timer here
        self.debouncerTimer.setSingleShot(True)
        self.debouncerTimer.timeout.connect(lambda: self.async_tasks.append(self.filterItems()))
        #self.debouncerTimer.timeout.connect(lambda: asyncio.ensure_future(self.filterItems()))

        self.initUI()
        QTimer.singleShot(10, self.syncSetContents)


    def initUI(self):
        adjustForDPI(self)
        self.setupWFlags()
        self.connectSlots()
        self.setupLayout()
        self.setFonts()

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
        self.filterEdit.textChanged.connect(self.onfilterChanged)
        self.filterMessage.connect(self.updateInfoLabel)

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
                "labels": set([label.lower() for label in doc["labels"]]),
                "tags": set([tag.lower() for tag in doc["tags"]]),

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
        self.async_tasks.append(self.setContents())


    def setFonts(self):
        size = FontSizePoint
        regularFont = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        tinyFont = MontserratRegular(size.TINY) or QFont("Arial", size.TINY)
        self.filterLabel.setFont(regularFont)
        self.tuneLabel.setFont(regularFont)
        self.temperatureLabel.setFont(tinyFont)
        self.audacityLabel.setFont(tinyFont)
        self.cycleLabel.setFont(tinyFont)
        self.filterEdit.setFont(tinyFont)

    def onfilterChanged(self):
        self.debouncerTimer.start(Schedule.CHANGE_DELAY)

    async def filterItems(self):
        matching_insight = []

        filterText: str = self.filterEdit.text()

        if not (filterText):
            self.filterInfoLabel.clear()
            return

        filters = re.split(r"[ ,;|]+", filterText.strip())
        self.filterMessage.emit("Filtering")

        def isSubset(filters: List[str], labels: List[str]):
            labels = [label.strip().lower() for label in labels]
            filters = [filter_.strip().lower() for filter_ in filters]
            return len(set(filters).intersection(set(labels))) > 0

        async for idx, doc in enumerate_async(self.gatherInsights()):
            if isSubset(filters, doc["labels"]) or isSubset(filters, doc["tags"]):
                matching_insight.append(doc)

        if not matching_insight:
            self.filterMessage.emit('No matches found.')
            return

        clearLayout(self.insightslayout) # clear the layout first
        for idx, doc in enumerate(matching_insight):
            try:
                max_per_row = ViewController.DEFAULT_DISPLAY_ROWS
                row = idx // max_per_row
                col = idx % max_per_row
                insight = Insight(**doc)
                insight_widget = InsightItem(insight, self)
                self.insightslayout.addWidget(insight_widget, row, col)
                self.filterMessage.emit(f"Found {len(matching_insight)} matchs.")
            except TypeError: #  in case no  data was found
                return

    def updateInfoLabel(self, message: str):
        def delay(func: Callable,  ms_delay: int):
            QTimer.singleShot(ms_delay, func)
        i = 0
        k  = 2
        repeat_delay = 50
        max_iter = 3
        if message.endswith('.'):
            self.filterInfoLabel.setText(message)
        else:
            while i <= max_iter:
                delay(lambda: self.filterInfoLabel.setText(f'{message} .'),  repeat_delay)
                delay(lambda: self.filterInfoLabel.setText(f'{message} ..'),  repeat_delay * k)
                delay(lambda: self.filterInfoLabel.setText(f'{message} ...'),  repeat_delay * (k ** 2))
                if i == max_iter:
                    self.filterInfoLabel.setText(f'{message} ...')
                i += 1
                k += 1


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