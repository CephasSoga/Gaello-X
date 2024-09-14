import os
import asyncio
from io import BytesIO
from typing import List, Dict, Any, Callable

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QWidget, QGridLayout, QApplication
from qasync import QEventLoop, asyncSlot

from app.handlers.AuthHandler import handleAuth
from app.handlers.ShortLiveSeries import Series
from app.handlers.ExportAssets import symbolList
from app.windows.AssetPreviewFrame import AssetPreview
from app.windows.AssetFocusFrame import AssetFocus
from utils.appHelper import setRelativeToMainWindow, adjustForDPI
from utils.databases import mongoGet
from utils.asyncJobs import quickFetchBytes, asyncWrap, ThreadRun
from utils.graphics import chartWithSense
from utils.paths import getFrozenPath
from app.config.scheduler import Schedule
from app.config.balancer import BatchBalance
from app.config.renderer import ViewController


class ExploreAsset(QFrame):
    def __init__(self, connection: MongoClient, async_tasks: list, parent=None):
        super(ExploreAsset, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "exploreAsset.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.async_tasks = async_tasks

        self.symbols = [symbol for symbol in symbolList]
        self.assetPreviews: list[AssetPreview] = []
        self.debounceTimer = QTimer()  # Initialize the debounce timer here
        self.debounceTimer.setSingleShot(True)
        self.debounceTimer.timeout.connect(self.filterItems)

        self.baseImgesUrl = "https://financialmodelingprep.com/image-stock/"

        self.rowLength = ViewController.MAX_DISPLAY_ROWS

        self.allData: List[Dict] = []

        self.initUI()
        QTimer.singleShot(Schedule.NO_DELAY, self.syncGetAllData)
        QTimer.singleShot(Schedule.ASSET_JOB_START_DELAY, self.startLazyLoad)

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.connectSlots()
        self.setupLayout()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.close_.clicked.connect(self.hide) # only hide to preserve state
        self.searchEdit.textChanged.connect(self.onSearchTextChanged)

    def setupLayout(self):
        self.scrollLayout = QGridLayout()
        self.scrollLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setSpacing(ViewController.DEFAULT_SPACING)

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.searchScroll.setWidget(self.scrollWidget)


    def startLazyLoad(self):
        self.lazyLoadTimer = QTimer()
        self.lazyLoadTimer.timeout.connect(lambda:  self.loadNextBatch(self.allData))
        self.lazyLoadTimer.start(BatchBalance.RELOADING_MSEC)  # Load next batch every ... ms

        #self.lazyLoadTimer.singleShot(1000, self.loadNextBatch)

        self.batchSize = BatchBalance.ASSET_REMOTE_LOADING_SIZE
        self.currentIndex = 0

    def loadNextBatch(self, allData: List[Dict]):
        if not allData or len(allData) == 0:
            return
        
        if self.currentIndex >= len(self.symbols):
            self.lazyLoadTimer.stop()
            return

        tasks = []
        for _ in range(self.batchSize):
            if self.currentIndex >= len(self.symbols):
                break
            symbol = self.symbols[self.currentIndex]
            row = self.currentIndex // self.rowLength
            col = self.currentIndex % self.rowLength
            task = self.task(allData, symbol, row, col)
            tasks.append(task)
            self.currentIndex += 1

        self.async_tasks.extend(tasks)

    @asyncSlot()
    async def task(self, allData: List[Dict], symbol: str, row: int, col: dict):
        symbol:str = symbol.symbol
        data = [data for data in allData if data.get("symbol") == symbol]
        if not data or len(data) == 0:
            print(f'> symbol not found: {symbol} | [Not in database] ')
            return
        
        _ = await self.processData(data, symbol, row, col)
        
    async def processData(self, data: List[Dict], symbol: str, row: int, col: int):
        def func_(data):

            symbolData = data[0]

            name = symbolData["name"]
            outlookTarget = symbolData["ticker"]["general"]["outlook"]
            if outlookTarget:
                baseImageUrl = outlookTarget.get("image")
            else:
                baseImageUrl = None

            historicalPriceTarget = symbolData['ticker']['historical']['price']
            if not historicalPriceTarget:
                return
            
            historicalPrice = historicalPriceTarget['historical'] 
            currentPrice = historicalPrice[0]['adjClose']
            previousPrice = historicalPrice[1]['adjClose']
            growth = 100 * (currentPrice - previousPrice)/previousPrice

            reorderedPrices = [point['adjClose'] for point in historicalPrice][::-1]
            reorderedDates = [point['date'] for point in historicalPrice][::-1]
            chartOutPut = chartWithSense(reorderedDates, reorderedPrices)
            chartPixmap = QPixmap(str(chartOutPut))

            return name, baseImageUrl, currentPrice, growth, chartPixmap
        
        res = await ThreadRun(func_, data)
        if res:
            name, baseImageUrl, currentPrice, growth, chartPixmap = res

            alternateImageUrl = f"{self.baseImgesUrl}{symbol}.png"
            imageUrl = baseImageUrl if baseImageUrl else alternateImageUrl
            imagePixmap = await self.getTickerPixmap(imageUrl)

            item = AssetPreview(
                symbol=symbol, 
                name=name, 
                price=currentPrice, 
                growth=growth, 
                imagePixmap=imagePixmap, 
                chartPixmap=chartPixmap, 
                parent=self)
            item.clicked.connect(lambda: self.async_tasks.append(handleAuth(self.connection, 2, self.expand, item, symbol)))
            self.scrollLayout.addWidget(item, row, col)
            self.assetPreviews.append(item)

            await asyncio.sleep(0.1)

    async def getAllData(self):
        asyncMongoGet = asyncWrap(mongoGet)
        self.allData = await asyncMongoGet(collection="ticker", connection=self.connection, limit=int(5e4))
        return self.allData

    def syncGetAllData(self):
        self.async_tasks.append(self.getAllData())

    async def loopRun(self, excutor: Any, func: Callable):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(excutor, func)
        await asyncio.sleep(0.1)

    async def getTickerPixmap(self, url):
        response = await quickFetchBytes(url)
        if not response:
            return

        pixmap = QPixmap()
        bytesObj = response if isinstance(response, bytes) else None
        pixmap.loadFromData(BytesIO(bytesObj).read())
        return pixmap

    def expand(self, item: AssetPreview, symbol):
        expand = AssetFocus(symbol=symbol, connection=self.connection, parent=self.parent())
        setRelativeToMainWindow(expand, self, "center")
        self.installEventFilter(expand)

    def onSearchTextChanged(self):
        self.debounceTimer.start(300)

    def filterItems(self):
        text = self.searchEdit.text().lower()
        self.filteredSymbols = [item for item in self.symbols if text in item.symbol.lower()]

        for preview in self.assetPreviews:
            if preview.symbol not in [fs.symbol for fs in self.filteredSymbols]:
                preview.hide()
            else:
                preview.show()

if __name__ == "__main__":
    import sys
    from qasync import QApplication, QEventLoop

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = ExploreAsset()
    window.show()

    with loop:
        loop.run_forever()
