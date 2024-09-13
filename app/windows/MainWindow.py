import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QSizePolicy

from app.windows.MessageBox import MessageBox
from app.config.scheduler import Schedule
from app.windows.LoginFrame import SignInFrame
from app.windows.MenuFrame import AccountMenu
from app.windows.TopWidget import Header
from app.windows.BottomWidget import Bottom
from app.windows.Styles import msgBoxStyleSheet
from utils.appHelper import stackOnCurrentWindow, setRelativeToMainWindow, isFrozen, adjustForDPI, moveWidget
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
        QTimer.singleShot(
            Schedule.DEFAULT_DELAY, 
            lambda: asyncio.ensure_future(self.proceedWithUpdate())
        )

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
    
    @pyqtSlot()
    async def proceedWithUpdate(self):
        path_to_store_binary = getFileSystemPath(os.path.join("C:", "Program Files", "Gaello X", "updates", "gaello.exe"))
        target_screen_resolution = (1920, 1080)
        new_version_available = await self.checkForUpdate(target_screen_resolution, self.connection)
        if not new_version_available:
            return
        
        permission = self.promptUserForDownload()
        if not permission:
            return

        download = await self.download(path_to_store_binary, new_version_available)
        if not download:
            return

        user_wants_to_update_now = self.promptUserForUpdate()
        if not user_wants_to_update_now:
            return

        # if app was closed before timeout
        self.closedBeforeUpdateTimeout.connect(self.execUpdateScript)
        self.warnForRestart()
        self.execUpdateScript()
        sys.exit(0)

    async def download(self, path_to_store_binary: str | Path, version: Version):
        downloader = VersionDownloadManager(path_to_store_binary=path_to_store_binary)
        moveWidget(downloader, parent=self, x="left", y="bottom")
        stackOnCurrentWindow(downloader)
        return await downloader.download_new_binary(version)

    async def checkForUpdate(self, screen_resource: tuple[int, int], connection: MongoClient):
        controller = VersionController()
        return await controller.check_for_update(screen_resolution=screen_resource, connection=connection)
    
    def promptUserForDownload(self) -> bool:
        msgBox = MessageBox()
        msgBox.level("question")
        msgBox.message("New version available. Would you like to download it?")
        msgBox.title("Update Available")
        msgBox.buttons(("yes", "no"))
        msgBox.setDefaultButton(msgBox.Yes)
        return msgBox.exec_() == msgBox.Yes
    

    def promptUserForUpdate(self) -> bool:
        msgBox = MessageBox()
        msgBox.level("question")
        msgBox.message("Would you like to update now?")
        msgBox.title("Update Available")
        msgBox.buttons(("yes", "no"))
        msgBox.setDefaultButton(msgBox.Yes)
        return msgBox.exec_() == msgBox.Yes
    
    def warnForRestart(self):
        msgBox = MessageBox()
        msgBox.level("warning")
        msgBox.message("Application will restart now for the update to take effect.")
        msgBox.title("Update Downloaded")
        msgBox.buttons(("ok", ))
        msgBox.setDefaultButton(msgBox.Ok)
        self.closedBeforeUpdateTimeout.emit()
        msgBox.exec_()

    def execUpdateScript(self):
        script_to_exec = getFrozenPath(
            os.path.join("app", "version", "update.py")
        )
        try:
            subprocess.Popen(["python", script_to_exec])
        except OSError as oe:
            raise RuntimeError(f"An OS Error prevented the update script to execute properly: {oe}.")
        except Exception as e:
            raise