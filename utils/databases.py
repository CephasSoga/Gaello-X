import os
from typing import List, Dict
from urllib.parse import quote_plus

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from utils.logs import Logger
from utils.envHandler import getenv

logger = Logger(__name__)

uri = getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def mongoGet(database: str = "market", collection: str = ..., sortField: str = "date", limit: int = 1, **kwargs) -> List[Dict]:
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
        return
    
    finally:
        #client.close()
        pass

