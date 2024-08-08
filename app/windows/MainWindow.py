import json
import os
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout

from app.windows.LoginFrame import SignInFrame
from app.windows.TopWidget import Header
from app.windows.BottomWidget import Bottom
from utils.appHelper import stackOnCurrentWindow
from utils.paths import constructPath

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)


class MainWindow(QMainWindow):
    finishedLoading = pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()
        path = os.path.join("UI", "mainwindow.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()

    def initUI(self):
        try:
            self.setWFlags()
            self.setWIcon()
            self.setLayout()
            self.connectSlots()
        finally:
            self.finishedLoading.emit()

    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    def setWIcon(self):
        self.setWindowIcon(QIcon(r"rsrc/logo/cube-log-big.png"))

    def setLayout(self):
        screenGeometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            screenGeometry.x(),
            screenGeometry.y(),
            screenGeometry.width(),
            screenGeometry.height()
        )

        self.scrollArea.setStyleSheet("border-style: none;")
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollWidget)

        w, h = 1900, 1080
        self.header = Header(self)
        self.bottom = Bottom(self)
        self.header.setMinimumSize(w, h)
        self.bottom.setMinimumSize(w, h)

        self.scrollLayout.addWidget(self.header)
        self.scrollLayout.addWidget(self.bottom)

    def closeAndExit(self):
        self.close()
        exit(0)

    def connectSlots(self):
        self.header.minimize.clicked.connect(self.hide)
        self.header.closeApp.clicked.connect(self.closeAndExit)
        self.finishedLoading.connect(self.onLoadingFinished)

    def onLoadingFinished(self):
        baseFolder = Path(os.getenv('APP_BASE_PATH'))
        credentialsPath = constructPath(baseFolder,  r'credentials\credentials.json')
        if not os.path.exists(credentialsPath):
            self.spawnAccountSettings()
        else:
            self.header.account.setEnabled(False)
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
