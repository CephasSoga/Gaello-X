import os
import json
from typing import Dict, Any, Tuple

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from databases.mongodb.Operations import *
from utils.envHandler import getenv
from utils.logs import Logger


logger = Logger(__name__)

def read_user_endpoint() -> Tuple[str, str] | None:
    """
    Reads the user endpoint from the credentials file.

    This function retrieves the base path using the "APP_BASE_PATH" environment variable.
    It then constructs the path to the credentials file and attempts to open it.
    If the file is found, it loads the JSON data and returns the user ID and email.
    If the file is not found, it returns None.
    If any other exception occurs during the process, it is re-raised.

    Returns:
        Tuple[str, str] | None: A tuple containing the user ID and email, or None if the file is not found.
    """
    base_path = getenv("APP_BASE_PATH")
    credentials_path = os.path.join(base_path, "credentials/credentials.json")
    try:
        with open(credentials_path, 'r') as credentials_file:
            credentials = json.load(credentials_file)

        return credentials.get('id', ''), credentials.get('email', '')
    except FileNotFoundError:
        return None
    except Exception as e:
        raise(e)

creds_details = read_user_endpoint()

if not creds_details:
    logger.log('error', "Empty credentials", ValueError("Empty credentials"))
    id, email = '', ''
else:
    id, email = creds_details


class JanineMongoDatabase:
    """
    A class used to interact with a MongoDB database for storing chat history.

    Attributes
    ----------
    client : MongoClient
        The MongoDB client used to connect to the database.
    database : Database
        The MongoDB database instance.
    user : str
        The user associated with the chat history.
    chatHistory : Collection
        The MongoDB collection for storing chat history.

    Methods
    -------
    __init__(connectionStr: str, user: str="User")
        Initializes the JanineMongoDatabase instance with a MongoDB connection string and user.

    insert(item: Dict[str, Any])
        Inserts a chat history item into the MongoDB collection.

    history()
        Retrieves all chat history items from the MongoDB collection.

    deleteExcess(max:int=50)
        Deletes excess chat history items from the MongoDB collection to maintain a maximum limit.
    """
    def __init__(self, connectionStr: str, user: str="User"):
        """
        Initializes the JanineMongoDatabase instance with a MongoDB connection string and user.

        Parameters
        ----------
        connectionStr : str
            The MongoDB connection string.
        user : str, optional
            The user associated with the chat history. Default is "User".
        """
        self.client = MongoClient(connectionStr)
        self.database: Database = self.client.JanineDB

        self.user = user
        self.chatHistory: Collection = self.database[f'{id}-{email}']

    def insert(self, item: Dict[str, Any]):
        """
        Inserts a chat history item into the MongoDB collection.

        Parameters:
        item : Dict[str, Any]
            The chat history item to be inserted.
        """
        insert(self.chatHistory, item)

    def history(self):
        """
        Retrieves all chat history items from the MongoDB collection.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the chat history items.
        """
        return fetchAll(self.chatHistory)
    
    def deleteExcess(self, max:int=50):
        """Chat context up to 50 chat items. Delete the excess."""
        count = self.chatHistory.count_documents({})
        excess = count-max
        print(f"Database contains {count} documents")
        if excess > 0:
            deleteMany(self.chatHistory, limit=excess)
    
connectionStr = getenv("MONGO_URI")

janineDB = JanineMongoDatabase(connectionStr)
chatHistory = janineDB.chatHistory