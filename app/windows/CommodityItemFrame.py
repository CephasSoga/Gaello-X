import os
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QFrame

from app.windows.AuthHandler import handleAuth
from app.windows.Fonts import loadFont
from app.windows.SingleFocusFrame import SingleFocus
from utils.appHelper import setRelativeToMainWindow

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)


class CommodityItem(QFrame):
    clicked = pyqtSignal()
    def __init__(self, symbol: str, name: str, price: float, growth: float, historicalPixmap: Optional[QPixmap] = None, parent=None):
        super(CommodityItem, self).__init__(parent)
        path = os.path.join(r"UI/commodityItem.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.symbol = symbol
        self.name = name
        self.price = price
        self.growth = growth
        self.historicalPixmap = historicalPixmap

        self.initUI()

    def initUI(self):
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

        if self.historicalPixmap:
            self.chartLabel.setPixmap(self.historicalPixmap)

        if self.growth >= 0:
            self.growthLabel.setText(f"+{self.growth:.3f}%")
            self.growthLabel.setStyleSheet(f"color: green; border: none; border-radius: 0;")
        else:
            self.growthLabel.setText(f"{self.growth:.3f}%")
            self.growthLabel.setStyleSheet("color: red; border: none; border-radius: 0;")

    def setFonts(self):
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Bold.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(9)
        else:
            font = QFont("Arial", 9)

        self.nameLabel.setFont(font)
        self.priceLabel.setFont(font)
        self.growthLabel.setFont(font)

        tinyFontFam = loadFont(r"rsrc/fonts/Exo_2/static/Exo2-Light.ttf")
        if tinyFontFam:
            tinyFont = QFont(tinyFontFam)
            tinyFont.setPointSize(8)
        else:
            font = QFont("Arial", 8)

        self.tagLabel.setFont(tinyFont)

    def connectSlots(self):
        self.clicked.connect(lambda: handleAuth(2, self.spawnFocus))
    def spawnFocus(self):
        ancestorWidget = self.parent().parent().parent().parent() #Stands for ExploreMarket widget
        item = SingleFocus(symbol=self.symbol, targetCollection='commodities')
        setRelativeToMainWindow(item, ancestorWidget, "center")
        ancestorWidget.installEventFilter(item)
