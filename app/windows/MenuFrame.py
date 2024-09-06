import os
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Callable

from PyQt5 import  uic
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QFrame, QMessageBox

from app.windows.AccountPlanChangeFrame import AccountPlanChange
from app.windows.LoginFrame import SignInFrame
from app.handlers.AuthHandler import sync_read_user_cred_file
from app.windows.NewAccountPlan import NewAccountPlan
from app.windows.NewAccountOk import AccountAllSet, AccountInitFailure
from utils.appHelper import setRelativeToMainWindow, adjustForDPI, showWindow
from utils.paths import getFrozenPath
from utils.paths import getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from utils.asyncJobs import asyncWrap
from utils.databases  import mongoGet

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
        except FileNotFoundError:
            sign_in = SignInFrame()
            showWindow(sign_in)
            
    def connectSlots(self):
        self.logoutButton.clicked.connect(self.logout)
        self.changePlanButton.clicked.connect(self.changePlan)
        self.settingsButton.clicked.connect(self.spawnSettings)

    def logout(self):
        pathOnSystem = os.path.join(
            getenv('APP_BASE_PATH'), 'credentials', 'credentials.json'
        )
        targetFile = Path(getFileSystemPath(pathOnSystem))

        if targetFile.exists():
            try:
                targetFile.unlink()
            except Exception:
                try: 
                    os.remove(targetFile)
                except Exception:
                    QMessageBox.critical(None, "Error", "Failed to delete credentials. Please try again later.")

            QMessageBox.information(None, "Logged Out", "You have been logged out.\nOptionally restart the app to make the logout effective.")
            _delayAfterLogout = 0.5
            time.sleep(_delayAfterLogout) # sleep to make sure operation was completed
        else:
            QMessageBox.information(None, "Not Logged In", "You are already logged out.")


    def changePlan(self):
        parent = self.parent() # Stands for TopWidget widget
        self.accountPlanChanger = AccountPlanChange(self.connection)
        self.hide()
        setRelativeToMainWindow(self.accountPlanChanger, parent, 'center')

    def spawnSettings(self):pass


    async def deleteSubscription(self, subscriptionId: str, accessToken: str, mode: str = "live"):
        pass

    async def deleteSubscriptionWithNoFail(self, subscriptionId: str, accessToken: str, mode: str = "live"):
        pass

    def asyncTosync(self, func: Callable, *args, **kwargs):
        return asyncio.ensure_future(func(*args, **kwargs))

