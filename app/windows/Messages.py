import os
from pathlib import Path

from PyQt5 import uic, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QFrame, QVBoxLayout,QSlider, QLabel, QSizePolicy, QWidget

from app.windows.Types import *
from utils.time import time_, date
from utils.paths import getFrozenPath
from app.windows.Styles import userMessageBackground, chatScrollBarStyle
from app.windows.Fonts import RobotoRegular, Exo2Light

class ChatTextMessage(QFrame):
    def __init__(self, message:Message, parent=None):
        super(ChatTextMessage, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "text_message.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        self.content = message.content
        if isinstance(self.content, TextMessage):
            self.textMessage = self.content.text
        else:
            raise TypeError("Message must be a TextMessage")
        self.origin = self.content.origin

        self.initUI()

    def initUI(self):
        self.setupLayout()
        self.setContents()
        self.setFonts()

    def setupLayout(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(1)

        self.text.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if self.origin == "User":
            self.setStyleSheet(userMessageBackground)


    def setContents(self):
        self.originLabel.setText(f"{self.origin}")
        self.text.setPlainText(f"{self.textMessage}")
        self.date.setText(f"{self.content.date}")
        self.time.setText(f"{self.content.time}")

        self.text.setReadOnly(True)

        self.updateMinimumHeight()

    def setFontOnObjects(self, font, objects:list):
        for obj in objects:
            obj.setFont(font)

    def setFonts(self):
        regularFont = RobotoRegular(10) or QFont("Arial", 10)
        tinyFont = Exo2Light(8) or QFont("Arial", 8)
        self.setFontOnObjects(regularFont, [self.text])
        self.setFontOnObjects(tinyFont, [self.originLabel, self.date, self.time])

    def getTextSize(self):
        fontMetrics = QtGui.QFontMetrics(self.text.font())
        w = fontMetrics.width(self.text.toPlainText())
        h = fontMetrics.height() * (self.text.document().lineCount())
        return w, h


    def updateMinimumHeight(self):
        _, minh = self.getTextSize()
        margin = 100 # Adjust this value based on your layout and padding requirements
        minh = minh + margin
        self.text.setFixedHeight(minh)
        self.setFixedHeight(minh + margin)


class ChatVoiceMail(QFrame):
    def __init__(self, message:Message, parent=None):
        super(ChatVoiceMail, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "voicemail.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        self.content = message.content
        if isinstance(self.content, VoiceMail):
            self.filePath = self.content.filePath
        else:
            raise TypeError("Message must be a VoiceMail")
        self.origin = self.content.origin

        self.initUI()

    def initUI(self):
        self.setContents()
        self.setupLayout()
        self.connectSlots()
        self.setFonts()

    def setContents(self):
        self.videoWidget = QVideoWidget()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.setPosition)

        self.originLabel.setText(f"{self.origin}")
        self.date.setText(f"Date: {date()}")
        self.time.setText(f"Time: {time_()}")

        self.loadAudio(self.filePath)

    def setFontOnObjects(self, font, objects:list):
        for obj in objects:
            obj.setFont(font)

    def setFonts(self):
        tinyFont = Exo2Light(8) or QFont("Arial", 8)
        self.setFontOnObjects(tinyFont, [self.originLabel, self.date, self.time])
    
    def setupLayout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.slider)
        self.infoWrapper.setLayout(self.layout)

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(1)

        if self.origin == "User":
            self.setStyleSheet(userMessageBackground)

    def connectSlots(self):
        self.play.clicked.connect(
            self.playAudio
        )
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def loadAudio(self, filePath:Path):
        filePath = str(filePath)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))
        self.videoWidget.show()
        self.play.setEnabled(True)
        self.slider.setEnabled(True)
        self.originLabel.setText(f"{self.origin}")
        self.date.setText(f"Date: {date()}")
        self.time.setText(f"Time: {time_()}")

    def  playAudio(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        side = 64
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            iconPath = getFrozenPath(os.path.join("assets",  "icons", "pause-button.png"))
            icon = QtGui.QIcon(iconPath)
            self.play.setIcon(icon)
            self.play.setIconSize(QSize(side, side))
        else:
            iconPath = getFrozenPath(os.path.join("assets",  "icons", "play-button.png"))
            icon = QtGui.QIcon(iconPath)
            self.play.setIcon(icon)
            self.play.setIconSize(QSize(side, side))

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)
        self.updateDurationLabel(duration)

    def updateDurationLabel(self, duration):
        seconds = (duration / 1000) % 60
        minutes = (duration / (1000 * 60)) % 60
        hours = (duration / (1000 * 60 * 60)) % 24

        if hours > 0:
            self.length.setText(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        else:
            self.length.setText(f"{int(minutes):02}:{int(seconds):02}")


    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.play.setEnabled(False)
        self.slider.setEnabled(False)


class ChatMultimedia(QWidget):
    def __init__(self, message: Message, parent=None) -> None:
        super(ChatMultimedia, self).__init__(parent)

        self.content = message.content
        if isinstance(self.content, Multimedia):
            self.filePath = self.content.filePath
            self.text = self.content.text
        else:
            raise TypeError("ChatMultimedia requires a Multimedia instance")
        self.origin = self.content.origin

        path = getFrozenPath(os.path.join("assets", "UI", "multimedia_.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()
        
    def initUI(self):
        self.setContents()
        self.setupLayout()
        self.connectSlots()
        self.setFonts()

    def setupLayout(self):
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.videoWidget)
        self.layout.addWidget(self.imageLabel)
        self.layout.addWidget(self.slider)

        self.read.setLayout(self.layout)

        if self.origin == "User":
            self.setStyleSheet(userMessageBackground)

    def setFontOnObjects(self, font, objects:list):
        for obj in objects:
            obj.setFont(font)

    def setFonts(self):
        regularFont = RobotoRegular(10) or QFont("Arial", 10)
        tinyFont = Exo2Light(8) or QFont("Arial", 8)
        self.setFontOnObjects(regularFont, [self.textLabel])
        self.setFontOnObjects(tinyFont, [self.label, self.date, self.time])



    def setContents(self):
        self.videoWidget = QVideoWidget()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.play.setEnabled(False)
        self.play.clicked.connect(self.playMedia)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.setPosition)

        self.loadMedia(self.filePath)

    def connectSlots(self):
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def loadMedia(self, filePath):
        filePath = str(filePath)
        mimeType, _ = mimetypes.guess_type(filePath)
        if mimeType:
            if mimeType.startswith('image'):
                self.showImage(filePath)
            elif mimeType.startswith('video'):
                self.loadVideo(filePath)
            elif mimeType.startswith('audio'):
                self.loadAudio(filePath)

    def showImage(self, filePath):
        pixmap = QtGui.QPixmap(filePath)
        self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.imageLabel.show()
        self.videoWidget.hide()
        self.mediaPlayer.stop()
        self.play.setEnabled(False)
        self.play.hide()
        self.slider.setEnabled(False)
        self.slider.hide()
        self.textLabel.setText(self.text)
        self.label.setText(f"{self.origin}: {self.filePath}")
        self.date.setText(f"Date: {date()}")
        self.time.setText(f"Time: {time_()}")

    def loadVideo(self, filePath):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))
        self.videoWidget.show()
        self.imageLabel.hide()
        self.play.setEnabled(True)
        self.slider.setEnabled(True)
        self.textLabel.setText(self.text)
        self.label.setText(f"{self.origin}: {self.filePath}")
        self.date.setText(f"Date: {date()}")
        self.time.setText(f"Time: {time_()}")

    def loadAudio(self, filePath):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))
        self.imageLabel.hide()
        self.videoWidget.hide()
        self.play.setEnabled(True)
        self.slider.setEnabled(True)
        self.textLabel.setText(self.text)
        self.label.setText(f"{self.origin}: {self.filePath}")
        self.date.setText(f"Date: {date()}")
        self.time.setText(f"Time: {time_()}")

    def playMedia(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        side = 64
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            iconPath = getFrozenPath(os.path.join("assets",  "icons", "pause.png"))
            icon = QtGui.QIcon(iconPath)
            self.play.setIcon(icon)
            self.play.setIconSize(QSize(side, side))
        else:
            iconPath = getFrozenPath(os.path.join("assets",  "icons", "play2.png"))
            icon = QtGui.QIcon(r"icons/play2.png")
            self.play.setIcon(icon)
            self.play.setIconSize(QSize(side, side))

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)
        self.updateDurationLabel(duration)

    def updateDurationLabel(self, duration):
        seconds = (duration / 1000) % 60
        minutes = (duration / (1000 * 60)) % 60
        hours = (duration / (1000 * 60 * 60)) % 24

        if hours > 0:
            self.length.setText(f"Length: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        else:
            self.length.setText(f"Length: {int(minutes):02}:{int(seconds):02}")

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.play.setEnabled(False)
        self.slider.setEnabled(False)
        self.imageLabel.setText("Error: " + self.mediaPlayer.errorString())

    
