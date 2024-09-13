import os
import asyncio

from pymongo.mongo_client import MongoClient

from PyQt5  import uic
from PyQt5.QtCore import Qt, QUrl, QEvent, QTimer
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QSizePolicy, QFrame

from app.handlers.AuthHandler import  handleAuth
from utils.appHelper import *
from utils.paths import resourcePath
from app.config.fonts import RobotoRegular, FontSizePoint
from app.windows.InsightsWidget import JanineInsights
from app.windows.CommunityWidget import JanineCommunity
from app.windows.PlusWidget import ProjectHome
from utils.paths import getFrozenPath
from app.config.renderer import ViewController

# ffmpeg binaries at assets\binaries\w64\ffmpeg\bin
ffmpeg_path = resourcePath(os.path.join('assets', 'binaries', 'w64', 'ffmpeg', 'bin'))
os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']

class PressInsigthsFrame(QFrame):
    def __init__(self, connection: MongoClient, widget: QWidget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.insightsWindow = None
        self.connection = connection
        self.widget.installEventFilter(self)

    def openInsights(self):
        if not self.insightsWindow:
            self.insightsWindow = JanineInsights(connection=self.connection, parent=self.parent())
            asyncio.ensure_future(handleAuth(self.connection, 2, stackOnCurrentWindow, self.insightsWindow))
        else:
            self.insightsWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openInsights()
            return True
        else:
            return super().eventFilter(obj, event)
        
class PressCommunityFrame(QFrame):
    def __init__(self, connection: MongoClient, widget: QWidget, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.widget = widget
        self.communityWindow = None
        self.widget.installEventFilter(self)

    def openCommunity(self):
        if not self.communityWindow:
            self.communityWindow = JanineCommunity(self.parent())
            asyncio.ensure_future(handleAuth(self.connection, 1, stackOnCurrentWindow, self.communityWindow))
        else:
            self.communityWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openCommunity()
            return True
        else:
            return super().eventFilter(obj, event)
        
class PressPlusFrame(QFrame):
    def __init__(self, widget: QWidget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.communityWindow = None
        self.widget.installEventFilter(self)

    def openCommunity(self):   
        if not self.communityWindow:
            self.communityWindow = ProjectHome(self.parent())
            stackOnCurrentWindow(self.communityWindow)
        else:
            self.communityWindow = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.openCommunity()
            return True
        else:
            return super().eventFilter(obj, event)

class Bottom(QMainWindow):
    def __init__(self, connection: MongoClient, async_tasks: list, parent=None):
        super(Bottom, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "bottom.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection
        self.async_tasks = async_tasks
        self.exploreProjectUrl = 'https://www.cube.ai'
        self.kickstartUrl = 'https://www.gaello.io/docs'

        self.initUI()
        msDelay = 2000
        QTimer.singleShot(msDelay, self.setupMovies)
        
    def initUI(self):
        adjustForDPI(self)
        self.setFonts()
        self.setWFlags()
        self.connectSlots()
        self.installEventFilters()

    def setFonts(self):
        size = FontSizePoint
        font = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        self.exploreProject.setFont(font)
        self.kickstart.setFont(font)
        self.insights.setFont(font)
        self.insightLabel.setFont(font)
        self.communityLabel.setFont(font)
        self.plusLabel.setFont(font)


    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    def createMediaPlayer(self, path, widget: QWidget):
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(*ViewController.SCROLL_NO_MARGINS)

        videoWidget = QVideoWidget(widget)
        videoWidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        videoWidget.setAspectRatioMode(Qt.KeepAspectRatio)      
        layout.addWidget(videoWidget)

        mediaPlayer = QMediaPlayer(widget, QMediaPlayer.VideoSurface)
        mediaPlayer.setVideoOutput(videoWidget)

        mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))

        mediaPlayer.mediaStatusChanged.connect(lambda status: self.handleMediaStatusChanged(status, mediaPlayer))

        widget.setLayout(layout)

        mediaPlayer.play()

    def handleMediaStatusChanged(self, status, mediaPlayer):
        if status == QMediaPlayer.EndOfMedia:
            mediaPlayer.setPosition(0)
            mediaPlayer.play()

    def setupMovies(self):
        insigthMoviePath = resourcePath(
            os.path.join("assets", "videos", "chipset.mp4") #os.path.join("rsrc", "videos", "chipset.mp4")
        )
        self.createMediaPlayer(insigthMoviePath, self.insightsWidget)

        communityMoviePath = resourcePath(
            os.path.join("assets", "videos", "network.mp4") #os.path.join("rsrc", "videos", "network.mp4")#r"rsrc/videos/network.mp4"
        )
        self.createMediaPlayer(communityMoviePath, self.communityWidget)

        plusMoviePath = resourcePath(
            os.path.join("assets", "videos", "bwwave.mp4")#os.path.join("rsrc", "videos", "bwwave.mp4")#r"rsrc/videos/bwwave.mp4"
        )
        self.createMediaPlayer(plusMoviePath, self.plusWidget)

    def connectSlots(self):
        self.insightsFrame_ = PressInsigthsFrame(connection=self.connection, widget=self.insightsFrame)
        self.communityFrame_ = PressCommunityFrame(connection=self.connection, widget=self.communityFrame)
        self.plusFrame_ = PressPlusFrame(self.plusFrame)

        self.exploreProject.clicked.connect(lambda: browse(self.exploreProjectUrl))
        self.kickstart.clicked.connect(lambda: browse(self.kickstartUrl))
        self.insights.clicked.connect(self.insightsFrame_.openInsights)

    def installEventFilters(self):
        self.installEventFilter(self.insightsFrame_)
        self.installEventFilter(self.communityFrame_)
        self.installEventFilter(self.plusFrame_)

