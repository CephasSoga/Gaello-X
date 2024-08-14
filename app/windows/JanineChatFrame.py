import os
import glob
import asyncio
from pathlib import Path
from typing import List, Union

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent, pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from qasync import asyncSlot, QApplication, QEventLoop

from app.windows.Spinner import Spinner, Worker
from app.windows.Messages import *
from app.windows.Types import Recorder
from app.windows.Styles import scrollBarStyle
from utils.paths import latestTargetFilesWithPolling
from models.api.requests import RequestManager
from models.janine.JanineModel import Janine
from databases.mongodb.JanineDB import JanineMongoDatabase
from utils.fileHelper import getAudioLength
from utils.envHandler import getenv
from utils.paths import rawPathStr, getFrozenPath, getFileSystemPath
from app.windows.Fonts import  QuicksandBold, Exo2Medium
from app.windows.WaiterFrame import Waiter
from app.windows.ChatTitleFrame import ChatTitleSelector, ChatTitle
from utils.appHelper import setRelativeToMainWindow,clearLayout
from utils.time import now

HISTORY_LIMIT = 100

class JanineChat(QFrame):
    gatheredChats = pyqtSignal(list)
    def __init__(self, parent=None):
        super(JanineChat, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "chat_.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.waiter = Waiter()

        self.initUI()
        #QTimer.singleShot(10, self.topLevelHistoryRendering)

    def initUI(self):
        import time

        s = time.perf_counter()
        self.setContents()
        self.setWFlags()
        self.setupLayout()
        self.setButtonDescriptions()
        self.connectSlots()
        self.setFonts()
        self.runAsyncforHistory()
        e = time.perf_counter()
        print(f"UI init took: {e - s:.2f} seconds")

    def setContents(self):
        self.chatMessages: list[Message] = []
        self.lastMessageIndex = -1
        self.requestManager = RequestManager()

        self.db = JanineMongoDatabase()
        self.recorder = Recorder()
        self.janine = Janine(self.db)

        self.outputFile = None
        self.isRecording = False
        self.fileLoaded = False
        self.loadedFilePath = ""

        self.chatWidget = QWidget()
        self.historyWidget = QWidget()
        self.messageBox = QMessageBox()

        self.basePath = getFileSystemPath(getenv("APP_BASE_PATH"))

    def setFontOnObjects(self, font, objects:list):
        for obj in objects:
            obj.setFont(font)

    def setFonts(self):
        regularFont = QuicksandBold(10) or QFont("Arial", 10)
        discreteFont = Exo2Medium(9) or QFont("Arial", 9)
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

        self.newChat.clicked.connect(self.startNewChat)

        self.gatheredChats.connect(self.topLevelHistoryRendering)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def alignByOrigin(self, msg: Union[ChatTextMessage, ChatVoiceMail, ChatMultimedia], origin: str):
        self.hLayout = QHBoxLayout()
        if origin == "User":
            self.hLayout.addStretch()
            self.hLayout.addWidget(msg)
        else:
            self.hLayout.addWidget(msg)
            self.hLayout.addStretch()
        self.chatLayout.addLayout(self.hLayout)
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
        multimedia = Multimedia(model=self.janine, filePath=tempPath, text=text, origin=origin)
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
        voicemail = VoiceMail(model=self.janine, path=path, origin=origin)
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

    def startNewChat(self):
        clearLayout(self.chatLayout)
        selector = ChatTitleSelector(self)
        selector.titleSet.connect(self.newChatTitleSelected)
        setRelativeToMainWindow(selector, self, 'center')

    def newChatTitleSelected(self, title: str):
        if title:
            chatTitle = ChatTitle(title=title, func=self.showFullChat, parent=self)
            chatTitle.setStyleSheet(
                "background-color: rgba(10, 10, 10, 200);"
            )
            self.historyLayout.addWidget(chatTitle)
            self.historyWidget.setLayout(self.historyLayout)
            self.historyScrollArea.setWidget(self.historyWidget)
            self.installEventFilter(chatTitle)
        
            #mongoUpdate(database=self.db.user, collection='chatHistory', update={'$set': {'chat': {'title': title, 'time': now()}}})
            self.db.createChat(title=title)
            print("title: ",self.db.title)
            try:
                self.db.database['metadata'].insert_one({'chat': {'createdAt': now(), 'title': title}}) #  insert a metadata record to properly sort collections 
            except Exception: # if it fails because the database has not be initialized yet
                self.logger.log("error", "error inserting metadata record", ValueError("No connection to Janine database found."))
                print('unsed con.')
                self.db.connect() # Connect to database
                self.db.database['metadata'].insert_one({'chat': {'createdAt': now(), 'title': title}}) #  and retry
            self.db.insert({'title': title}) # insert dummy data into collection to properly initialize collection
            self.db.delete({'title': title}) # delete right away

    async def getCollections(self):
        await asyncio.sleep(0.1)
        self.db.connect()
        collections = self.db.getCollections()
        print("collections: ", collections)
        self.gatheredChats.emit(collections)

    def gatherChatHistory(self, collectionNames: List[str]):
        for collection in collectionNames:
            chat  = ChatTitle(title=collection, func=self.showFullChat, parent=self)
            self.historyLayout.addWidget(chat)
            self.historyWidget.setLayout(self.historyLayout)
            self.historyScrollArea.setWidget(self.historyWidget)
            self.installEventFilter(chat)

    def showFullChat(self, collection: str):
        try:
            clearLayout(self.chatLayout)
            chatItems = self.db.database[collection].find().sort("content.date", 1).limit(HISTORY_LIMIT)
            messages = list(map(lambda x: x['content'], chatItems))
            for message in messages:
                msg = TextMessage(text=message.get('text') or message.get('transcription'),
                    origin=message['origin'],
                    date=message['date'],
                    time=message['time']
                )
                self.push(msg)
        finally:
            self.db.chatHistory = self.db.database[collection] #switch to current collection to handle how messages are distributed accross chat
            

    def topLevelHistoryRendering(self, collections: list[str]):
        if not collections or self.db.chatHistory is None:
            self.startNewChat()
        else:
            self.gatherChatHistory(collections)

    def runAsyncforHistory(self):
        spinner = Spinner(parent=self)
        self.worker = Worker(self.getCollections, 'async')

        self.worker.start()

        self.worker.started.connect(spinner.start)
        self.worker.finished.connect(spinner.stop)

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




    



