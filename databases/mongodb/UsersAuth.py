import os
import uuid
import json
from typing import Dict
from pathlib import Path

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database

from app.handlers.HashWorker import Hasher
from utils.fileHelper import hideFolder
from utils.paths import constructPath, getFileSystemPath
from utils.envHandler import getenv

class UserCredentials:
    """
    A class representing user credentials.

    Attributes:
    -----------
    userField : Dict[str, str]
        A dictionary containing user information such as first name, last name, and email.
    companyField : Dict[str, str]
        A dictionary containing company information.
    accountTypeField : Dict[str, str]
        A dictionary containing account type information.
    prospectedField : Dict[str, str]
        A dictionary containing prospected information.

    Methods:
    --------
    integratePswdHash(pswdHash: bytes) -> Self
        Integrates a password hash into the user field of the object.

    toDict() -> dict
        Returns a dictionary representation of the object.
    """
    def __init__(self, **fields):
        self.userField: Dict[str, str] = fields.get('user', {})
        self.companyField: Dict[str, str] = fields.get('company', {})
        self.accountTypeField:  Dict[str, str] = fields.get('accountType', {})
        self.prospectedField: Dict[str, str] = fields.get('prospected', {})

    def integratePswdHash(self, pswdHash: bytes):
        """
        Integrates a password hash into the user field of the object.

        Args:
            pswdHash (bytes): The password hash to be integrated.

        Returns:
            Self: The updated object with the password hash integrated into the user field.
        """
        self.userField = {
            "firstName": self.userField.get('firstName'),
            "lastName": self.userField.get('lastName'),
            "email": self.userField.get('email'),
            "password": pswdHash,
        }
        return self
    
    def toDict(self, id: str = uuid.uuid4().hex):
        """
        Returns a dictionary representation of the object.

        Args:
            id (str): The unique identifier for the user. Defaults to a random UUID.

        Returns:
            dict: A dictionary containing the following keys:
                - "userId" (str): The user ID. Defaults to a random UUID.
                - "user" (dict): The user field.
                - "company" (dict): The company field.
                - "accountType" (dict): The account type field.
                - "prospected" (dict): The prospected field.
        """
        return {
            "userId": id,
            "user": self.userField,
            "company": self.companyField,
            "accountType": self.accountTypeField,
            "prospected": self.prospectedField,
        }


class UserAuthentification:
    """
    A class representing user authentication and registration functionality.

    Attributes:
    -----------
    client : MongoClient
        A MongoDB client instance for connecting to the database.
    database : Database
        The MongoDB database instance for storing user credentials.
    users : Collection
        The MongoDB collection for storing user credentials.
    hasher : Hasher
        An instance of the Hasher class for hashing and matching passwords.

    Methods:
    --------
    login(email: str, password: str) -> bool
        Authenticates a user with the provided email and password.
    register(credentials: UserCredentials) -> bool
        Registers a new user with the given credentials.
    save(cred: Dict) -> None
        Saves the given credentials to a local persistent file.
    delete_user(email: str) -> bool
        Deletes a user from the database based on their email.
    """
    def __init__(self, connection_str: str, connection: MongoClient = None):
        self.client = connection or MongoClient(connection_str, server_api=ServerApi('1'))
        self.database: Database = self.client.UsersAuth
        self.users: Collection = self.database.users

        self.hasher = Hasher()

    def login(self, email: str, password: str) -> bool:
        """
        Authenticates a user with the provided email and password.

        Args:
            email (str): The email of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            bool: True if the user's credentials are valid, False otherwise.
        """
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
        """
        Register a new user with the given credentials.

        Args:
            credentials (UserCredentials): The user credentials containing the user's email and password.

        Returns:
            bool: True if the user was successfully registered, False otherwise.

        Raises:
            ValueError: If the user's email or password is empty.

        Side Effects:
            - Inserts the user's credentials into the database.
            - Dumps none-sensible fields into a local persistent file.

        """
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
        credDict = credentials.toDict(id=uuid.uuid4().hex)
        self.users.insert_one(credDict)

        # Dump none-sensible fields into a local persistent file
        self.save(
            {
                "email": credDict.get('user', {}).get('email', ""),
                "id": credDict.get('userId', ""),
                "loggedIn": True,
                "presistentLoggedIn": True,
                "authorizationLevel": 'defined'
            }
        )
        return True

    def save(self, cred: Dict):
        """
        Save the given credentials to a local persistent file.

        Args:
            cred (Dict): A dictionary containing the credentials to be saved.

        Returns:
            None

        Raises:
            FileNotFoundError: If the 'APP_BASE_PATH' environment variable is not set.
            Exception: If there is an error while hiding the credentials folder.

        This function saves the given credentials to a local persistent file. It first retrieves the base folder path from the 'APP_BASE_PATH' environment variable. It then constructs the path to the credentials file and creates the necessary directories if they don't exist. The credentials are then saved to the file using the 'json.dump' function. Finally, it attempts to hide the credentials folder, but if there is an error, it prints the exception.
        """
        baseFolder = Path(
            getFileSystemPath(getenv('APP_BASE_PATH'))
        )
        credentialsPath = constructPath(baseFolder,  'credentials', 'credentials.json')
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
        """
        Deletes a user from the database based on their email.

        Args:
            email (str): The email of the user to be deleted.

        Returns:
            bool: True if the user was successfully deleted, False otherwise.
        """
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
