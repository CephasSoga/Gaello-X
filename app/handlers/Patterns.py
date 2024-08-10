import dotenv
from datetime import datetime, timedelta
from typing import Union, Optional, Dict

from utils.databases import mongoGet

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
    def __init__(self, asset: Union[Index, Symbol], interval:int = 60):
        self.asset = asset
        today = datetime.now().date()
        self.startTime = (today - timedelta(days=interval)).isoformat()
        self.endTime = today.isoformat()

    def historical(self, collection:str):
        try:
            docs = mongoGet(collection=collection, symbol=self.asset.symbol)

            if not docs:
                raise Exception("No documents that match this query was found in the database.")

            data: Dict = list(docs)[0]

            target = data["historicalData"]
            index_symbol = target["symbol"]
            index_name = self.asset.name
            quotes = target["quotes"]

            dates = []
            opens = []
            highs = []
            lows = []
            closes = []

            for quote in quotes:
                dates.append(quote["date"].isoformat())
                opens.append(quote["open"])
                highs.append(quote["high"])
                lows.append(quote["low"])
                closes.append(quote["adjClose"])
            
            lastClose = closes[-1]
            previousClose = closes[-2]

            growth = 100 * (lastClose - previousClose) / previousClose

            index_data = {
                "symbol": index_symbol,
                "name": index_name,
                "dates": dates,
                "opens": opens,
                "highs": highs,
                "lows": lows,
                "closes": closes,
                "price": lastClose,
                "growth": growth,
                "lastUpdated": datetime.now().isoformat()

            }

            return index_data 
        except Exception as e:
            raise(e)


def main():
    from app.handlers.ExportAssets import symbolList as l
    asset = l[0]
    series = Series(asset)
    historical_data = series.historical()
    print(historical_data)

if __name__ == "__main__":
   import time
   s = time.perf_counter()
   main()
   e = time.perf_counter()
   print(f"Time elapsed: {e-s:.16f} seconds")
