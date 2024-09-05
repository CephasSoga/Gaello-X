import os
from typing import List, Dict
from urllib.parse import quote_plus

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from utils.logs import Logger
from utils.envHandler import getenv

logger = Logger("Utils-Databases")

uri = getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def mongoGet(database: str = "market", collection: str = ..., sortField: str = "date", limit: int = 1, connection: MongoClient = client, **kwargs) -> List[Dict]:
    """
    This function retrieves documents from a specified MongoDB collection based on the provided parameters.

    Parameters:
    - database (str): The name of the MongoDB database. Default is "market".
    - collection (str): The name of the MongoDB collection. This parameter is required.
    - sortField (str): The field to sort the documents by. Default is "date".
    - limit (int): The maximum number of documents to retrieve. Default is 1.
    - connection (MongoClient): The MongoDB client to use. If not provided, a new client will be created.
    - kwargs (Dict): Additional query parameters to filter the documents.

    Returns:
    - List[Dict]: A list of dictionaries representing the retrieved documents. If no documents are found, an empty list is returned.
    """
    if connection:
        client = connection
    
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

def mongoUpdate(database: str = "market", collection: str = ..., query: Dict = {}, update: Dict = {}, scale: str = 'one'):
    """
    This function updates documents in a specified MongoDB collection based on the provided parameters.

    Parameters:
    - database (str): The name of the MongoDB database. Default is "market".
    - collection (str): The name of the MongoDB collection. This parameter is required.
    - query (Dict): A dictionary representing the query to identify the documents to update.
    - update (Dict): A dictionary representing the update operations to be performed.
    - scale (str): The scale of the update operation. It can be either 'one' or 'many'. Default is 'one'.

    Returns:
    - bool: Returns True if the update operation is successful and at least one document is modified.
            Returns False if the update operation fails or no document is modified.
    """
    try:
        #confirm successful connection
        state = client.admin.command('ping')
        if state['ok'] == 1:
            db: Database = client[database]
            collection: Collection = db[collection]
            if scale == 'one':
                result = collection.update_one(query, update)
                return result.modified_count > 0
            elif scale == 'many':
                result = collection.update_many(query, update)
                return result.modified_count > 0
            
            else:
                raise ValueError('Invalid scale')            
        else:
            e = Exception("MongoDB > Update:: Connection failed.")
            logger.log(level='error', message="", error=e)
            return False
        
    except Exception as e:
        logger.log(
            level='error',
            message="MongoDB > Update:: An error occurred while updating documents.",  
            error=e,
            params={
                'database': database,
                'collection': collection,
                'query': query,
                'update': update
            })
        return False
    
    finally:
        #client.close()
        pass
