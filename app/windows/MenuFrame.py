import os
import time
from pathlib import Path

from PyQt5 import  uic
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QFrame

from app.windows.MessageBox import MessageBox
from app.windows.AccountPlanChangeFrame import AccountPlanChange
from app.windows.AccountDeletionFrame import AccountDeleteTrigger
from app.windows.LoginFrame import SignInFrame
from app.handlers.AuthHandler import sync_read_user_cred_file
from utils.appHelper import setRelativeToMainWindow, adjustForDPI, showWindow
from utils.paths import getFrozenPath
from utils.paths import getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from utils.databases import mongoGet


class Menu(QFrame):
    def __init__(self, parent=None):
        super(Menu, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "menu.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)

class AccountMenu(QFrame):
    def __init__(self, connection, parent=None):
        super(AccountMenu, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "accountMenu.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setContents()
        self.connectSlots()


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def setContents(self):
        try:
            id = sync_read_user_cred_file().get("id", None)
            if id:
                self.idLabel.setText(f"Account ID: {id}")
                self.idLabel.setAlignment(Qt.AlignCenter)

            email = sync_read_user_cred_file().get("email", None)

            if email:
                users = mongoGet(database='UsersAuth', collection="users", limit=int(1e7), connection=self.connection) # Use a verly large limit to avoid returned range not including user
                this_user = [user for user in users if user['user']['email'] == email]
                user = this_user[0] if this_user else None
                if user:
                    target = "subscription"
                    self.planLabel.setText(f"Account Current Plan: {user.get(target, "")}")
                    self.planLabel.setAlignment(Qt.AlignCenter)
                
        except FileNotFoundError:
            sign_in = SignInFrame(connection=self.connection)
            showWindow(sign_in)
            
    def connectSlots(self):
        self.logoutButton.clicked.connect(self.logout)
        self.changePlanButton.clicked.connect(self.changePlan)
        self.settingsButton.clicked.connect(self.spawnSettings)
        self.deleteAccountButton.clicked.connect(self.deleteAccount)

    def logout(self):
        pathOnSystem = os.path.join(
            getenv('APP_BASE_PATH'), 'credentials', 'credentials.json'
        )
        targetFile = Path(getFileSystemPath(pathOnSystem))

        messageBox = MessageBox()

        if targetFile.exists():
            try:
                targetFile.unlink()
            except Exception:
                try: 
                    os.remove(targetFile)
                except Exception:
                    messageBox.level("critical")
                    messageBox.title("Error")
                    messageBox.message("Failed to delete credentials. Please try again later.")
                    messageBox.buttons(("ok",))
                    messageBox.exec_()
                    return
            messageBox.level("information")
            messageBox.title("Logged Out")
            messageBox.message("You have been logged out.\nOptionally restart the app to make the logout effective.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            _delayAfterLogout = 0.5
            time.sleep(_delayAfterLogout) # sleep to make sure operation was completed
        else:
            messageBox.level("information")
            messageBox.title("Not Logged In")
            messageBox.message("You are already logged out.")
            messageBox.buttons(("ok",))
            messageBox.exec_()

    def changePlan(self):
        parent = self.parent() # Stands for TopWidget widget
        self.accountPlanChanger = AccountPlanChange(self.connection)
        self.hide()
        setRelativeToMainWindow(self.accountPlanChanger, parent, 'center')

    def spawnSettings(self):pass


    def deleteAccount(self):
        accountDeletor = AccountDeleteTrigger(self.connection)
        self.hide()
        setRelativeToMainWindow(accountDeletor, self.parent(), 'center')

    