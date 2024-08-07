import os
import aiohttp
import asyncio
import dotenv
from datetime import datetime, timedelta
from typing import Union, Optional

dotenv.load_dotenv()

class SymbolPattern:
    def __init__(self,
        symbol: str,
        name: Optional[str] = None,
        exchange: Optional[str] = None,
        exchangeShortName: Optional[str] = None
    ):
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
        self.exchangeShortName = exchangeShortName

class Symbol:
    def __init__(self, args: SymbolPattern):
        self.symbol = args.symbol
        self.name = args.name
        self.exchange = args.exchange
        self.exchangeShortName = args.exchangeShortName

class Index:
    def __init__(self, args: SymbolPattern):
        self.symbol = args.symbol
        self.name = args.name
        self.exchange = args.exchange
        self.exchangeShortName = args.exchangeShortName

class Series:
    def __init__(self, asset: Union[Index, Symbol], interval:int=60):
        self.apikey = os.getenv("FMP_API_KEY")
        self.symbol = asset.symbol
        self.name = asset.name
        self.exchange = asset.exchange
        self.exchangeShortName = asset.exchangeShortName
        self.baseUrl = "https://financialmodelingprep.com/api/v3/historical-price-full/"
        today = datetime.now().date()
        self.startTime = (today - timedelta(days=interval)).isoformat()
        self.endTime = today.isoformat()

    async def historical(self, interval: str = "daily"):
        try:
            target = f"{self.baseUrl}{self.symbol}"
            params = {
                "apikey": self.apikey,
                "from": self.startTime,
                "to": self.endTime,
                "interval": interval
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(target, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if "historical" not in data:
                        raise Exception("Unexpected API response format")

                    dates = []
                    opens= []
                    lows = []
                    highs = []
                    closes = []
                    for item in data["historical"]:
                        dates.append(item["date"])
                        opens.append(item["open"])
                        lows.append(item["low"])
                        highs.append(item["high"])
                        closes.append(item["close"])

                    lastClose = closes[0]
                    previousClose = closes[1]

                    growth = 100 * (lastClose - previousClose)/previousClose

                    return {
                        "dates": dates,
                        "opens": opens,
                        "lows": lows,
                        "highs": highs,
                        "closes": closes,
                        "price": lastClose,
                        "growth": growth,
                    }

        except aiohttp.ClientError as ce:
            print(f"AIOHTTP error occurred on Series Creation: {ce}")
            return {
                "dates": [],
                "opens": [],
                "lows": [],
                "highs": [],
                "closes": [],
                "price": 0,
                "growth": 0,
            }

        except Exception as e:
            print(f"Other error occurred on Series Creation: {e}")
            return {
                "dates": [],
                "opens": [],
                "lows": [],
                "highs": [],
                "closes": [],
                "price": 0,
                "growth": 0,
            }


async def main():
    asset = Symbol(SymbolPattern(symbol="AAPL"))
    series = Series(asset)
    historical_data = await series.historical()
    print(historical_data["dates"][0])

if __name__ == "__main__":
    asyncio.run(main())