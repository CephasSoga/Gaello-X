import os
import uuid
import json
from typing import Dict
from pathlib import Path

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from app.assets.HashWorker import Hasher
from utils.fileHelper import hideFolder
from utils.paths import constructPath

class UserCredentials:
    def __init__(self, **fields):
        self.userField: Dict[str, str] = fields.get('user', {})
        self.companyField: Dict[str, str] = fields.get('company', {})
        self.accountTypeField:  Dict[str, str] = fields.get('accountType', {})
        self.prospectedField: Dict[str, str] = fields.get('prospected', {})

    def integratePswdHash(self, pswdHash: bytes):
        self.userField = {
            "firstName": self.userField.get('firstName'),
            "lastName": self.userField.get('lastName'),
            "email": self.userField.get('email'),
            "password": pswdHash,
        }
        return self
    
    def toDict(self):
        return {
            "user": self.userField,
            "company": self.companyField,
            "accountType": self.accountTypeField,
            "prospected": self.prospectedField,
        }


class UserAuthentification:
    def __init__(self, connection_str: str):
        self.client = MongoClient(connection_str, server_api=ServerApi('1'))
        self.database: Database = self.client.UsersAuth
        self.users: Collection = self.database.users

        self.hasher = Hasher()

    def login(self, email: str, password: str) -> bool:
        user = self.users.find_one({"user.email": email})
        if user:
            credentials = UserCredentials(**user)
            storedPassword = credentials.userField.get('password')
            if storedPassword and self.hasher.matchPswds(storedPassword, password):
                return True
            if not storedPassword:
                return False
        return False

    def register(self, credentials: UserCredentials) -> bool:
        email = credentials.userField.get('email')
        if not email:
            raise ValueError('UserCredentials.UserField: Email is empty')
        if self.users.find_one({"user.email": email}):
            return False

        password = credentials.userField.get('password')
        if not password:
            raise ValueError('UserCredentials.userField: Password is empty')
        
        hashedPassword = self.hasher.hashPswd(password)
        credentials = credentials.integratePswdHash(hashedPassword)
        credDict = credentials.toDict()
        self.users.insert_one(credDict)

        # Dump none-sensible fields into a local persistent file
        self.save(
            {
                "email": credDict.get('user', {}).get('email', ""),
                "id": uuid.uuid4().hex,
                "loggedIn": True,
                "presistentLoggedIn": True,
                "authorisationLevel": 0
            }
        )
        return True

    def save(self, cred: Dict):
        baseFolder = Path(os.getenv('APP_BASE_PATH'))
        credentialsPath = constructPath(baseFolder,  r'credentials\credentials.json')
        credentialsPath.parent.mkdir(parents=True, exist_ok=True)

        with credentialsPath.open('w') as f:
            json.dump(cred, f)

        # Hide credentials folder
        try:
            #hideFolder(baseFolder)
            _ = 1
        except Exception as e:
            _ = 0
            print(e)

    def delete_user(self, email: str) -> bool:
        result = self.users.delete_one({"user.email": email})
        return result.deleted_count > 0


# MongoDB connection string
connection_str = os.getenv("MONGO_URI")
# Create UsersAuth instance
userAuthInstance = UserAuthentification(connection_str)

if __name__ == "__main__":

    # Create UsersAuth instance
    auth = UserAuthentification(connection_str)

    # Test credentials
    test_credentials = UserCredentials(user={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "my_secure_password"
    })

    # Register user
    if auth.register(test_credentials):
        print("User registered successfully")

    # Attempt login
    if auth.login("john.doe@example.com", "my_secure_password"):
        print("Login successful")
    else:
        print("Login failed")

    # Delete user
    #if auth.delete_user("john.doe@example.com"):
    #    print("User deleted successfully")
