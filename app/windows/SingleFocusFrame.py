import os
import json
import asyncio
from typing import Any
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, pyqtSlot, QObject, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit

from utils.databases import mongoGet
from app.windows.Spinner import Spinner
from app.handlers.Patterns import Index, Symbol
from utils.workers import spinnerWork
from app.windows.Fonts import RobotoRegular
from app.windows.Styles import chatScrollBarStyle
from utils.appHelper import clearLayout
from utils.paths import getPath


class SingleFocus(QWidget):
    def __init__(self, symbol:str, targetCollection: str, parent=None):
        super().__init__(parent)
        path = getPath(os.path.join("assets", "UI" , "singleFocus.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.symbol = symbol
        self.targetCollection = targetCollection
        target = mongoGet(collection=targetCollection, symbol=self.symbol)
        if self.targetCollection =='forex':
            start = 'price'
        elif self.targetCollection == 'commodities':
            start = 'historical'
        else:
            start = 'historicalData'
        self.target = target[0][start] if target else None

        self.initUI()
        QTimer.singleShot(0, self.makeQuoteWithSpinner)

    def initUI(self):
        self.setWFlags()
        self.setupLayout()

    def setupLayout(self):
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(10, 10, 10, 10)
        self.scrollLayout.setSpacing(10)
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

    async def fetchQuote(self):
        await asyncio.sleep(2)
        if not self.target:
            return
        if self.targetCollection in ['crypto', 'forex']:
            end = 'quote'
        elif self.targetCollection in ['indices', 'commodities']:
            end = 'quotes'
        else:
            end = ''
        subTarget = self.target.get(end)
        # force it to return a list
        return subTarget if subTarget else []
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)

    def populateResult(self, result):
        clearLayout(self.scrollLayout)
        if result is None or len(result) == 0:
            #Do somthing here later
            pass
        item = QTextEdit()
        item.clear()
        item.setStyleSheet(f"color: rgb(255, 255, 255)")
        item.setFont(
            RobotoRegular(10) or QFont ('Arial', 10)
        )
        item.setReadOnly(True)
        try:
            item.setPlainText(json.dumps(result, indent=4, separators=(',\n', ': ')))
        except Exception:
            for res in result:
                if isinstance(res, dict):
                    for key in res.keys():
                        notHandled = res[key]
                        if isinstance(notHandled, datetime):
                            handledDateTimeType = notHandled.isoformat()
                            res[key] = handledDateTimeType
            item.setPlainText(json.dumps(result, indent=4, separators=(',\n', ': ')))
        item.update()
        item.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        item.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLayout.addWidget(item)
        self.scrollLayout.update()

    @pyqtSlot(list)
    def populateQuote(self, financials):
        self.populateResult(financials)

    def makeQuoteWithSpinner(self):
        self.spinner = Spinner()

        self.thread = QThread()
        self.worker = Worker(self.fetchQuote)

        spinnerWork(self.spinner, self.thread, self.worker, self.populateQuote)

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
