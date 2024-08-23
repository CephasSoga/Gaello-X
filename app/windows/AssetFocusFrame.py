import os
import json
import asyncio
from typing import Any
from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit

from utils.databases import mongoGet
from app.windows.Spinner import Spinner
from app.handlers.Patterns import Index, Symbol
from app.config.fonts import RobotoSemiBold, RobotoRegular, FontSizePoint
from app.windows.Styles import chatScrollBarStyle
from utils.logs import Logger
from utils.appHelper import clearLayout, adjustForDPI
from utils.workers import spinnerWork
from utils.paths import getFrozenPath
from app.config.renderer import ViewController

class AssetFocusItem(QFrame):
    def __init__(self, parent=None):
        super(AssetFocusItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "assetFocusItem.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setAppearance()
        self.setFonts()

    def setAppearance(self):
        self.setStyleSheet(
            """
            QWidget {
                background: none;
                background-color: rgba(15, 45, 100, 200);
                border-color: rgba(255, 255, 255, 100);
                border-width: 1px;
                border-style: dotted;
            }
            """
        )

    def setFonts(self):
        size = FontSizePoint
        font = RobotoSemiBold(size.BIG) or QFont("Arial", size.BIG)
        self.name.setFont(font)
        self.value.setFont(font)

class AssetFocus(QWidget):
    def __init__(self, symbol:str, parent=None):
        super(AssetFocus, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "assetFocus.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.logger = Logger("Stocks-Focus")

        self.symbol = symbol
        self.apikey = os.getenv("FMP_API_KEY")
        target = mongoGet(collection='ticker', symbol=self.symbol)
        self.target = target[0]['ticker'] if target else None

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.setupLayout()
        self.connectSlots()

    def setupLayout(self):
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.scrollLayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.financials.clicked.connect(self.makeFinancialsWithSpinner)
        self.metrics.clicked.connect(self.makeMetricsWithSpinner)
        self.ratios.clicked.connect(self.makeRatiosWithSpinner)
        self.priceTargets.clicked.connect(self.makePriceTargetsWithSpinner)

    async def fetchFinancials(self):
        await asyncio.sleep(2)
        if not self.target:
            return
        subTarget = self.target['general']['financials']
        # force it to return a list
        return subTarget if subTarget else []
        
    async def fetchMetrics(self):
        await asyncio.sleep(2)
        if not self.target:
            return
        subTarget = self.target['analysis']['keyMetricsTTM']
        return subTarget if subTarget else []
        
    async def fetchRatios(self):
        await asyncio.sleep(2)
        if not self.target:
            return
        subTarget = self.target['analysis']['ratios']
        return subTarget if subTarget else []
    async def fetchPriceTargets(self):
        await asyncio.sleep(2)
        if not self.target:
            return
        subTarget = self.target['general']['priceTarget']
        return subTarget if subTarget else []

    def populateResult(self, result):
        size = FontSizePoint
        clearLayout(self.scrollLayout)
        if result is None or len(result) == 0:
            self.scrollLayout.addWidget(QLabel("No data is available."))
        item = QTextEdit()
        item.clear()
        item.setStyleSheet(f"color: rgb(255, 255, 255)")
        item.setFont(
            RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        )
        item.setReadOnly(True)
        item.setPlainText(json.dumps(result, indent=4, separators=(',\n', ': ')))
        item.update()
        item.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        item.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLayout.addWidget(item)
        self.scrollLayout.update()

    @pyqtSlot(list)
    def populateFinancials(self, financials):
        self.populateResult(financials)

    @pyqtSlot(list)
    def populateMetrics(self, metrics):
        self.populateResult(metrics)

    @pyqtSlot(list)
    def populateRatios(self, ratios):
        self.populateResult(ratios)

    @pyqtSlot(list)
    def populatePriceTargets(self, priceTargets):
        self.populateResult(priceTargets)

    def makeFinancialsWithSpinner(self):
        self.spinner = Spinner()

        self.thread = QThread()
        self.worker = Worker(self.fetchFinancials)

        spinnerWork(self.spinner, self.thread, self.worker, self.populateFinancials)

    def makeMetricsWithSpinner(self):
        self.spinner = Spinner()
        self.thread = QThread()
        self.worker = Worker(self.fetchMetrics)

        spinnerWork(self.spinner, self.thread, self.worker, self.populateMetrics)

    def makeRatiosWithSpinner(self):
        self.spinner = Spinner()
        self.thread = QThread()
        self.worker = Worker(self.fetchRatios)

        spinnerWork(self.spinner, self.thread, self.worker, self.populateRatios)

    def makePriceTargetsWithSpinner(self):
        self.spinner = Spinner()
        self.thread = QThread()
        self.worker = Worker(self.fetchPriceTargets)

        spinnerWork(self.spinner, self.thread, self.worker, self.populatePriceTargets)

class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(list)

    def __init__(self, async_func):
        super(Worker, self).__init__()
        self.async_func = async_func

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        financials = loop.run_until_complete(self.async_func())
        self.result.emit(financials)
        self.finished.emit()
