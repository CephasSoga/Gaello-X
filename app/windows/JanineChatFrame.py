import os
import glob
import asyncio
from pathlib import Path
from typing import Union

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent, pyqtSlot
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from qasync import asyncSlot, QApplication, QEventLoop

import app.rsrc.images.backgrounds
from app.windows.Messages import *
from app.windows.Types import Recorder
from app.windows.Styles import scrollBarStyle
from utils.paths import latestTargetFilesWithPolling
from models.api.requests import RequestManager
from models.janine.JanineModel import janineInstance
from databases.mongodb.JanineDB import janineDB
from utils.fileHelper import getAudioLength
from utils.envHandler import getenv
from utils.paths import rawPathStr
from app.windows.WaiterFrame import Waiter

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class JanineChat(QFrame):
    def __init__(self, parent=None):
        super(JanineChat, self).__init__(parent)
        path = os.path.join(r"UI/chat_.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.waiter = Waiter()

        self.initUI()

    def initUI(self):
        self.setContents()
        self.setWFlags()
        self.setupLayout()
        self.setButtonDescriptions()
        self.connectSlots()
        self.setFonts()

    def setContents(self):
        self.requestManager = RequestManager()
        self.db = janineDB
        self.recorder = Recorder()

        self.janine = janineInstance

        self.chatMessages: list[Message] = []
        self.lastMessageIndex = -1

        self.outputFile = None
        self.isRecording = False
        self.fileLoaded = False
        self.loadedFilePath = ""

        self.chatWidget = QWidget()
        self.historyWidget = QWidget()
        self.messageBox = QMessageBox()

        self.basePath = getenv("APP_BASE_PATH")

    def setFontOnObjects(self, font, objects:list):
        for obj in objects:
            obj.setFont(font)

    def setFonts(self):
        regularFontFam = loadFont(r"rsrc/fonts/Montserrat/static/Montserrat-Regular.ttf")
        if regularFontFam:
            regularFont = QFont(regularFontFam, 10)
        else:
            regularFont = QFont("Arial", 10)

        discreteFontFam = loadFont(r"rsrc/fonts/Exo_2/static/Exo2-Light.ttf")
        if discreteFontFam:
            discreteFont = QFont(discreteFontFam, 9)
        else:
            discreteFont = QFont("Arial", 9)

        self.setFontOnObjects(regularFont, [self.newChat, self.message, self.caution])
        self.setFontOnObjects(discreteFont, [self.caution])

    def setWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

    def setupLayout(self):
        self.message.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.chatLayout = QVBoxLayout()
        self.chatLayout.setSpacing(10)
        self.chatLayout.setContentsMargins(10, 10, 10, 10)
        self.chatLayout.setAlignment(Qt.AlignTop)
        self.chatWidget.setLayout(self.chatLayout)
        self.chatScrollArea.verticalScrollBar().setStyleSheet(scrollBarStyle)  
        self.chatScrollArea.setWidgetResizable(True)
        self.chatScrollArea.setWidget(self.chatWidget)
        # Get the vertical scrollbar and set its value to maximum
        scrollBar = self.chatScrollArea.verticalScrollBar()
        scrollBar.setValue(scrollBar.maximum())

        self.historyLayout = QVBoxLayout()
        self.historyLayout.setSpacing(10)
        self.historyLayout.setContentsMargins(10, 10, 10, 10)
        self.historyLayout.setAlignment(Qt.AlignTop)
        self.historyWidget.setLayout(self.historyLayout)
        self.historyScrollArea.verticalScrollBar().setStyleSheet(scrollBarStyle)
        self.historyScrollArea.setWidgetResizable(True)
        self.historyScrollArea.setWidget(self.historyWidget)

        self.waiterWidget = None

    def setButtonDescriptions(self):
        self.newChat.setToolTip("Start a new chat With Janine")
        self.send.setToolTip("Click to send message")
        self.voicemail.setToolTip("Click to toggle recording")
        self.attach.setToolTip("Attach file to chat")

    def connectSlots(self):
        self.recorder.recorded.connect(self.whileRecording)
        self.recorder.progress.connect(self.timer)
        self.close_.clicked.connect(lambda: self.close())
        self.voicemail.clicked.connect(self.constructVoiceMail)
        self.attach.clicked.connect(self.loadMedia)
        self.send.clicked.connect(self.constructMessage)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def alignByOrigin(self, msg: Union[ChatTextMessage, ChatVoiceMail, ChatMultimedia], origin: str):
        hLayout = QHBoxLayout()
        if origin == "User":
            hLayout.addStretch()
            hLayout.addWidget(msg)
        else:
            hLayout.addWidget(msg)
            hLayout.addStretch()
        self.chatLayout.addLayout(hLayout)
        self.chatWidget.update()

    def display(self):
        for idx, message in enumerate(self.chatMessages):
            if idx > self.lastMessageIndex:
                if isinstance(message.content, TextMessage):
                    msg = ChatTextMessage(message, self)
                    self.alignByOrigin(msg, msg.origin)
                
                elif isinstance(message.content, VoiceMail):
                    msg = ChatVoiceMail(message, self)                   
                    self.alignByOrigin(msg, msg.origin)

                elif isinstance(message.content, Multimedia):
                    msg  = ChatMultimedia(message, self)
                    self.alignByOrigin(msg, msg.origin)

        self.lastMessageIndex = len(self.chatMessages) - 1

    def push(self, item: TextMessage|VoiceMail|Multimedia):
        message = Message(item)
        self.chatMessages.append(message)
        self.display()

    def loadMedia(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Media File",
              "", 
              "Images (*.png *.jpg);;Videos (*.mp4 *.avi);;Audio (*.mp3 *.wav)", 
              options=options
        )
        if filePath:
            self.loadedFilePath = filePath
            self.fileLoaded = True
            self.message.setText(f"Attached file: {self.loadedFilePath}\n")
        else:
            pass

    async def attachFileFunc(self, origin:str="User"):
        text = "\n".join(self.message.toPlainText().split("\n")[1:])
        tempPath = Path(self.loadedFilePath)
        multimedia = Multimedia(tempPath, text, origin=origin)
        multimediaStr = await multimedia.toString()
        await self.requestManager.post(message=multimediaStr)
        self.db.insert(item=multimediaStr)
        self.push(multimedia)    

    @asyncSlot()
    async def attachMultimediaFile(self):
        await self.attachFileFunc()
        await self.completeMutimediaMessage()
        self.resetMessageField()

    asyncSlot()
    async def completeMutimediaMessage(self):
        await self.spawnWaiter()
        response = await self.janine.remoteCompleteMessage()
        if isinstance(response, Path):
            await self.voiceMailFunc(response, origin="Janine")
        else:
            await self.textMessageFunc(message=response, origin="Janine")
        self.removeWaiter()
        self.resetMessageField()

    def resetMessageField(self):
        self.fileLoaded = False
        self.loadedFilePath = ""
        self.message.clear()

    async def textMessageFunc(self, message:str=None, origin:str="User"):
        if message:
            text = message
        else: 
            text = self.message.toPlainText()
            if len(text) == 0:
                self.messageBox.information(
                    self, "Invalid Text Message", "No message input found.",
                )
                return
        message = TextMessage(text,  origin=origin)
        messageStr = message.toString()
        await self.requestManager.post(message=messageStr)
        self.db.insert(item=messageStr)
        self.push(message)


    @asyncSlot()
    async def textMessage(self):
        await self.textMessageFunc()
        await self.completeTextMessage()
        self.resetMessageField()

    @asyncSlot()
    async def completeTextMessage(self):
        await self.spawnWaiter()
        response = await self.janine.remoteCompleteMessage()
        self.removeWaiter()
        await self.textMessageFunc(message=response, origin="Janine")
        
    async def constructMessageFunc(self):
        if self.fileLoaded:
            await self.attachMultimediaFile()

        else:
            await self.textMessage()

    @pyqtSlot(float)
    def timer(self, elapsed_time):
        # Update the progress bar with the elapsed time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.timerLabel.setText(f"{minutes:02}:{seconds:02}")

    def whileRecording(self):
        self.timerLabel.setText("00:00")

    async def voiceMailFunc(self, path: Path, origin:str="User"):
        duration = getAudioLength(path)
        if duration == 0:
            self.messageBox.information(
                self, "Invalid Voice Message", "No voice input found.",
            )
            return
        voicemail = VoiceMail(path, origin=origin)
        voicemailStr = await voicemail.toString()
        await self.requestManager.post(message=voicemailStr)
        self.db.insert(item=voicemailStr)
        self.push(voicemail)

    @asyncSlot()
    async def constructVoiceMailFunc(self):
        if  not self.isRecording:
            self.recorder.start()
        else:
            self.whileRecording()
            self.recorder.stop()
            basePath = Path(rawPathStr(self.basePath))
            targetDir = basePath / 'static/exchanges'
            pattern = str(targetDir / '*.wav')
            wavFiles = glob.glob(pattern)
            if wavFiles:
                latestWavFile = latestTargetFilesWithPolling(pattern=pattern)
                latestWavFile = Path(latestWavFile)
                await self.voiceMailFunc(latestWavFile)
                await self.completeVoiceMail()

        self.isRecording = not self.isRecording

    @asyncSlot()
    async def completeVoiceMail(self):
        await self.spawnWaiter()
        response = await self.janine.remoteCompleteMessage()
        self.removeWaiter()
        await self.voiceMailFunc(response, origin="Janine")

    def constructMessage(self):
        asyncio.ensure_future(self.constructMessageFunc())

    def constructVoiceMail(self):
        asyncio.ensure_future(self.constructVoiceMailFunc())


    async def spawnWaiter(self):
        if not self.waiterWidget:
            self.waiterWidget = QWidget()
            self.waiterlayout = QHBoxLayout()
            self.waiterWidget.setLayout(self.waiterlayout)
        self.waiterlayout.addStretch()
        self.waiterlayout.addWidget(self.waiter)
        self.waiterWidget.update()
        self.waiterWidget.show()
        self.chatLayout.addWidget(self.waiterWidget)
        self.chatWidget.update()
        await asyncio.sleep(2) # let Waiter show properly

    def removeWaiter(self):
        self.chatLayout.removeWidget(self.waiterWidget)
        self.waiterWidget.hide()
        self.chatWidget.update()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = JanineChat()
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()




    



