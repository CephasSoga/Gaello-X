import os
import aiohttp
import asyncio
import dotenv

dotenv.load_dotenv()

class Assets:
    """
    A class used to interact with the financial modeling prep API to fetch financial assets data.

    Description:
    -----------
    An aseet is either a stock, a currency pair, a cryptocurrency, an option, an index or any other financial product.

    Attributes
    ----------
    apikey : str
        The API key for accessing the financial modeling prep API.
    url : str
        The base URL for the financial modeling prep API.

    Methods
    -------
    stocks()
        Asynchronously fetches stock data from the financial modeling prep API.

    """
    def __init__(self):
        """
        Initializes the Assets class with the necessary API key and URL.

        This function retrieves the API key from the environment variables and sets it as an instance variable. It also sets the URL for the financial modeling prep API as an instance variable.

        Parameters:
            None

        Returns:
            None
        """
        self.apikey = os.getenv("FMP_API_KEY")
        self.url = "https://financialmodelingprep.com/api/v3/stock/list"

    async def stocks(self):
        """
        Asynchronously fetches stock data from the financial modeling prep API.

        This function sends a GET request to the financial modeling prep API to retrieve stock data. It uses the aiohttp library to make the asynchronous request.

        Parameters:
            None

        Returns:
            A dictionary containing the stock data retrieved from the API. If an error occurs during the request, it prints the error message and returns None.
        """
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
