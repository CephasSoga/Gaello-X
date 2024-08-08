import os
import asyncio
from io import BytesIO

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QWidget, QGridLayout, QApplication
from qasync import QEventLoop, asyncSlot

from app.windows.AuthHandler import handleAuth
from app.assets.ShortLiveSeries import Series
from app.assets.ExportAssets import symbolList
from app.windows.AssetPreviewFrame import AssetPreview
from app.windows.AssetFocusFrame import AssetFocus
from utils.appHelper import setRelativeToMainWindow
from utils.databases import mongoGet
from utils.asyncJobs import quickFetchBytes
from utils.graphics import chartWithSense

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class ExploreAsset(QFrame):
    def __init__(self, parent=None):
        super(ExploreAsset, self).__init__(parent)
        path = os.path.join("UI", "exploreAsset.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.symbols = [symbol for symbol in symbolList]
        self.assetPreviews: list[AssetPreview] = []
        self.debounceTimer = QTimer()  # Initialize the debounce timer here
        self.debounceTimer.setSingleShot(True)
        self.debounceTimer.timeout.connect(self.filterItems)

        self.baseImgesUrl = "https://financialmodelingprep.com/image-stock/"

        self.rowLength = 4

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()
        self.setupLayout()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)
        self.searchEdit.textChanged.connect(self.onSearchTextChanged)

    def setupLayout(self):
        self.scrollLayout = QGridLayout()
        self.scrollLayout.setContentsMargins(10, 10, 10, 10)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setSpacing(10)

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.searchScroll.setWidget(self.scrollWidget)

        self.startLazyLoad()

    def startLazyLoad(self):
        self.lazyLoadTimer = QTimer()
        self.lazyLoadTimer.timeout.connect(self.loadNextBatch)
        self.lazyLoadTimer.start(1000)  # Load next batch every 100 ms

        #self.lazyLoadTimer.singleShot(1000, self.loadNextBatch)

        self.batchSize = 5
        self.currentIndex = 0

    def loadNextBatch(self):
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
            task = self.task(symbol, row, col)
            tasks.append(task)
            self.currentIndex += 1

        asyncio.ensure_future(asyncio.gather(*tasks))

    @asyncSlot()
    async def task(self, symbol, row, col):
        symbol:str = symbol.symbol
        data = mongoGet(collection="ticker", symbol=symbol)
        if not data:
            print(f'{symbol} Not Found.')
            return

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

        alternateImageUrl = f"{self.baseImgesUrl}{symbol}.png"
        imageUrl = baseImageUrl if baseImageUrl else alternateImageUrl
        imagePixmap = await self.getTickerPixmap(imageUrl)

        item = AssetPreview(symbol, name, currentPrice, growth, imagePixmap, chartPixmap, self)
        item.clicked.connect(lambda: handleAuth(2, self.expand, item, symbol))
        self.scrollLayout.addWidget(item, row, col)
        self.assetPreviews.append(item)

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
        expand = AssetFocus(symbol, self.parent())
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
