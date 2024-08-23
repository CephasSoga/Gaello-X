import os
import asyncio
from typing import Optional

from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame

from app.handlers.AuthHandler import handleAuth
from app.config.fonts import RobotoBold, Exo2Light, FontSizePoint
from app.windows.SingleFocusFrame import SingleFocus
from utils.appHelper import setRelativeToMainWindow, adjustForDPI
from utils.paths import getFrozenPath

class CryptoItem(QFrame):
    clicked = pyqtSignal()
    def __init__(self, symbol: str, name: str, price: float, growth: float, imagePixmap: Optional[QPixmap], historicalPixmap: Optional[QPixmap], parent=None):
        super().__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "cryptoItem.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        self.symbol = symbol
        self.name = name
        self.price = price
        self.growth = growth
        self.imagePixmap = imagePixmap
        self.historicalPixmap = historicalPixmap

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
    
    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit the custom clicked signal
        super().mousePressEvent(event)

    def setContents(self):
        self.priceLabel.setAlignment(Qt.AlignRight)
        self.growthLabel.setAlignment(Qt.AlignRight)

        self.nameLabel.setText(self.name)
        self.priceLabel.setText(f"{self.price:.3f}")

        if self.imagePixmap:
            self.imageLabel.setPixmap(self.imagePixmap)
        if self.historicalPixmap:
            self.chartLabel.setPixmap(self.historicalPixmap)

        if self.growth >= 0:
            self.growthLabel.setText(f"+{self.growth:.3f}%")
            self.growthLabel.setStyleSheet("color: green; border: none; border-radius: 0;")
        else:
            self.growthLabel.setText(f"{self.growth:.3f}%")
            self.growthLabel.setStyleSheet("color: red; border: none; border-radius: 0;")

    def setFonts(self):
        size = FontSizePoint
        font = RobotoBold(size.SMALL) or QFont("Arial", size.SMALL)
        self.nameLabel.setFont(font)
        self.priceLabel.setFont(font)
        self.growthLabel.setFont(font)

        tinyFont = Exo2Light(size.TINY) or QFont("Arial", size.TINY)
        self.tagLabel.setFont(tinyFont)

    def connectSlots(self):
        self.clicked.connect(lambda: asyncio.ensure_future(handleAuth(2, self.spawnFocus)))

    def spawnFocus(self):
        ancestorWidget = self.parent().parent().parent().parent() #Stands for ExploreMarket widget
        item = SingleFocus(symbol=self.symbol, targetCollection='crypto')
        setRelativeToMainWindow(item, ancestorWidget, "center")
        ancestorWidget.installEventFilter(item)
