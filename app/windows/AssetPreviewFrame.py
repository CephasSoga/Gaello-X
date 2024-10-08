import os
from typing import Optional

from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QFrame

from app.config.fonts import RobotoSemiBold, FontSizePoint
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

# import resources
import app.config.resources

class AssetPreview(QFrame):
    clicked = pyqtSignal()
    def __init__(self,
                 symbol: str, 
                name:Optional[str]=None, 
                price:Optional[float]=None, 
                growth:Optional[float]=None, 
                imagePixmap:Optional[QPixmap]=None, 
                chartPixmap: Optional[QPixmap] = None,
                parent = None):
        super(AssetPreview, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "assetPreview.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.symbol = symbol
        self.name = name
        self.price = price
        self.growth = growth
        self.imagePixmap = imagePixmap
        self.chartPixmap = chartPixmap
        
        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()
        self.setFonts()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
    
    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit the custom clicked signal
        super().mousePressEvent(event)

    def setContents(self):
        if self.imagePixmap:
            self.imageLabel.setPixmap(self.imagePixmap)
        if self.chartPixmap:
            self.chartLabel.setPixmap(self.chartPixmap)

        self.nameLabel.setText(self.name)
        self.priceLabel.setText(f"{self.price}")
        side = 40
        if self.growth >= 0:
            self.growthLabel.setText(f"+{self.growth:.2f}%")
            self.growthLabel.setStyleSheet(
                """QLabel {
                    color: green;
                    background: none;
                    border-style: none;
                }"""
            )
            icon = QIcon(getFrozenPath(os.path.join("assets", "icons", "up.png")))
            self.icon.setIcon(icon)
            self.icon.setIconSize(QSize(side, side))

        else:
            self.growthLabel.setText(f"{self.growth:.2f}%")
            self.growthLabel.setStyleSheet(
                """QLabel {
                    color: red;
                    background: none;
                    border-style: none;
                }"""
            )
            icon = QIcon(getFrozenPath(os.path.join("assets", "icons", "down.png")))
            self.icon.setIcon(icon)
            self.icon.setIconSize(QSize(side, side))


    def setFonts(self):
        size = FontSizePoint
        font = RobotoSemiBold(size.SMALL) or QFont("Arial", size.SMALL)
        for obj in self.children():
            obj.setFont(font)