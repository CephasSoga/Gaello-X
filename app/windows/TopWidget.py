import os

from PyQt5 import uic
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtWidgets import QFrame, QMainWindow

from utils.appHelper import *
from utils.paths import resourcePath
from app.windows.JanineChatFrame import JanineChat
from app.windows.MarketSummaryFrame import MarketSummary
from app.windows.ExploreAssetsFrame import ExploreAsset
from app.windows.ExploreMarketFrame import ExploreMarket

from app.windows.AuthHandler import  handleAuth
from app.windows.WebEngine import DocWebEngineView
from app.windows.LoginFrame import SignInFrame
from app.windows.NotificationsFrame import Notifications
from app.windows.HelpFrame import Help
from app.windows.MenuFrame import Menu
from app.windows.Fonts import *

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class PressChatFrame(QFrame):
    def __init__(self, frame: QFrame, parent=None):
        super().__init__(parent)
        self.frame = frame
        self.janineWindow = None
        self.frame.installEventFilter(self)

    def openChat(self):
        if not self.janineWindow:
            self.janineWindow = JanineChat(self.parent())
            handleAuth(1, stackOnCurrentWindow, self.janineWindow)
        else:
            self.janineWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openChat()
            return True
        return super().eventFilter(obj, event)
        
class PressExploreFrame(QFrame):
    def __init__(self, frame: QFrame, parent=None):
        super().__init__(parent)
        self.frame = frame
        self.summaryWindow = None
        self.frame.installEventFilter(self)
    
    def openExploreArea(self):
        if not self.summaryWindow:
            self.summaryWindow = MarketSummary(self.parent())
            handleAuth(1, stackOnCurrentWindow, self.summaryWindow)
        else:
            self.summaryWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openExploreArea()
            return True
        else:
            return super().eventFilter(obj, event)

class Header(QMainWindow):
    def __init__(self, parent=None):
        super(Header, self).__init__(parent)
        path = os.path.join("UI", "header.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.aboutUsUrl = 'example.com'
        self.demoUrl =  'example.com'

        self.initUI()
        msDelay = 1000
        QTimer.singleShot(msDelay, self.setupMovies)

    def initUI(self):
        self.setFonts()
        self.connectSlots()
        self.installEventFilters()

    def setFonts(self):
        labelFont = RobotoRegular(10) or QFont('Arial', 10)
        titleFont = RobotoBold(11) or QFont('Arial', 11)

        self.exploreForexLabel.setFont(labelFont)
        self.exploreStocksLabel.setFont(labelFont)

        self.exploreForexTitle.setFont(titleFont)
        self.exploreStocksTitle.setFont(titleFont)

        tinyFont = QuicksandBold(9) or QFont('Arial', 9)
        self.chat_p.setFont(tinyFont)
        self.explore_p.setFont(tinyFont)

    def setupMovies(self):
        marketMovie = QMovie(resourcePath(
            os.path.join('rsrc', 'videos', 'marketChart.gif')#r"rsrc/videos/marketChart.gif"
        ))
        self.marketGif.setMovie(marketMovie)
        marketMovie.start()

        stocktMovie = QMovie(resourcePath(
            os.path.join('rsrc', 'videos', 'stockChart.gif')#r"rsrc/videos/stockChart.gif"
        ))
        self.stockGif.setMovie(stocktMovie)
        stocktMovie.start()

    def connectSlots(self):
        self.chatFrame = PressChatFrame(self.chat)
        self.summaryFrame = PressExploreFrame(self.explore)

        assets = ExploreAsset(self)
        assets.hide()
        self.assetButton.clicked.connect(
            lambda: handleAuth(1, stackOnCurrentWindow, assets)
        )

        market = ExploreMarket(self)
        market.hide()
        self.marketButton.clicked.connect(
            lambda: handleAuth(1, stackOnCurrentWindow, market)
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

        self.accountWindow = SignInFrame(self)
        self.account.clicked.connect(
            lambda: showWindow(self.accountWindow)
        )

        self.notificationsWindow = Notifications(self)
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


