import os
import aiohttp
import asyncio
import dotenv

dotenv.load_dotenv()

class Assets:
    def __init__(self):
        self.apikey = os.getenv("FMP_API_KEY")
        self.url = "https://financialmodelingprep.com/api/v3/stock/list"

    async def stocks(self):
        try:
            params = {
                "apikey": self.apikey,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, params=params) as response:
                    response.raise_for_status()
                    stocks = await response.json()
                    return stocks
        except aiohttp.ClientError as ce:
            print(f"AIOHTTP error occurred on Asset Creation: {ce}")
        except Exception as e:
            print(f"Other error occurred on Asset creation: {e}")

async def main():
    assets = Assets()
    stocks = await assets.stocks()
    print(stocks[0])

if __name__ == "__main__":
    asyncio.run(main())
