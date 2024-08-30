import os
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

from app.config.fonts import RobotoRegular, MontserratRegular, FontSizePoint
from app.windows.InsightItems import InsightItem
from app.inferential.ExportInsights import insights
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI
from app.config.renderer import ViewController
from utils.databases import mongoGet
from utils.asyncJobs import asyncWrap, enumerate_async
from utils.envHandler import getenv

@dataclass
class Insight:
    title: str
    description: str
    date: str
    description: str
    content: str
    image_url: str | list[str]
    urls: list[str]
    labels: list[str]
    tags: list[str]

class JanineInsights(QWidget):

    def __init__(self, parent=None):
        super(JanineInsights, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "insightsWidget.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setupWFlags()
        self.connectSlots()
        self.setupLayout()
        self.setContents()
        self.setFonts()

    def setupLayout(self):
        self.insightslayout = QGridLayout()
        self.insightslayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.insightslayout.setAlignment(Qt.AlignTop)
        self.insightslayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.widget = QWidget()
        self.widget.setLayout(self.insightslayout)

        self.scrollArea.setWidget(self.widget)
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setupWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)


    def connectSlots(self):
        self.close_.clicked.connect(self.close)


    def eventFilter(self, obj, event):
        if event.type() == Qt.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    

    async def gatherInsights(self):
        async_mongGet = asyncWrap(mongoGet)
        today = datetime.now().date().isoformat()
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        latest_collection = today
        data = await async_mongGet(database='insights', collection=latest_collection, limit=int(1e6))
        if not data:
            latest_collection = yesterday
            data = await async_mongGet(database='insights', collection=latest_collection, limit=int(1e6))
            if not data:
                return []
        for doc in data:
            yield doc
    
    async def setContents(self):
        async for idx, insight in enumerate_async(self.gatherInsights()):
            max_per_row = 3
            row = idx // max_per_row
            col = idx % max_per_row
            insight = Insight(**insight)
            insight_widget = InsightItem(insight, self)
            self.insightslayout.addWidget(insight_widget, row, col)


    def setFonts(self):
        size = FontSizePoint
        regularFont = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        tinyFont = MontserratRegular(size.TINY) or QFont("Arial", size.TINY)
        self.filterLabel.setFont(regularFont)
        self.tuneLabel.setFont(regularFont)
        self.temperatureLabel.setFont(tinyFont)
        self.audacityLabel.setFont(tinyFont)
        self.cycleLabel.setFont(tinyFont)
        self.subjectsCombo.setFont(tinyFont)
        self.locationsCombo.setFont(tinyFont)
        self.assetsCombo.setFont(tinyFont)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = JanineInsights()
    window.show()

    sys.exit(app.exec_())