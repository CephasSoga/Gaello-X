from app.handlers.Patterns import SymbolPattern, Symbol, Index
from app.handlers.Assets import Assets
from typing import List, Any
import asyncio

def complyToPattern(stock: Any) -> Symbol:
    # Construct a Symbol object from stock data
    pattern = SymbolPattern(
        symbol=stock["symbol"],
        name=stock["name"],
        exchange=stock["exchange"],
        exchangeShortName=stock["exchangeShortName"],
    )
    symbol = Symbol(pattern)
    return symbol

async def symbols(semaphoreSize: int = 10) -> List[Symbol]:
    assets = Assets()  # Initialize the Assets object
    semaphore = asyncio.Semaphore(semaphoreSize)  # Limit concurrent requests

    stocks = await assets.getStocks()  # Fetch stocks asynchronously

    # Pre-allocate the symbols list with None placeholders
    symbols = [None] * len(stocks)

    async def collection(index, stock):
        async with semaphore:  # Ensure limited concurrency
            symbol = complyToPattern(stock)
            symbols[index] = symbol  # Store the result in the pre-allocated list

    # Gather and execute all asynchronous collection tasks
    await asyncio.gather(*[collection(index, stock) for index, stock in enumerate(stocks)])

    return symbols  # Return the list of Symbol objects


    

### REDUCE OVERLOAD UNTIL PROJECT IS READY FOR DEPLOYMENT.
### ALSO HELPS AVOID THE FMP API ACTIVELY REFUSING REQUESTS BECAUSE OF THE FREE PLAN THE PROJECT IS USING FOR NOW.
#otherwise use: # symbolList = symbols()
# Define the list of symbols
symbolList = [
    Symbol(SymbolPattern("AAPL", "Apple Inc")),
    Symbol(SymbolPattern("TSLA", "TESLA")),
    Symbol(SymbolPattern("MSFT", "Microsoft Corporation")),
    Symbol(SymbolPattern("AMZN", "Amazon")),
    Symbol(SymbolPattern("GOOG", "Alphabet Inc.")),
    Symbol(SymbolPattern("DIS", "Disney")),
    Symbol(SymbolPattern("NFLX", "Netflix, Inc.")),
    Symbol(SymbolPattern("JPM", "J.P Morgan")),
]

# Define the list of indices
IndexList = [
    Symbol(SymbolPattern(data["symbol"], data["name"]))
    for data in [
        {"symbol": "^GSPC", "name": "S&P 500"},
        {"symbol": "^IXIC", "name": "NASDAQ Composite"},
        {"symbol": "^DJI", "name": "Dow Jones Industrial Average"},
        {"symbol": "^RUT", "name": "Russell 2000"},
        {"symbol": "^FTSE", "name": "FTSE 100"},
        {"symbol": "^N225", "name": "Nikkei 225"},
        {"symbol": "^HSI", "name": "Hang Seng Index"},
        {"symbol": "^STOXX50E", "name": "Euro Stoxx 50"},
        {"symbol": "^AORD", "name": "All Ordinaries"},
        {"symbol": "^BSESN", "name": "BSE Sensex"},
        {"symbol": "^FCHI", "name": "CAC 40"},
        {"symbol": "^GDAXI", "name": "DAX Performance Index"},
        {"symbol": "^KS11", "name": "KOSPI Composite Index"},
        {"symbol": "^TWII", "name": "Taiwan Weighted"},
        {"symbol": "^MXX", "name": "IPC Mexico"},
        {"symbol": "^BVSP", "name": "Bovespa Index"},
        {"symbol": "^MERV", "name": "MERVAL Index"},
        {"symbol": "^AEX", "name": "AEX Amsterdam Index"},
        {"symbol": "^OSEAX", "name": "OSE All Share Index"},
        {"symbol": "^SSMI", "name": "Swiss Market Index"},
        {"symbol": "^GSPTSE", "name": "S&P/TSX Composite Index"},
        {"symbol": "^ATX", "name": "Austrian Traded Index"},
        {"symbol": "^OMX", "name": "OMX Nordic 40"},
        {"symbol": "^NZ50", "name": "NZX 50 Index"},
        {"symbol": "^JKSE", "name": "Jakarta Composite Index"},
        {"symbol": "^KLSE", "name": "FTSE Bursa Malaysia KLCI"},
        {"symbol": "^ISEQ", "name": "ISEQ Overall Index"},
        {"symbol": "^J203", "name": "FTSE/JSE Africa All Share Index"},
        {"symbol": "^TA125.TA", "name": "TA-125"},
        {"symbol": "^XU100", "name": "BIST 100"},
        {"symbol": "^MSCI", "name": "MSCI World Index"},
    ]
]
