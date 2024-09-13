import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QSizePolicy

from app.windows.MessageBox import MessageBox
from app.config.scheduler import Schedule
from app.windows.LoginFrame import SignInFrame
from app.windows.MenuFrame import AccountMenu
from app.windows.TopWidget import Header
from app.windows.BottomWidget import Bottom
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
    downloadFinished = pyqtSignal()
    updateAvailable = pyqtSignal()
    userWantsToDownload = pyqtSignal()
    userWantsToUpdateNow = pyqtSignal()


    new_version = None

    def __init__(self, connection: MongoClient, async_tasks: list[asyncio.Task], parent=None):
        super(MainWindow, self).__init__()
        path = getFrozenPath(os.path.join("assets", "UI", "mainwindow.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection
        self.async_tasks = async_tasks
        
        self.initUI()
        QTimer.singleShot(
            Schedule.NO_DELAY, 
            self.proceedWithUpdate
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

        self.header = Header(connection=self.connection, async_tasks=self.async_tasks, parent=self)
        self.bottom = Bottom(connection=self.connection, async_tasks=self.async_tasks, parent=self)
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
    
    def proceedWithUpdate(self):
        path_to_store_binary = getFileSystemPath(os.path.join("C:", "Program Files", "Gaello X", "updates", "gaello.exe"))
        target_screen_resolution = (1920, 1080)
        self.async_tasks.append(self.checkForUpdate(target_screen_resolution, self.connection))

        # connect updateAvailable & userWantsToDownload signals
        self.updateAvailable.connect(self.promptUserForDownload)
        self.userWantsToDownload.connect(
            lambda: self.async_tasks.append(self.download(path_to_store_binary, self.new_version))
        )

        # connect downloadFinished & userWantsToUpdateNow signals
        self.downloadFinished.connect(self.promptUserForUpdate)
        self.userWantsToUpdateNow.connect(self.makeUpadte)
        
    def makeUpadte(self):
        # if app was closed before timeout
        self.closedBeforeUpdateTimeout.connect(self.execUpdateScript)
        self.warnForRestart()
        self.execUpdateScript()
        sys.exit(0)

    async def download(self, path_to_store_binary: str | Path, version: Version):
        downloader = VersionDownloadManager(path_to_store_binary=path_to_store_binary)
        moveWidget(downloader, parent=self, x="left", y="bottom")
        stackOnCurrentWindow(downloader)
        result = await downloader.download_new_binary(version)
        if result:
            self.downloadFinished.emit()
        return result

    async def checkForUpdate(self, screen_resource: tuple[int, int], connection: MongoClient):
        controller = VersionController()
        result = await controller.check_for_update(screen_resolution=screen_resource, connection=connection)
        if result:
            self.new_version = result
            self.updateAvailable.emit()
        return result

    def promptUserForDownload(self) -> bool:
        msgBox = MessageBox()
        msgBox.level("question")
        msgBox.message("New version available. Would you like to download it?")
        msgBox.title("Update Available")
        msgBox.buttons(("yes", "no"))
        msgBox.setDefaultButton(msgBox.Yes)
        # Connect signals to handle user response
        msgBox.buttonClicked.connect(self.handleUserDownloadChoice)
        msgBox.open()  # This opens the message box without blocking the event loop

    def promptUserForUpdate(self) -> bool:
        msgBox = MessageBox()
        msgBox.level("question")
        msgBox.message("Would you like to update now?")
        msgBox.title("Update Available")
        msgBox.buttons(("yes", "no"))
        msgBox.setDefaultButton(msgBox.Yes)
        # Connect signals to handle user response
        msgBox.buttonClicked.connect(self.handleUserUpdateChoice)
        msgBox.open()  # This opens the message box without blocking the event loop
    
    def handleUserDownloadChoice(self, button):
        # Handle the user's response
        if button.text() == "&Yes":
            self.userWantsToDownload.emit()  # Emit signal if 'Yes' is clicked
            return True
        else:
            # Do something if 'No' is clicked, or handle no download action
            return False
        
    def handleUserUpdateChoice(self, button):
        # Handle the user's response
        if button.text() == "&Yes":
            self.userWantsToUpdateNow.emit()  # Emit signal if 'Yes' is clicked
            return True
        else:
            # Do something if 'No' is clicked, or handle no download action
            return False

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