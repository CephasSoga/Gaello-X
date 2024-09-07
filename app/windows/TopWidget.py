import os
import asyncio

from PyQt5 import uic
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtWidgets import QFrame, QMainWindow

from pymongo.mongo_client import MongoClient

from utils.appHelper import *
from utils.paths import resourcePath
from app.windows.JanineChatFrame import JanineChat
from app.windows.MarketSummaryFrame import MarketSummary
from app.windows.ExploreAssetsFrame import ExploreAsset
from app.windows.ExploreMarketFrame import ExploreMarket

from app.handlers.AuthHandler import  handleAuth
from app.windows.WebEngine import DocWebEngineView
from app.windows.LoginFrame import SignInFrame
from app.windows.NotificationsFrame import Notifications
from app.windows.HelpFrame import Help
from app.windows.MenuFrame import Menu
from app.config.fonts import QuicksandBold, RobotoBold, RobotoRegular, FontSizePoint
from utils.paths import getFrozenPath

class PressChatFrame(QFrame):
    def __init__(self, connection: MongoClient, frame: QFrame, parent=None):
        super().__init__(parent)
        self.frame = frame
        self.janineWindow = None
        self.connection = connection
        self.frame.installEventFilter(self)

    def openChat(self):
        if not self.janineWindow:
            self.janineWindow = JanineChat(connection=self.connection, parent=self.parent())
            asyncio.ensure_future(handleAuth(self.connection, 1, stackOnCurrentWindow, self.janineWindow))
        else:
            self.janineWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openChat()
            return True
        return super().eventFilter(obj, event)
        
class PressExploreFrame(QFrame):
    def __init__(self, connection: MongoClient, frame: QFrame, parent=None):
        super().__init__(parent)
        self.frame = frame
        self.summaryWindow = None
        self.connection = connection
        self.frame.installEventFilter(self)
    
    def openExploreArea(self):
        if not self.summaryWindow:
            self.summaryWindow = MarketSummary(connection=self.connection, parent=self.parent())
            asyncio.ensure_future(handleAuth(self.connection, 1, stackOnCurrentWindow, self.summaryWindow))
        else:
            self.summaryWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openExploreArea()
            return True
        else:
            return super().eventFilter(obj, event)

class Header(QMainWindow):
    def __init__(self, connection: MongoClient, parent=None):
        super(Header, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "header.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection

        self.aboutUsUrl = 'example.com'
        self.demoUrl =  'example.com'

        self.initUI()
        msDelay = 1000
        QTimer.singleShot(msDelay, self.setupMovies)

    def initUI(self):
        adjustForDPI(self)
        self.setFonts()
        self.connectSlots()
        self.installEventFilters()

    def setFonts(self):
        size = FontSizePoint
        labelFont = RobotoRegular(size.MEDIUM) or QFont('Arial', size.MEDIUM)
        titleFont = RobotoBold(size.BIG) or QFont('Arial', size.BIG)

        self.exploreForexLabel.setFont(labelFont)
        self.exploreStocksLabel.setFont(labelFont)

        self.exploreForexTitle.setFont(titleFont)
        self.exploreStocksTitle.setFont(titleFont)

        tinyFont = QuicksandBold(size.TINY) or QFont('Arial', size.TINY)
        self.chat_p.setFont(tinyFont)
        self.explore_p.setFont(tinyFont)

    def setupMovies(self):
        marketMovie = QMovie(resourcePath(
            os.path.join("assets", 'videos', 'marketChart.gif')#r"rsrc/videos/marketChart.gif"
        ))
        self.marketGif.setMovie(marketMovie)
        marketMovie.start()

        stocktMovie = QMovie(resourcePath(
            os.path.join("assets", 'videos', 'stockChart.gif')#r"rsrc/videos/stockChart.gif"
        ))
        self.stockGif.setMovie(stocktMovie)
        stocktMovie.start()

    def connectSlots(self):
        self.chatFrame = PressChatFrame(connection=self.connection, frame=self.chat)
        self.summaryFrame = PressExploreFrame(connection=self.connection, frame=self.explore)

        assets = ExploreAsset(connection=self.connection, parent=self)
        assets.hide()
        self.assetButton.clicked.connect(
            lambda: asyncio.ensure_future(handleAuth(self.connection, 1, stackOnCurrentWindow, assets))
        )

        market = ExploreMarket(connection=self.connection, parent=self)
        market.hide()
        self.marketButton.clicked.connect(
            lambda: asyncio.ensure_future(handleAuth(self.connection, 1, stackOnCurrentWindow, market))
        )

        self.docWebEngineView = DocWebEngineView()
        self.docs.clicked.connect(
            lambda: showWindow(self.docWebEngineView.web)
        )

        self.aboutUs.clicked.connect(
            lambda: browse(self.aboutUsUrl)
        )

        self.demo.clicked.connect(
            lambda: browse(self.demoUrl)
        )

        self.accountWindow = SignInFrame(connection=self.connection, parent=self)
        self.account.clicked.connect(
            lambda: showWindow(self.accountWindow)
        )

        self.notificationsWindow = Notifications(connection=self.connection, parent=self)
        setRelativeToMainWindow(self.notificationsWindow, self)
        self.notificationsWindow.hide()
        self.notifications.clicked.connect(
            lambda: stackOnCurrentWindow(self.notificationsWindow)
        )

        self.helpWindow = Help(self)
        setRelativeToMainWindow(self.helpWindow, self)
        self.helpWindow.hide()
        self.help.clicked.connect(
            lambda: stackOnCurrentWindow(self.helpWindow)
        )

        self.menuWindow = Menu(self)
        setRelativeToMainWindow(self.menuWindow, self)
        self.menuWindow.hide()
        self.menu.clicked.connect(
            lambda: stackOnCurrentWindow(self.menuWindow)
        )

    def openInBrowser(self, url):
        browse(url)

    def installEventFilters(self):
        self.installEventFilter(self.notificationsWindow)
        self.installEventFilter(self.helpWindow)
        self.installEventFilter(self.menuWindow)


