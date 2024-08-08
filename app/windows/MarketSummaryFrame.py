from ast import Dict
import os
import asyncio
from typing import Optional, List, Dict
from io import BytesIO

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QWidget, QApplication


from app.windows.Spinner import Spinner, Worker
from app.windows.ArticleItemFrame import ArticleItem
from app.assets.Outliners import MarketOutliner, Outline, OutlineTitle
from app.assets.ExportAssets import IndexList
from utils.databases import mongoGet
from utils.asyncJobs import quickFetchBytes


currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class MarketSummary(QFrame):
    dataFetched = pyqtSignal(str, list)
    updateFocus = pyqtSignal()

    def __init__(self, parent=None):
        super(MarketSummary, self).__init__(parent)
        path = os.path.join("UI", "marketSummary.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.outliner = MarketOutliner()
        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()
        self.setupLayout()
        self.dataFetched.connect(self.handleDataFetched)
        self.updateFocus.connect(self.handleNewsFetched)
        self.runAllAsync()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)

    def setupLayout(self):
        self.gridScrollLayout = QGridLayout()
        self.gridScrollLayout.setAlignment(Qt.AlignTop)
        self.gridScrollLayout.setSpacing(10)
        self.gridScrollLayout.setContentsMargins(10, 10, 10, 10)
        self.focusScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.focusScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gridScrollWidget = QWidget()
        self.gridScrollWidget.setLayout(self.gridScrollLayout)
        self.focusScroll.setWidget(self.gridScrollWidget)

        self.vboxScrollLayout = QVBoxLayout()
        self.vboxScrollLayout.setAlignment(Qt.AlignTop)
        self.vboxScrollLayout.setSpacing(10)
        self.vboxScrollLayout.setContentsMargins(10, 10, 10, 10)
        self.outlineScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.outlineScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.outlineScroll.setAlignment(Qt.AlignTop)
        self.vboxScrollWidget = QWidget()
        self.vboxScrollWidget.setLayout(self.vboxScrollLayout)
        self.outlineScroll.setWidget(self.vboxScrollWidget)

    async def gainers(self):
        gainers = await self.outliner.gainers()
        self.dataFetched.emit('gainers', gainers)

    async def losers(self):
        losers = await self.outliner.losers()
        self.dataFetched.emit('losers', losers)

    async def mostactives(self):
        actives = await self.outliner.mostactive()
        self.dataFetched.emit('mostactives', actives)

    async def sectorPerformances(self):
        sectors = await self.outliner.sectorPerformances()
        self.dataFetched.emit('sectors', sectors)

    def handleDataFetched(self, category, items):
        if category == 'gainers':
            self.addGainers(items)
        elif category == 'losers':
            self.addLosers(items)
        elif category == 'mostactives':
            self.addMostActives(items)
        elif category == 'sectors':
            self.addSectorPerformances(items)

    def handleNewsFetched(self):
        asyncio.ensure_future(self.setFocus())

    def addGainers(self, gainers):
        title = OutlineTitle(self)
        title.titleLabel.setText("Market Gainers")
        self.vboxScrollLayout.addWidget(title)

        if len(gainers) == 0:
            return

        for gainer in gainers:
            outline = Outline(self)
            symbol = gainer["ticker"]
            name = gainer["companyName"]
            price = gainer["price"]
            priceChange = gainer["changes"]
            growth = gainer["changesPercentage"]

            self.setOutlineContents(self.vboxScrollLayout, outline, symbol, name, price, priceChange, growth)

    def addLosers(self, losers):
        title = OutlineTitle(self)
        title.titleLabel.setText("Market Losers")
        self.vboxScrollLayout.addWidget(title)

        if len(losers) == 0:
            return

        for loser in losers:
            outline = Outline(self)
            symbol = loser["ticker"]
            name = loser["companyName"]
            price = loser["price"]
            priceChange = loser["changes"]
            growth = loser["changesPercentage"]

            self.setOutlineContents(self.vboxScrollLayout, outline, symbol, name, price, priceChange, growth)

    def addMostActives(self, actives):
        title = OutlineTitle(self)
        title.titleLabel.setText("Most Actives")
        self.vboxScrollLayout.addWidget(title)

        if len(actives) == 0:
            return

        for active in actives:
            outline = Outline(self)
            symbol = active["ticker"]
            name = active["companyName"]
            price = active["price"]
            priceChange = active["changes"]
            growth = active["changesPercentage"]

            self.setOutlineContents(self.vboxScrollLayout, outline, symbol, name, price, priceChange, growth)

    def addSectorPerformances(self, sectors):
        title = OutlineTitle(self)
        title.titleLabel.setText("Sector Performances")
        self.vboxScrollLayout.addWidget(title)

        if len(sectors) == 0:
            return

        for sector in sectors:
            outline = Outline(self)
            symbol = sector["sector"]
            name = ""
            price = ""
            priceChange = ""
            growth = sector["changesPercentage"]

            self.setOutlineContents(self.vboxScrollLayout, outline, symbol, name, price, priceChange, growth)

    def setOutlineContents(self, layout: QVBoxLayout, outline: Outline, symbol: Optional[str], name: Optional[str], price: Optional[int], priceChange: Optional[int], growth: Optional[int]):
        outline.symbolLabel.setText(f"{symbol}")
        outline.nameLabel.setText(f"{name}")
        outline.priceLabel.setText(f"{price}")
        outline.priceChangeLabel.setText(f"{priceChange}")
        growth = growth.strip().replace('%', '')
        if float(growth) >= 0:
            outline.growthLabel.setStyleSheet(
                """
                QLabel {
                    color: green; 
                }
                """
            )
        else:
            outline.growthLabel.setStyleSheet(
                """
                QLabel {
                    color: red; 
                }
                """
            )
        outline.growthLabel.setText(f"{growth}%")

        layout.addWidget(outline)

    async def setOutlinesContents(self):
        await self.gainers()
        await self.losers()
        await self.mostactives()
        await self.sectorPerformances()

    async def setFocus(self):
        articles: List[Dict] = mongoGet(collection='articles',limit=10)

        for pos, article in enumerate(articles):
            title = article.get('title', '')
            imageUrl = article.get('image', '')
            author = article.get('author', '')
            content = article.get('content', None) or article.get('text')
            date = article.get('date', None) or article.get('publishedAt')
            link = article.get('link', None) or article.get('url')
            tickers = article.get('tickers', [])
            source = article.get('site', '')

            imagePixmap = await self.getPixmap(imageUrl)
            item  = ArticleItem(
                title=title,
                imagePixmap=imagePixmap,
                author=author,
                source=source,
                date=date,
                content=content,
                link=link,
                tickers=tickers,
                parent=self
            )
            row = pos // 3
            col = pos % 3
            self.gridScrollLayout.addWidget(item, row, col)

    async def getPixmap(self, url):
        response = await quickFetchBytes(url)
        if not response:
            return
        
        pixmap = QPixmap()
        bytesObj = response if isinstance(response, bytes) else None
        pixmap.loadFromData(BytesIO(bytesObj).read())
        return pixmap

    async def allAsync(self):
        await self.setOutlinesContents()
        self.updateFocus.emit()

    def runAllAsync(self):
        spinner = Spinner(parent=self)
        self.worker = Worker(self.allAsync, 'async')

        self.worker.start()

        self.worker.started.connect(spinner.start)
        self.worker.finished.connect(spinner.stop)
        

if __name__ == "__main__":
    import sys
    from qasync import QApplication, QEventLoop

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MarketSummary()
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()
