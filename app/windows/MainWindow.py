import json
import os
from pathlib import Path

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QSizePolicy

from app.windows.LoginFrame import SignInFrame
from app.windows.MenuFrame import AccountMenu
from app.windows.TopWidget import Header
from app.windows.BottomWidget import Bottom
from utils.appHelper import stackOnCurrentWindow, setRelativeToMainWindow, isFrozen, adjustForDPI
from utils.paths import constructPath, getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from app.config.renderer import ViewController

class MainWindow(QMainWindow):
    finishedLoading = pyqtSignal()
    def __init__(self, connection: MongoClient):
        super(MainWindow, self).__init__()
        path = getFrozenPath(os.path.join("assets", "UI", "mainwindow.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection
        
        self.initUI()

    def initUI(self):
        try:
            w, h = adjustForDPI(self)
            print(f"Window size: {w} x {h}")
            self.setWFlags()
            self.setWIcon()
            self.setLayout(w=w, h=h)
            self.connectSlots()
        finally:
            self.finishedLoading.emit()

    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    def setWIcon(self):
        iconPath = getFrozenPath(os.path.join("assets", "logo", "cube-log-big.png"))
        self.setWindowIcon(QIcon(iconPath))

    def setLayout(self, w: int, h: int):
        screenGeometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screenGeometry)

        self.scrollArea.setStyleSheet("border-style: none;")
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scrollWidget = QWidget()
        self.scrollWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(*ViewController.SCROLL_NO_MARGINS)
        self.scrollLayout.setSpacing(ViewController.NO_SPACING)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollWidget)

        self.header = Header(connection=self.connection, parent=self)
        self.bottom = Bottom(connection=self.connection, parent=self)
        #self.showMaximized()  # or self.showFullScreen()
        self.header.setMinimumSize(w, h)
        self.bottom.setMinimumSize(w, h)

        self.scrollLayout.addWidget(self.header)
        self.scrollLayout.addWidget(self.bottom)

    def closeAndExit(self):
        self.close()
        self.connection.close()
        if not isFrozen():
            exit(0)

    def connectSlots(self):
        self.header.minimize.clicked.connect(self.reduceWindow)
        self.header.closeApp.clicked.connect(self.closeAndExit)
        self.finishedLoading.connect(self.onLoadingFinished)

    def onLoadingFinished(self):
        basePath = Path(
            getFileSystemPath(getenv("APP_BASE_PATH"))
        )
        credentialsPath = constructPath(basePath,  'credentials', 'credentials.json')
        if not os.path.exists(credentialsPath):
            self.spawnAccountSettings()
        else:
            self.header.account.clicked.disconnect()
            self.header.account.clicked.connect(self.spawnAccountDetails)
            self.header.account.setStyleSheet(
            """
                QPushButton {
                    background-color: rgb(135, 206, 235);
                    border-radius: 24px;
                    border-style: none;
                }
            """
            )
            with credentialsPath.open('r') as f:
                credentials = json.load(f)
                # Optionally add more checks for credential validity here
                if credentials.get('email'):
                    # more here (e.g.: db fields matching)
                    pass
                else:
                    self.spawnAccountSettings()

    def spawnAccountSettings(self):
        self.accountConnector = SignInFrame(self)
        stackOnCurrentWindow(self.accountConnector)
    
    def spawnAccountDetails(self):
        self.accountMenu = AccountMenu()
        setRelativeToMainWindow(self.accountMenu, self.header, 'right')

    def reduceWindow(self):
        self.showMinimized()  # This keeps the window in a reduced state (icon in taskbar)