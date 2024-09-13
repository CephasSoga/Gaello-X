import os
import uuid
import json
from pathlib import Path

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QLayout

from app.windows.MessageBox import MessageBox
from utils.paths import getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from utils.appHelper import setRelativeToMainWindow, showWindow
from app.config.fonts import RobotoRegular, FontSizePoint
from app.windows.NewAccountSetup import NewAccountSetup

from databases.mongodb.UsersAuth import UserCredentials, userAuthInstance
from utils.databases import mongoGet


class SignInFrame(QMainWindow):
    def __init__(self, connection: MongoClient, parent=None):
        super(SignInFrame, self).__init__(parent)
        self.newAccountSetupWidget = None  # Initialize as None
        path = getFrozenPath(os.path.join("assets", "UI", "login.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.connection = connection
        self.parent_ = self.parent()
        self.userAuth = userAuthInstance

        # Set the window modality flag to ApplicationModal
        self.setWindowModality(Qt.ApplicationModal)

        self.initUI()


    def initUI(self):
        self.setWFlags()
        self.abstractContents()
        self.connectSlots()
        self.setFonts()

    def abstractContents(self):
        self.passwordEdit.setEchoMode(QLineEdit.Password)

    def setWFlags(self):
        self.setWindowFlag(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.createNewAccount.clicked.connect(self.spawnSetup)
        self.loginButton.clicked.connect(self.login)

    def login(self):
        email = self.emailEdit.text().strip()
        password = self.passwordEdit.text().strip()
        messageBox = MessageBox()

        try:
            if not email or not password:
                
                return

            persistentSessionKey = self.readPersistentSessionManager()
            if not persistentSessionKey:
                #TODO: ...
                if self.userAuth.login(email, password):
                    #TODO: Allow access to restricted windows:  Cleared!
                    messageBox.level("information")
                    messageBox.title("Success")
                    messageBox.message("You are now logged in. \nRestart this appliaction to make login effective ")
                    messageBox.buttons(("ok",))
                    messageBox.exec_()
                    # Recreate persistent login file
                    self.retreiveAndSave(email)
                    self.close()

                else:
                    messageBox.level("warning")
                    messageBox.title("Credentials issue")
                    messageBox.message("Wrong user credentials have been provided.")
                    messageBox.buttons(("ok",))
                    messageBox.exec_()
                    return

            elif  persistentSessionKey == email:
                if self.userAuth.login(email, password):
                    #TODO: Allow access to restricted windows
                    messageBox.level("information")
                    messageBox.title("Success")
                    messageBox.message("You are now logged in. \nRestart this appliaction to make login effective ")
                    messageBox.buttons(("ok",))
                    messageBox.exec_()
                    self.close()
                else:
                    messageBox.level("warning")
                    messageBox.title("Credentials issue")
                    messageBox.message("Wrong user credentials have been provided.")
                    messageBox.buttons(("ok",))
                    messageBox.exec_()
                    return

            else:
                messageBox.level("warning")
                messageBox.title("Credentials issue")
                messageBox.message("Wrong user credentials have been provided.")
                messageBox.buttons(("ok",))
                messageBox.exec_()
                return

        finally:
            self.emailEdit.clear()
            self.passwordEdit.clear()


    def readPersistentSessionManager(self):
        base_path = getFileSystemPath(getenv("APP_BASE_PATH"))
        credentials_path = Path(os.path.join(base_path, 'credentials', 'credentials.json'))
        if not credentials_path.exists():
            return None
        else:
            with credentials_path.open('r') as f:
                credentials = json.load(f)
                email: str = credentials.get('email')
        return email

    def retreiveAndSave(self, email: str):
        users = mongoGet(database='UsersAuth', collection="users", connection=self.connection, limit=int(1e7))
        this_user = [user for user in users if user['user']['email'] == email]
        user = this_user[0] if this_user else None

        credentials = UserCredentials(**user)

        credDict = credentials.toDict(id=user.get("userId", uuid.uuid4().hex))
        self.userAuth.save(
            {
                "email": credDict.get('user', {}).get('email', ""),
                "id": credDict.get('userId', ""),
                "loggedIn": True,
                "presistentLoggedIn": True,
                "authorisationLevel": 'defined',
            }
        )

    def spawnSetup(self):
        if self.newAccountSetupWidget is None:  # Create only when needed
            self.newAccountSetupWidget = NewAccountSetup(connection=self.connection, parent=self.parent_)
        self.newAccountSetupWidget.hide()
        if self.parent_ is not None:
            setRelativeToMainWindow(self.newAccountSetupWidget, self.parent_, 'center')
        else:
            showWindow(self.newAccountSetupWidget)
        self.hide()
    
    def setFonts(self):
        size = FontSizePoint
        font = RobotoRegular(size.SMALL) or QFont("Arial", size.SMALL)
        for obj in [self.emailEdit, self.passwordEdit, self.loginButton, self.createNewAccount]:
            if not isinstance(obj, QLayout):
                obj.setFont(font)



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    window = SignInFrame()
    window.show()
    app.exec_()

        