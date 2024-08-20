import os
import asyncio
from io import BytesIO
from typing import List, Callable

from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget, QApplication
from qasync import QEventLoop, asyncSlot

from utils.asyncJobs import quickFetchBytes, quickFetchJson
from utils.databases import mongoGet
from utils.graphics import chartWithSense
from app.windows.ForexItemFrame import ForexItem
from app.windows.IndexItemFrame import IndexItem
from app.windows.CryptoItemFrame import CryptoItem
from app.windows.CommodityItemFrame import CommodityItem
from app.windows.Styles import scrollBarStyle
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

class ExploreMarket(QFrame):
    def __init__(self, parent=None):
        super(ExploreMarket, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "exploreMarket.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.flagsSource = "https://flagcdn.com"
        self.chartDisplayWidth, self.chartDisplayHeigth = 120, 60

        self.forexList = ['ARS/MXN', 'TND/ZAR', 'XAG/RUB', 'ILS/NOK']
        self.forexCurrentIndex = 0
        self.forexBatchSize = 1
        self.forexRawSize = 2
        
        self.indicesList = ['S &P 500', 'S & P 500', 'NASDAQ Composite', 'Russell 2000', 'Dow Jones Industrial Average']
        self.indicesCurrentIndex = 0
        self.indicesBatchSize = 1
        self.indicesRawSize = 2

        self.cryptosList = ['BTCUSD', "ETHUSD", "DERPUSD", "BTRSTUSD", "ARQUSD", "ALIENUSD"]
        self.cryptosCurrentIndex = 0
        self.cryptosBatchSize = 1
        self.cryptosRawSize = 2

        self.commoditiesList = ["ESUSD", "GOLDUSD"]
        self.commoditiesCurrentIndex = 0
        self.commoditiesBatchSize = 1
        self.commoditiesRawSize = 2

        self.initUI()
        self.startLazyLoad(self.completeJobs)
        
    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setupLayout()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setupLayout(self):
        # Forex
        self.forexLayout = QGridLayout()
        self.forexLayout.setAlignment(Qt.AlignTop)
        self.forexLayout.setContentsMargins(10, 10, 10, 10)
        self.forexLayout.setSpacing(10)

        self.forexWidget = QWidget()
        self.forexWidget.setLayout(self.forexLayout)
        self.forexScroll.setWidget(self.forexWidget)

        # Indices
        self.indicesLayout = QGridLayout()
        self.indicesLayout.setAlignment(Qt.AlignTop)
        self.indicesLayout.setContentsMargins(10, 10, 10, 10)
        self.indicesLayout.setSpacing(10)

        self.indicesWidget = QWidget()
        self.indicesWidget.setLayout(self.indicesLayout)
        self.indicesScroll.setWidget(self.indicesWidget)

        # Cryptos
        self.cryptosLayout = QGridLayout()
        self.cryptosLayout.setAlignment(Qt.AlignTop)
        self.cryptosLayout.setContentsMargins(10, 10, 10, 10)
        self.cryptosLayout.setSpacing(10)

        self.cryptosWidget = QWidget()
        self.cryptosWidget.setLayout(self.cryptosLayout)
        self.cryptosScroll.setWidget(self.cryptosWidget)

        # Commodities
        self.commoditiesLayout = QGridLayout()
        self.commoditiesLayout.setAlignment(Qt.AlignTop)
        self.commoditiesLayout.setContentsMargins(10, 10, 10, 10)
        self.commoditiesLayout.setSpacing(10)

        self.commoditiesWidget = QWidget()
        self.commoditiesWidget.setLayout(self.commoditiesLayout)
        self.commoditiesScroll.setWidget(self.commoditiesWidget)

        # Set styles
        self.forexScroll.verticalScrollBar().setStyleSheet(scrollBarStyle)  
        self.forexScroll.setWidgetResizable(True)

        self.indicesScroll.verticalScrollBar().setStyleSheet(scrollBarStyle)  
        self.indicesScroll.setWidgetResizable(True)

        self.cryptosScroll.verticalScrollBar().setStyleSheet(scrollBarStyle)  
        self.cryptosScroll.setWidgetResizable(True)

        self.commoditiesScroll.verticalScrollBar().setStyleSheet(scrollBarStyle)  
        self.commoditiesScroll.setWidgetResizable(True)       

    def connectSlots(self):
        self.close_.clicked.connect(self.close)

    def startLazyLoad(self, execFunc: Callable, timeout: int = 100, *args, **kwargs):
        self.lazyLoadTimer = QTimer()
        self.lazyLoadTimer.singleShot(timeout, lambda: execFunc(*args, **kwargs))
        self.BatchSize = 5

    def completeJobs(self):
        self.loadNextBatch(self.forexList, self.forexCurrentIndex, self.forexBatchSize, self.forexRawSize, self.forexTask)
        self.loadNextBatch(self.indicesList, self.indicesCurrentIndex, self.indicesBatchSize, self.indicesRawSize, self.indexTask)
        self.loadNextBatch(self.cryptosList, self.cryptosCurrentIndex, self.cryptosBatchSize, self.cryptosRawSize, self.cryptoTask)
        self.loadNextBatch(self.commoditiesList, self.commoditiesCurrentIndex, self.commoditiesBatchSize, self.commoditiesRawSize, self.commodityTask)

    def loadNextBatch(self, items: List[str], currentIndex: int, BatchSize: int, rawSize: int, taskFunc: Callable):
        totalLength = len(items)
        if currentIndex >= totalLength:
            self.lazyLoadTimer.stop()
            return

        tasks = []

        for pos, item in enumerate(items):
            if currentIndex >= totalLength:
                break

            row = pos // rawSize
            col = pos % rawSize

            task = taskFunc(item, row, col)
            tasks.append(task)

            currentIndex += 1

        asyncio.ensure_future(asyncio.gather(*tasks))

    @asyncSlot()
    async def forexTask(self, forexPair: str, row: int, col: int):
        codes = forexPair.split("/")
        flag1Code = codes[0][:2].lower()
        flag2Code = codes[1][:2].lower()

        flag1Url = f"https://flagcdn.com/w40/{flag1Code}.png"
        flag2Url = f"https://flagcdn.com/w40/{flag2Code}.png"

        flag1 = await self.getFlagPixmap(flag1Url)
        flag2 = await self.getFlagPixmap(flag2Url)

        forexData = mongoGet(collection='forex', name=forexPair)
        if not forexData:
            return

        quoteTarget = forexData[0]["price"]["quote"]

        price = quoteTarget[0]["price"]
        growth = quoteTarget[0]["changesPercentage"]

        historicalTarget = forexData[0]["price"]["historical"]["quotes"]

        # only for testing
        chartVoidInputs = (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], [100, 123, 146, 122, 122, 129, 129, 133, 131, 134])
        if not historicalTarget:
            chartInputs = chartVoidInputs
            chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
            chartPixmap = QPixmap(str(chartOutput))
            item = ForexItem(flag1, flag2, forexPair, price, growth, chartPixmap, self)
        else:
            chartInputs = ([point["date"] for point in historicalTarget], [point["adjClose"] for point in historicalTarget])
            chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
            chartPixmap = QPixmap(str(chartOutput))

            item = ForexItem(flag1, flag2, forexPair, price, growth, chartPixmap, self)

        self.forexLayout.addWidget(item, row, col)

    async def getFlagPixmap(self, url):
        response = await quickFetchBytes(url, {}, {"User-Agent": "GaelloX/1.0"})
        if not response:
            return

        pixmap = QPixmap()
        bytesObj = response if isinstance(response, bytes) else None
        pixmap.loadFromData(BytesIO(bytesObj).read())
        return pixmap

    @asyncSlot()
    async def indexTask(self, indexName, row, col):
        await asyncio.sleep(1)

        indexData = mongoGet(collection='indices', name=indexName)

        if not indexData:
            return

        target = indexData[0]['historical']['quotes']
        if not target:
            raise ValueError('Target was set to render inexistent fields')

        currentValues = target[-1]
        previousValues = target[-2]
        currentPrice = currentValues['adjClose']
        previousPrice = previousValues['adjClose']
        growth = 100 * (currentPrice - previousPrice) / previousPrice
        chartInputs = ([point['date'] for point in target], [point['adjClose'] for point in target])
        chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
        chartPixmap = QPixmap(str(chartOutput))

        # Cut long names so they don't harm the display
        if len(indexName) > 30:
            indexName = f'{indexName[:30]}.'
        indexSymbol = indexData[0]['symbol']
        item = IndexItem(indexSymbol, indexName, currentPrice, growth, chartPixmap)
        self.indicesLayout.addWidget(item, row, col)

    @asyncSlot()
    async def cryptoTask(self, cryptoSymbol: str, row, col):
        cryptoData = mongoGet(collection="crypto", symbol=cryptoSymbol)

        if not cryptoData:
            return

        # Refactor crypto name 
        cryptoName = cryptoData[0]["name"]
        cryptoName.replace("USD", "/USD")

        quoteTarget = cryptoData[0]['historicalData']["quote"][0]
        price = quoteTarget["price"]
        growth = quoteTarget["changesPercentage"]
        historicalTarget = cryptoData[0]['historicalData']["daily"]["historical"]

        chartInputs = ([point["date"] for point in historicalTarget], [point["adjClose"] for point in historicalTarget])
        chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
        chartPixmap = QPixmap(str(chartOutput))

        # symbol will probably end with 'USD' so we strip it away
        cryptoSymbol_ = cryptoSymbol.replace("USD", "")
        # Then get image/logo
        imagePixmap = await self.getCryptoPixmap(cryptoSymbol_)

        if not imagePixmap:
            item = CryptoItem(cryptoSymbol, cryptoName, price, growth, None, chartPixmap)
        else:
            item = CryptoItem(cryptoSymbol, cryptoName, price, growth, imagePixmap, chartPixmap)

        self.cryptosLayout.addWidget(item, row, col)

    async def getCryptoPixmap(self, cryptoSymbol):
        imageUrl = await self.getCryptoImageUrl(cryptoSymbol)
        if imageUrl:
            response = await quickFetchBytes(imageUrl)
            pixmap = QPixmap()
            bytesObj = response if response else None
            pixmap.loadFromData(BytesIO(bytesObj).read())
            return pixmap
        return None

    async def getCryptoImageUrl(self, symbol):
        try:
            apikey = os.getenv("CRYPTO_COMPARE_API_KEY")
            if not apikey:
                print("CRYPTO_COMPARE_API_KEY environment variable not set")
                return None

            # CryptoCompare API to fetch coin information
            url = f"https://min-api.cryptocompare.com/data/top/mktcapfull?limit=100&tsym=USD"
            data = await quickFetchJson(url, headers={"authorization": f'Apikey {apikey}'})
            if not data:
                return
            # Find the coin info for the desired symbol
            for coin in data["Data"]:
                if coin["CoinInfo"]["Name"] == symbol:
                    imageUrl = "https://www.cryptocompare.com" + coin["CoinInfo"]["ImageUrl"]
                    return imageUrl
        except Exception as e:
            print(f"Error fetching data from CryptoCompare: {e}")
        return None

    @asyncSlot()
    async def commodityTask(self, commoditySymbol, row, col):
        comData = mongoGet(collection="commodities", symbol=commoditySymbol)

        if not comData:
            return

        comName = comData[0]["name"]

        # some dummy data
        item = CommodityItem(commoditySymbol, comName, 100, 1.001)
        self.commoditiesLayout.addWidget(item, row, col)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = ExploreMarket()
    window.show()

    with loop:
        loop.run_forever()
