from typing import Dict, Any

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo import DESCENDING
from pymongo.errors import ConnectionFailure, CollectionInvalid

from databases.mongodb.Operations import *
from utils.envHandler import getenv
from utils.logs import Logger
from models.reader.cache import cached_credentials
from models.config.args import ModelsArgs

connectionStr = getenv("MONGO_URI")
logger = Logger("MongoDB-Janine")
ID = cached_credentials.get("id", None)
EMAIL = cached_credentials.get("email", None)
if not ID or not EMAIL:
    logger.log('warning', 'Empty user credentials.', ValueError('User credentials not found in cache.'))

class JanineMongoDatabase:
    def __init__(self, uri: str = connectionStr, user: str=f'{ID}-{EMAIL}', title: str = None, connection: MongoClient = None):
        self.uri = uri
        self.user = user.split('.')[0][:36] # Comply with mongodb db name max length
        self.id: str  = ID
        self.email: str = EMAIL
        self.client = None if not connection else connection
        self.database: Database = None
        self.chatCollections: list[str] = None
        self.chatHistory: Collection = None
        self.title = title

    def connect(self):
        """
        Connects to the MongoDB database.
        """
        try:
            if not self.client:
                self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.database = self.client[self.user]
        except ConnectionFailure as  conn_failure:
            logger.log("error", "Failed to connect to MongoDB", conn_failure)
        except Exception as e:
            logger.log("error", "Failed to create/connect to MongoDB database", e)

    def createChat(self, title: str = None):
        """
        Creates the chat history collection if it does not exist.
        """
        try:
            self.connect()
            if self.title is not None:
                self.chatHistory = self.database[self.title]
            else:
                if title:
                    self.chatHistory = self.database[title]
                else:
                    logger.log("error", "Chat title not provided", ValueError("Chat title not provided"))
        except CollectionInvalid as col_invalid:
            logger.log("error", "Invalid title: Failed to create chat history collection", col_invalid)
        except Exception as e:
            logger.log("error", "Failed to create chat", e)

    def getCollections(self):
        try:
            self.ensureMetadataIndex()
            self.chatCollections = self.getSortedCollections()
            if self.chatCollections and len(self.chatCollections) > 0:
                if self.title is not None:
                    self.chatHistory = self.database[self.title]
                else:
                    recentChat = self.chatCollections[-1]
                    self.chatHistory = self.database[recentChat]
            else:
                self.chatHistory = None
                self.chatCollections = None
            return self.chatCollections
        except Exception as e:
            logger.log("error", "Failed to get collections", e)
            return None
    
    def ensureMetadataIndex(self):
        """
        Ensure that a metadata collection exists and has an index on 'createdAt' field.
        """
        try:
            metadataCollection = self.database['metadata']
            # Create index on 'createdAt' field if it does not exist
            index = metadataCollection.index_information()
            if 'createdAt_DESC' not in index:
                # Create index on 'createdAt' field
                metadataCollection.create_index([('chat.createdAt', DESCENDING)])
        except Exception as e:
            logger.log("error", "Failed to create metadata index", e)
    
    def getSortedCollections(self, limit: int = ModelsArgs.MAX_CHAT_COLLECTIONS):
        metadataCollection = self.database['metadata']
        recentCollections = metadataCollection.find().sort('chat.createdAt', -1).limit(limit)
        # Extract collection names
        titles = [doc['chat']['title'] for doc in recentCollections]
        return titles

    def insert(self, item: Dict[str, Any]):
        """
        Inserts a chat history item into the MongoDB collection.

        Parameters:
        item : Dict[str, Any]
            The chat history item to be inserted.
        """
        if self.chatHistory is None:
            raise Exception("Chat history collection not initialized")
        insert(self.chatHistory, item)

    def history(self):
        """
        Retrieves all chat history items from the MongoDB collection.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the chat history items.
        """
        if self.chatHistory is None:
            raise Exception("Chat history collection not initialized")
        elif self.chatCollections:
            history = []
            hist_list =[fetchAll(self.database[collection]) for collection in self.chatCollections]
            for hist in hist_list:
                if isinstance(hist, list):
                    for item in hist:
                        history.append(item)
                else:
                    history.append(hist)
            return history
        elif not self.chatCollections and self.chatHistory is not None:
            return fetchAll(self.chatHistory)
        else:
            return []
    
    def deleteExcess(self, max:int=ModelsArgs.MAX_CHAT_DOCS):
        """Chat context up to specified max chat items. Delete the excess."""
        if self.chatHistory is None:
            raise Exception("Chat history collection not initialized")
        count = self.chatHistory.count_documents({})
        excess = count-max
        print(f"Database contains {count} documents")
        if excess > 0:
            deleteMany(self.chatHistory, limit=excess)

    def delete(self, query: Dict[str, Any]):
        """
        Deletes a chat history item from the MongoDB collection based on a query.

        Parameters:
        query : Dict[str, Any]
            The query to match the chat history item to be deleted.
        """
        if self.chatHistory is None:
            raise Exception("Chat history collection not initialized")
        delete(self.chatHistory, query)