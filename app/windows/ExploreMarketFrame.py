import os
import random
import asyncio
from io import BytesIO
from typing import List, Dict, Callable

from pymongo.mongo_client import MongoClient

from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget, QApplication
from qasync import QEventLoop, asyncSlot

from utils.asyncJobs import quickFetchBytes, quickFetchJson,  asyncWrap, ThreadRun
from utils.databases import mongoGet
from utils.envHandler import getenv
from utils.graphics import chartWithSense
from app.windows.ForexItemFrame import ForexItem
from app.windows.IndexItemFrame import IndexItem
from app.windows.CryptoItemFrame import CryptoItem
from app.windows.CommodityItemFrame import CommodityItem
from app.windows.Styles import scrollBarStyle
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI
from app.config.scheduler import Schedule
from app.config.balancer import BatchBalance
from app.config.renderer import ViewController

# import resources
import app.config.resources

class ExploreMarket(QFrame):
    def __init__(self, connection: MongoClient, async_tasks: list, parent=None):
        super(ExploreMarket, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "exploreMarket.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.async_tasks = async_tasks

        self.cryptos: List[Dict] = []
        self.commodities: List[Dict] = []
        self.indices: List[Dict] = []
        self.forexes: List[Dict] = []

        self.flagsSource = "https://flagcdn.com"
        self.chartDisplayWidth, self.chartDisplayHeigth = 130, 60

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
        QTimer.singleShot(Schedule.NO_DELAY, self.syncGetAllData)
        QTimer.singleShot(Schedule.BATCH_MARKET_JOBS_DELAY, lambda: self.startLazyLoad(self.completeJobs))
        
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
        self.forexLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.forexLayout.setSpacing(ViewController.DEFAULT_SPACING)

        self.forexWidget = QWidget()
        self.forexWidget.setLayout(self.forexLayout)
        self.forexScroll.setWidget(self.forexWidget)

        # Indices
        self.indicesLayout = QGridLayout()
        self.indicesLayout.setAlignment(Qt.AlignTop)
        self.indicesLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.indicesLayout.setSpacing(ViewController.DEFAULT_SPACING)

        self.indicesWidget = QWidget()
        self.indicesWidget.setLayout(self.indicesLayout)
        self.indicesScroll.setWidget(self.indicesWidget)

        # Cryptos
        self.cryptosLayout = QGridLayout()
        self.cryptosLayout.setAlignment(Qt.AlignTop)
        self.cryptosLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.cryptosLayout.setSpacing(ViewController.DEFAULT_SPACING)

        self.cryptosWidget = QWidget()
        self.cryptosWidget.setLayout(self.cryptosLayout)
        self.cryptosScroll.setWidget(self.cryptosWidget)

        # Commodities
        self.commoditiesLayout = QGridLayout()
        self.commoditiesLayout.setAlignment(Qt.AlignTop)
        self.commoditiesLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.commoditiesLayout.setSpacing(ViewController.DEFAULT_SPACING)

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
        self.close_.clicked.connect(self.hide) # only hide to preserve state

    def startLazyLoad(self, execFunc: Callable, timeout: int = BatchBalance.RELOADING_MSEC, *args, **kwargs):
        self.lazyLoadTimer = QTimer()
        self.lazyLoadTimer.setInterval(timeout)
        self.lazyLoadTimer.timeout.connect(lambda: execFunc(*args, **kwargs))
        self.BatchSize = BatchBalance.MARKET_REMOTE_LOADING_SIZE
        self.lazyLoadTimer.start(Schedule.LONG_WAITING_DELAY)

    def completeJobs(self):
        self.loadNextBatch(self.forexList, self.forexCurrentIndex, self.forexBatchSize, self.forexRawSize, self.forexTask)
        self.loadNextBatch(self.indicesList, self.indicesCurrentIndex, self.indicesBatchSize, self.indicesRawSize, self.indexTask)
        self.loadNextBatch(self.cryptosList, self.cryptosCurrentIndex, self.cryptosBatchSize, self.cryptosRawSize, self.cryptoTask)
        self.loadNextBatch(self.commoditiesList, self.commoditiesCurrentIndex, self.commoditiesBatchSize, self.commoditiesRawSize, self.commodityTask)

    def loadNextBatch(self, items: List[str], currentIndex: int, BatchSize: int, rawSize: int, taskFunc: Callable):
        totalLength = len(items)
        if currentIndex >= totalLength:
            self.lazyLoadTimer.stop()
            print("NO MORE DATA!")
            return

        tasks = []

        for pos, item in enumerate(items):
            if currentIndex >= totalLength:
                print("NO MORE DATA! Index exceeds list size.")
                break

            row = pos // rawSize
            col = pos % rawSize

            task = taskFunc(item, row, col)
            tasks.append(task)

            currentIndex += 1

        self.async_tasks.extend(tasks)

    @asyncSlot()
    async def forexTask(self, forexPair: str, row: int, col: int):
        def func_1(forexPair: str):
            codes = forexPair.split("/")
            flag1Code = codes[0][:2].lower()
            flag2Code = codes[1][:2].lower()

            flag1Url = f"https://flagcdn.com/w40/{flag1Code}.png"
            flag2Url = f"https://flagcdn.com/w40/{flag2Code}.png"

            return flag1Url, flag2Url
        
        def func_2(forexList: List[Dict], forexPair: str):
            forexData = [forex for forex in forexList if forex.get("name")==forexPair]

            if not forexData:
                return

            quoteTarget = forexData[0]["price"]["quote"]

            price = quoteTarget[0]["price"]
            growth = quoteTarget[0]["changesPercentage"]

            historicalTarget = forexData[0]["price"]["historical"]["quotes"][::-1] # reverse to get a descending order (based on date)

            # only for testing
            chartVoidInputs = (list(range(1000)), [random.randrange(200, 420) for _ in range(1000)])
            if not historicalTarget:
                chartInputs = chartVoidInputs
                chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
                chartPixmap = QPixmap(str(chartOutput))
            else:
                chartInputs = ([point["date"] for point in historicalTarget], [point["adjClose"] for point in historicalTarget])
                chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
                chartPixmap = QPixmap(str(chartOutput))

            return price, growth, chartPixmap

        def func_3(forexPair: str, price: float, growth: float, flag1: QPixmap, flag2: QPixmap, chartPixmap: QPixmap):
            item = ForexItem(
                connection=self.connection,
                async_tasks=self.async_tasks,
                flag1Pixmap=flag1, 
                flag2Pixmap=flag2, 
                pair=forexPair, 
                price=price, 
                growth=growth, 
                historicalPixmap=chartPixmap,
                parent=self)

            return item

        res = await ThreadRun(func_2, self.forexes, forexPair)
        if res:
            price, growth, chart = res
            flag1Url, flag2Url = await ThreadRun(func_1, forexPair)
            flag1 = await self.getFlagPixmap(flag1Url)
            flag2 = await self.getFlagPixmap(flag2Url)
            item = func_3(forexPair, price, growth, flag1, flag2, chart)
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
    async def indexTask(self, indexName: str, row: int, col: int):
        def func_1(indicesList: List, indexName: str):
            indexData = [index for index in  indicesList if index.get("name")==indexName]

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

            return indexSymbol, indexName, currentPrice, growth, chartPixmap

        def func_2(indexSymbol, indexName, currentPrice, growth, chartPixmap):
            item = IndexItem(
                connection=self.connection,
                async_tasks=self.async_tasks,
                symbol=indexSymbol, 
                name=indexName, 
                price=currentPrice, 
                growth=growth,
                historicalPixmap=chartPixmap,
            )
            return item
        
        res = await ThreadRun(func_1, self.indices, indexName)
        if res:
            item = func_2(*res)
            self.indicesLayout.addWidget(item, row, col)

    @asyncSlot()
    async def cryptoTask(self, cryptoSymbol: str, row, col):
        def func_1(cryptoList: List[Dict], cryptoSymbol: str):
            cryptoData = [crypto for crypto in cryptoList if crypto.get("symbol")==cryptoSymbol]

            if not cryptoData:
                return

            # Refactor crypto name 
            cryptoName: str = cryptoData[0]["name"]
            cryptoName = cryptoName.strip().replace("USD", "/USD").replace(" ", "")

            quoteTarget = cryptoData[0]['historicalData']["quote"][0]
            price = quoteTarget["price"]
            growth = quoteTarget["changesPercentage"]

            historicalTarget = cryptoData[0]['historicalData']["daily"]["historical"][::-1] # reverse to get a descending order (based on date)
            chartInputs = ([point["date"] for point in historicalTarget], [point["adjClose"] for point in historicalTarget])
            chartOutput = chartWithSense(chartInputs[0], chartInputs[1], self.chartDisplayWidth, self.chartDisplayHeigth)
            chartPixmap = QPixmap(str(chartOutput))

            # symbol will probably end with 'USD' so we strip it away
            cryptoSymbol_ = cryptoSymbol.replace("USD", "")
            
            return cryptoSymbol_, cryptoName, price, growth, chartPixmap

        def func_2(cryptoSymbol, cryptoName, price, growth, imagePixmap, chartPixmap):
            item = CryptoItem(
                connection=self.connection,
                async_tasks=self.async_tasks,
                symbol=cryptoSymbol, 
                name=cryptoName, 
                price=price, 
                growth=growth, 
                imagePixmap=imagePixmap,
                historicalPixmap=chartPixmap
            )

            return item
        
        res = await ThreadRun(func_1, self.cryptos, cryptoSymbol)
        if res:
            cryptoSymbol_, cryptoName, price, growth, chart = res
            imagePixmap = await self.getCryptoPixmap(cryptoSymbol_)
            item = func_2(cryptoSymbol, cryptoName, price, growth, imagePixmap, chart)

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
        def func_1(commoditiesList: List, commoditySymbol: str):
            comData = [com for com in  commoditiesList if com.get("symbol")==commoditySymbol]
        
            if not comData:
                return

            comName = comData[0]["name"]
            # some dummy data
            price = 100
            growth = 1.001
            return commoditySymbol, comName, price, growth
        
        def func_2(commoditySymbol, comName, price, growth):
            item = CommodityItem(
                connection=self.connection,
                async_tasks=self.async_tasks, 
                symbol=commoditySymbol, 
                name=comName, 
                price=price, 
                growth=growth
            )
            return item
        
        res = await ThreadRun(func_1, self.commodities, commoditySymbol)
        if res:
            item = func_2(*res)
            self.commoditiesLayout.addWidget(item, row, col)

    async def getAllData(self):
        asyncMongoGet = asyncWrap(mongoGet)
        self.cryptos = await asyncMongoGet(collection="crypto", limit=int(5e4), connection=self.connection)
        self.commodities = await asyncMongoGet(collection="commodities", limit=int(5e4), connection=self.connection)
        self.indices = await asyncMongoGet(collection='indices', limit=int(5e4), connection=self.connection)
        self.forexes = await asyncMongoGet(collection='forex', limit=int(5e4), connection=self.connection)
        for l in self.cryptos, self.commodities, self.indices, self.forexes:
            pass

    def syncGetAllData(self):
        self.async_tasks.append(self.getAllData())
        


if __name__ == "__main__":
    import sys
    from pymongo.server_api import ServerApi

    uri = getenv("MONGO_URI")

    # Create a new client and connect to the server
    mongo_client = MongoClient(uri, server_api=ServerApi('1'))


    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = ExploreMarket(mongo_client)
    window.show()

    with loop:
        loop.run_forever()

