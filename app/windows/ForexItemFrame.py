import os
import asyncio
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QFrame

from app.windows.AuthHandler import handleAuth
from app.windows.Fonts import RobotoBold, Exo2Light
from app.windows.SingleFocusFrame import SingleFocus
from utils.appHelper import setRelativeToMainWindow
from utils.paths import getFrozenPath


class ForexItem(QFrame):
    clicked = pyqtSignal()
    def __init__(self,
                #symbol: str, 
                flag1Pixmap: Optional[QPixmap], 
                flag2Pixmap: Optional[QPixmap], 
                pair: str, 
                price: float, 
                growth: float, 
                historicalPixmap: Optional[QPixmap], 
                parent=None):
        super(ForexItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "forexItem.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        #self.symbol = symbol
        self.flag1Pixmap = flag1Pixmap
        self.flag2Pixmap = flag2Pixmap
        self.pair = pair
        self.price = price
        self.growth = growth
        self.historicalPixmap = historicalPixmap


        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.setContens()
        self.setFonts()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    
    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit the custom clicked signal
        super().mousePressEvent(event)

    def setContens(self):
        self.priceLabel.setAlignment(Qt.AlignRight)
        self.growthLabel.setAlignment(Qt.AlignRight)

        if self.flag1Pixmap: 
            self.flag1Label.setPixmap(self.flag1Pixmap)
        if self.flag2Pixmap:
            self.flag2Label.setPixmap(self.flag2Pixmap)

        if self.historicalPixmap:
            self.chartLabel.setPixmap(self.historicalPixmap)

        self.pairLabel.setText(self.pair)
        self.priceLabel.setText(f'{self.price:.3f}')

        if self.growth >= 0:
            self.growthLabel.setText(f'+{self.growth:.3f}%')
            self.growthLabel.setStyleSheet("color: green; border: none; border-radius: 0;")

        else:
            self.growthLabel.setText(f'{self.growth:.3f}%')
            self.growthLabel.setStyleSheet("color: red; border: none; border-radius: 0;")

    def setFonts(self):
        font = RobotoBold(9) or QFont("Arial", 9)
        for obj in self.children():
            obj.setFont(font)

        tinyFont = Exo2Light(8) or QFont("Arial", 8)
        self.tagLabel.setFont(tinyFont)

    def connectSlots(self):
        self.clicked.connect(lambda: handleAuth(2, self.spawnFocus))

    def spawnFocus(self):
        ancestorWidget = self.parent().parent().parent().parent() #Stands for ExploreMarket widget
        item = SingleFocus(symbol=self.pair.replace("/",""), targetCollection='forex')
        setRelativeToMainWindow(item, ancestorWidget, "center")
        ancestorWidget.installEventFilter(item)
            
