import os
from urllib.parse import quote_plus

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from utils.logs import Logger

logger = Logger(__name__)

uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def mongoGet(database: str = "market", collection: str = ..., sortField: str = "date", limit: int = 1, **kwargs):
    """
    Retrieves documents from a MongoDB collection based on the provided parameters.

    Args:
        database (str): The name of the MongoDB database. Default is "market".
        collection (str): The name of the MongoDB collection. This parameter is required.
        sortField (str): The field to sort the documents by. Default is "date".
        limit (int): The maximum number of documents to retrieve. Default is 1.
        **kwargs: Additional query parameters to filter the documents.

    Returns:
        List[Dict]: A list of dictionaries representing the retrieved documents. If no documents are found, an empty list is returned.

    Raises:
        Exception: If the connection to the MongoDB server fails or an error occurs while fetching the documents.

    Note:
        The MongoDB client is created using the `client` object, which is assumed to be defined elsewhere in the codebase.
    """
    try:
        #confirm successful connection
        state = client.admin.command('ping')
        if state['ok'] == 1:
            db: Database = client[database]
            collection: Collection = db[collection]

            documents = collection.find(kwargs).sort([(sortField, -1)]).limit(limit=limit)
        
            return list(documents)
        else:
           e = Exception("MongoDB > Retrieval:: Connection failed.")
           logger.log(level='error', message="", error=e)
    except Exception as e:
        logger.log(
            level='error',
            message="MongoDB > Retrieval:: An error occurred while fetching documents.",  
            error=e,
            params={
                'database': database,
                'collection': collection,
                'kwargs': kwargs,
                'limit': limit,
                'sortField': sortField,
            })
        raise(e)
    
    finally:
        #client.close()
        pass

