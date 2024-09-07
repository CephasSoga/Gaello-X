from typing import List, Dict, Optional

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from utils.logs import Logger

logger = Logger("Utils-Databases")

def mongoGet(database: str = "market", collection: str = ..., sortField: str = "date", limit: int = 1, connection: Optional[MongoClient] = None, **kwargs) -> List[Dict]:
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
    
    Raises:
    - ValueError: If the connection argument is not provided.
    """

    if connection is None:
        raise ValueError("MongoDB > Retrieval:: Connection not provided.")
    
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

def mongoUpdate(database: str = "market", collection: str = ..., query: Dict = {}, update: Dict = {}, scale: str = 'one', connection: Optional[MongoClient] = None):
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

    Raises:
    - ValueError: If the connection argument is not provided or the scale argument is not 'one' or 'many'.
    """
    if connection is None:
        raise ValueError("MongoDB > Retrieval:: Connection not provided.")
    
    client = connection

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


def mongoDeleteOne(database: str, collection: str, filter: Dict, connection: Optional[MongoClient] = None):
    """
    This function deletes one document from a specified MongoDB collection based on the provided filter.
    
    Parameters:
    - database (str): The name of the MongoDB database.
    - collection (str): The name of the MongoDB collection.
    - filter (Dict): A dictionary representing the filter to identify the document to delete.
    - connection (MongoClient): The MongoDB client to use. If not provided, a new client will be created.
    
    Returns:
    - bool: Returns True if the deletion operation is successful. Returns False if the deletion operation fails.
    
    Raises:
    - ValueError: If the connection argument is not provided.
    """

    if connection is None:
        raise ValueError("MongoDB > Retrieval:: Connection not provided.")
    
    client = connection
    
    try:
        #confirm successful connection
        state = client.admin.command('ping')
        if state['ok'] == 1:
            db: Database = client[database]
            collection: Collection = db[collection]
            result = collection.delete_one(filter)
            return result.deleted_count > 0
        else:
            e = Exception("MongoDB > Delete:: Connection failed.")
            logger.log(level='error', message="", error=e)
            return False
        
    except Exception as e:
        logger.log(
            level='error',
            message="MongoDB > Delete:: An error occurred while deleting documents.",  
            error=e,
            params={
                'database': database,
                'collection': collection,
                'filter': filter
            })
        return False