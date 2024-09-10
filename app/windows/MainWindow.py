import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox, QMainWindow, QApplication, QVBoxLayout, QSizePolicy

from app.windows.LoginFrame import SignInFrame
from app.windows.MenuFrame import AccountMenu
from app.windows.TopWidget import Header
from app.windows.BottomWidget import Bottom
from utils.appHelper import stackOnCurrentWindow, setRelativeToMainWindow, isFrozen, adjustForDPI
from utils.paths import constructPath, getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from app.config.renderer import ViewController
from app.versions.control import VersionController
from app.versions.download import VersionDownloadManager
from app.versions.info import Version

class MainWindow(QMainWindow):
    finishedLoading = pyqtSignal()
    closedBeforeUpdateTimeout = pyqtSignal() # handle cases where user closes app before update timeout

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
        self.closedBeforeUpdateTimeout.emit()
        if not isFrozen():
            exit(0)
        else:
            sys.exit(0)

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
        self.accountConnector = SignInFrame(connection=self.connection, parent=self)
        stackOnCurrentWindow(self.accountConnector)
    
    def spawnAccountDetails(self):
        self.accountMenu = AccountMenu(connection=self.connection)
        setRelativeToMainWindow(self.accountMenu, self.header, 'right')

    def reduceWindow(self):
        self.showMinimized()  # This keeps the window in a reduced state (icon in taskbar)
    
    async def proceedWithUpdate(self):
        new_version_available = await self.checkForUpdate(getenv("VERSION_CONTROL_URL"))
        if not new_version_available:
            return
        
        permission = self.promptUserForDownload()
        if not permission:
            return

        download = await self.download(new_version_available)
        if not download:
            return

        user_wants_to_update_now = self.promptUserForUpdate()
        if not user_wants_to_update_now:
            return

        # if app was closed before timeout
        self.closedBeforeUpdateTimeout.connect(self.execUpdateScript)
        delay = 15
        self.warnForRestart(delay=delay)
        await asyncio.sleep(delay)
        self.execUpdateScript()
        sys.exit(0)

    async def download(self, version: Version):
        downloader = VersionDownloadManager()
        return await downloader.download(version)

    async def checkForUpdate(self, url):
        controller = VersionController()
        return await controller.check_for_update(url)
    
    def promptUserForDownload(self) -> bool:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("New version available. Would you like to download it?")
        msgBox.setWindowTitle("Update Available")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        return msgBox.exec_() == QMessageBox.Yes
    

    def promptUserForUpdate(self) -> bool:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Would you like to update now?")
        msgBox.setWindowTitle("Update Available")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        return msgBox.exec_() == QMessageBox.Yes
    
    def warnForRestart(self, delay: int = 15):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(f"Update downloaded. The application will restart in {delay} seconds.")
        msgBox.setWindowTitle("Update Downloaded")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()

    def execUpdateScript(self):
        script_to_exec = getFrozenPath(
            os.path.join("app", "version", "update.py")
        )

        subprocess.Popen(["python", script_to_exec])