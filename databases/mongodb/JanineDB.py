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
    def __init__(self, connectionStr: str, user: str="User"):
        self.client = MongoClient(connectionStr)
        self.database: Database = self.client.JanineDB

        self.user = user
        self.chatHistory: Collection = self.database[f'{id}-{email}']

    def insert(self, item: Dict[str, Any]):
        insert(self.chatHistory, item)

    def history(self):
        return fetchAll(self.chatHistory)
    
    def deleteExcess(self, max:int=50):
        """Chat context up to 50 chat items."""
        count = self.chatHistory.count_documents({})
        excess = count-max
        print(f"Database contains {count} documents")
        if excess > 0:
            deleteMany(self.chatHistory, limit=excess)
    
connectionStr = getenv("MONGO_URI")

janineDB = JanineMongoDatabase(connectionStr)
chatHistory = janineDB.chatHistory