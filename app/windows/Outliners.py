import os
import asyncio
from typing import Any, Dict, List

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame

from app.config.fonts import QuicksandRegular, FontSizePoint
from utils.databases import mongoGet
from utils.asyncJobs import asyncWrap
from utils.logs import Logger
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

class MarketOutliner:
    def __init__(self, connection: MongoClient) -> None:
        self.logger = Logger("Market-Outlines")
        self.default_outline_type = "default_void"
        self.default_outline_data = [{self.default_outline_type: None}]

        self.connection = connection

    async def get(self, endpoint: str) -> List[Dict]:
        await asyncio.sleep(0.1)
        try:
            asyncMongoGet = asyncWrap(mongoGet)
            res: Any = await asyncMongoGet(database="market", collection="marketSummary", connection=self.connection)
            doc: Dict = res[0] if res else {}
            target = doc["content"]["performances"]
            return target[endpoint]
        except Exception as e:
            self.logger.log("error", "Asset:: Outline Creation error ", e)
            return []

    async def gainers(self):
        return await self.get("biggestGainers")

    async def losers(self):
        return await self.get("biggestLosers")

    async def mostactive(self):
        return await self.get("mostActives")

    async def sectorPerformances(self):
        return await self.get("sectorPerformance")


class Outline(QFrame):
    def __init__(self, parent=None):
        super(Outline, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "outline.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setFonts()

    def setFonts(self):
        size = FontSizePoint
        font = QuicksandRegular(size.MEDIUM) or QFont('Arial', size.MEDIUM)
        self.symbolLabel.setFont(font)
        self.nameLabel.setFont(font)
        self.priceLabel.setFont(font)
        self.priceChangeLabel.setFont(font)
        self.growthLabel.setFont(font)

class OutlineTitle(QFrame):
    def __init__(self, parent=None):
        super(OutlineTitle, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "outlineTitle.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()


    def initUI(self):
        adjustForDPI(self)
        self.setFonts()

    def setFonts(self):
        size = FontSizePoint
        font = QuicksandRegular(size.BIG) or QFont('Arial', size.BIG)
        self.titleLabel.setFont(font)

async def main():
    outliner = MarketOutliner()
    gainers = await outliner.gainers()
    losers = await outliner.losers()
    most_active = await outliner.mostactive()
    sector_performances = await outliner.sectorPerformances()


    # Do something with the data
    print(gainers[0])

if __name__ == "__main__":
    asyncio.run(main())