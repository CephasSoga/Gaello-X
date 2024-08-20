import os

from PyQt5 import  uic
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QFrame

from app.windows.AuthHandler import read_user_id
from app.windows.NewAccountPlan import NewAccountPlan
from utils.appHelper import setRelativeToMainWindow, adjustForDPI
from utils.paths import getFrozenPath

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
        id = read_user_id()
        if id:
            self.idLabel.setText(f"Account ID: {id}")
            self.idLabel.setAlignment(Qt.AlignCenter)

    def connectSlots(self):
        self.changePlanButton.clicked.connect(self.spawnAccountPlan)
        self.settingsButton.clicked.connect(self.spawnSettings)

    def spawnAccountPlan(self):
        parent = self.parent() # Stands for TopWidget widget
        self.accountPlanWidget = NewAccountPlan(self)
        self.hide()
        setRelativeToMainWindow(self.accountPlanWidget, parent, 'center')


    def spawnSettings(self):
        pass