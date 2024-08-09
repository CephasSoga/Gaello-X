import os
import asyncio
from typing import Dict, List

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame

from app.windows.Fonts import QuicksandRegular
from utils.databases import mongoGet
from utils.logs import Logger

class MarketOutliner:
    def __init__(self):
        self.logger = Logger("Market-Outlines")
        self.default_outline_type = "default_void"
        self.default_outline_data = [{self.default_outline_type: None}]

    async def get(self, endpoint: str) -> List[Dict]:
        await asyncio.sleep(0.1)
        try:
            doc: Dict = mongoGet(database="market", collection="marketSummary")[0]
            target = doc["content"]["performances"]
            return target[endpoint]
        except Exception as e:
            self.logger.log("error", "Asset:: Outline Creation error ", e)
            return self.default_outline_data

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
        path = os.path.join("UI", "outline.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        self.setFonts()

    def setFonts(self):
        font = QuicksandRegular(10) or QFont('Arial', 10)
        self.symbolLabel.setFont(font)
        self.nameLabel.setFont(font)
        self.priceLabel.setFont(font)
        self.priceChangeLabel.setFont(font)
        self.growthLabel.setFont(font)

class OutlineTitle(QFrame):
    def __init__(self, parent=None):
        super(OutlineTitle, self).__init__(parent)
        path = os.path.join("UI", "outlineTitle.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()


    def initUI(self):
        self.setFonts()

    def setFonts(self):
        font = QuicksandRegular(12) or QFont('Arial', 12)
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