import os
import time
from pathlib import Path

from PyQt5 import  uic
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QFrame, QMessageBox

from app.handlers.AuthHandler import sync_read_user_cred_file
from app.windows.NewAccountPlan import NewAccountPlan
from utils.appHelper import setRelativeToMainWindow, adjustForDPI
from utils.paths import getFrozenPath
from utils.paths import getFrozenPath, getFileSystemPath
from utils.envHandler import getenv

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
    def __init__(self, parent=None):
        super(AccountMenu, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "accountMenu.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

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
        id = sync_read_user_cred_file().get("id", None)
        if id:
            self.idLabel.setText(f"Account ID: {id}")
            self.idLabel.setAlignment(Qt.AlignCenter)

    def connectSlots(self):
        self.logoutButton.clicked.connect(self.logout)
        self.changePlanButton.clicked.connect(self.spawnAccountPlan)
        self.settingsButton.clicked.connect(self.spawnSettings)

    def logout(self):
        pathOnSystem = os.path.join(
            getenv('APP_BASE_PATH'), 'credentilas', 'credentials.json'
        )
        targetFile = Path(getFileSystemPath(pathOnSystem))

        if targetFile.exists():
            try:
                targetFile.unlink()
            except Exception:
                try: 
                    os.remove(targetFile)
                except Exception:
                    QMessageBox.critical(self, "Error", "Failed to delete credentials. Please try again later.")

            QMessageBox.information(self, "Logged Out", "You have been logged out.\nOptionally restart the app to make the logout effective.")
            _delayAfterLogout = 0.5
            time.sleep(_delayAfterLogout) # sleep to make sure operation was completed


    def spawnAccountPlan(self):
        parent = self.parent() # Stands for TopWidget widget
        self.accountPlanWidget = NewAccountPlan(self)
        self.hide()
        setRelativeToMainWindow(self.accountPlanWidget, parent, 'center')


    def spawnSettings(self):
        pass