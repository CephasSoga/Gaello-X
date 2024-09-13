import os
import bson
import asyncio
from dataclasses import dataclass

from pymongo.mongo_client import MongoClient

from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QEvent, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QWidget

from utils.databases import mongoGet, mongoUpdate

from app.config.renderer import ViewController
from app.config.scheduler import Schedule
from app.config.fonts import FontSizePoint, QuicksandRegular, RobotoBold
from app.windows.Styles import chatScrollBarStyle
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI, moveWidget, clearLayout, stackOnCurrentWindow, setRelativeToMainWindow
from utils.asyncJobs import asyncWrap
from app.handlers.AuthHandler import sync_read_user_cred_file

@dataclass
class Unread:
    _id: bson.ObjectId # to help easily manipulate message througout classes
    email: str # eamil of recipient
    status: str 
    title: str
    content: str
    date: str
    time: str

@dataclass
class Read:
    _id: bson.ObjectId # to help easily manipulate message througout classes
    email: str # eamil of recipient
    status: str
    title: str
    content: str
    date: str
    time: str

class Popup(QFrame):
    def __init__(self, count: int,  parent=None):
        super(Popup, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "notificationPopup.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.count = count

        self.initUI()
        
    def initUI(self):
        adjustForDPI(self)
        self.setContents()
        self.setFonts()
        self.connectSlots()
        
    def setContents(self):
        if self.count ==  1:
            self.label.setText("You have 1 unread message.")
        else:
            self.label.setText(f"You have {self.count} unreads messages.")

    def setFonts(self):
        size = FontSizePoint
        font = QuicksandRegular(size.SMALL) or QFont('Arial', size.SMALL)
        self.label.setFont(font)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)

class NotificationExpand(QFrame):
    def __init__(self, message: Unread | Read, parent=None):
        super(NotificationExpand, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "notificationExpand.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.message = message
        
        self.initUI()
        
    def initUI(self):
        adjustForDPI(self)
        self.setContents()
        self.connectSlots()
        self.setFonts()
    
    def setContents(self):
        self.titleLabel.setText(self.message.title)
        self.contentTextEdit.setPlainText(self.message.content.replace("\t", ""))
        self.contentTextEdit.verticalScrollBar().setStyleSheet(chatScrollBarStyle)  
        self.contentTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dateLabel.setText(self.message.date)
        self.timeLabel.setText(self.message.time)

    def setFonts(self):
        size = FontSizePoint
        font = QuicksandRegular(size.SMALL) or QFont('Arial', size.SMALL)
        self.titleLabel.setFont(font)
        self.contentTextEdit.setFont(font)
        self.dateLabel.setFont(font)
        self.timeLabel.setFont(font)
    
    def connectSlots(self):
        self.close_.clicked.connect(self.close)

class NotificationItem(QFrame):

    isExpanded = pyqtSignal()

    def __init__(self, connection: MongoClient, message: Unread | Read, parent=None):
        super(NotificationItem, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "notificationItem.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.connection = connection
        self.message = message

        self.dbName = 'notifications'
        self.collection = 'from_system'

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.connectSlots()
        self.setContents()
        self.setFonts()
        self.installEventFilter(self)

    def setContents(self):
        self.titleLabel.setText(self.message.title)
        #self.contentLabel.setText(self.message.content)
        self.dateLabel.setText(self.message.date)
        self.timeLabel.setText(self.message.time)

    def connectSlots(self):
        self.isExpanded.connect(self.updateTimeout)


    def eventFiltter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.geometry().contains(event.globalPos()):
                self.expand()
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        # Emit the clicked signal when the mouse is pressed
        self.expand()
        # Call the base class implementation to maintain default behavior
        super().mousePressEvent(event)

    def expand(self):
        self.isExpanded.emit()
        try:
            parent = self.parent().parent().parent().parent() # stands for Header widget
        except AttributeError:
            parent = self.parent()
        expandItem = NotificationExpand(self.message, parent)
        setRelativeToMainWindow(expandItem, parent, "center")

    def updateTimeout(self):
        QTimer.singleShot(Schedule.DEFAULT_DELAY, self.syncMongoUpdate)

    def syncMongoUpdate(self):
        asyncio.ensure_future(self.updateMessageStatus())

    async def updateMessageStatus(self):
        print(f"Updating status for message ID: {self.message._id}")
        asyncMongoUpdate = asyncWrap(mongoUpdate)
        res = await asyncMongoUpdate(
            database=self.dbName, 
            collection=self.collection, 
            query={"_id": self.message._id}, 
            update={"$set": {"status": "read"}}, 
            connection=self.connection)
        print(f"Update result: {res}")

    def setFonts(self):
        size = FontSizePoint
        boldFont = RobotoBold(size.MEDIUM) or QFont('Arial', size.MEDIUM)
        smallFont = QuicksandRegular(size.TINY) or QFont('Arial', size.TINY)
        self.titleLabel.setFont(boldFont)
        #self.contentLabel.setFont(font)
        self.dateLabel.setFont(smallFont)
        self.timeLabel.setFont(smallFont)

class Notifications(QFrame):
    def __init__(self, connection: MongoClient, parent=None):
        super(Notifications, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "notifications.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection
        self.dbName = 'notifications'
        self.collection = 'from_system'
        self.unreadsCount = 0
        self.newMessagesCount = 0

        self.initUI()

        QTimer.singleShot(Schedule.DEFAULT_DELAY, self.hotReload)
        QTimer.singleShot(Schedule.DEFAULT_RELOAD_DELAY * Schedule.MAX_MULTIPLIER, self.showPopup) # give it enough time to spot unreadCounts updates

    def initUI(self):
        adjustForDPI(self)
        self.setupLayout()


    def setupLayout(self):
        self.unreads = QWidget()
        self.unreadsLayout = QVBoxLayout()
        self.unreadsScrollArea = QScrollArea()
        self.unreadsLayout.setContentsMargins(*ViewController.SCROLL_MARGINS) 
        self.unreadsLayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.unreadsLayout.setAlignment(Qt.AlignTop)
        self.unreadsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.unreadsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.unreadsScrollArea.setWidgetResizable(True)
        self.unreadsScrollArea.setWidget(self.unreads)
        self.unreads.setLayout(self.unreadsLayout)
        self.unreadsWrapperLayout = QVBoxLayout()
        self.unreadsWrapperLayout.addWidget(self.unreads)
        self.unreadsWidget.setLayout(self.unreadsWrapperLayout)

        self.reads = QWidget()
        self.readsLayout = QVBoxLayout()
        self.readsScrollArea = QScrollArea()
        self.readsLayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.readsLayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.readsLayout.setAlignment(Qt.AlignTop)
        self.readsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.readsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.readsScrollArea.setWidgetResizable(True)
        self.readsScrollArea.setWidget(self.reads)
        self.reads.setLayout(self.readsLayout)
        self.readsWrapperLayout = QVBoxLayout()
        self.readsWrapperLayout.addWidget(self.reads)
        self.readsWidget.setLayout(self.readsWrapperLayout)

    @pyqtSlot()
    def syncSetContents(self):
        asyncio.ensure_future(self.setContents())

    def hotReload(self):
        self.hotReloader = QTimer()
        self.hotReloader.start(Schedule.DEFAULT_RELOAD_DELAY)
        self.hotReloader.timeout.connect(self.syncSetContents)


    async def setContents(self):
        unreads, reads = await self.getNotifications()

        self.classifyNotifications(unreads, reads)

        # set a count value to use with popups
        self.unreadsCount = len(unreads)

    def classifyNotifications(self, unreads: list[Unread], reads: list[Read]):
        # Clear layouts first
        clearLayout(self.unreadsLayout)
        clearLayout(self.readsLayout)

        # Add new items to layouts
        for unread in unreads:
            item = NotificationItem(connection=self.connection, message=unread)
            self.unreadsLayout.addWidget(item)

        for read in reads:
            item = NotificationItem(connection=self.connection, message=read)
            self.readsLayout.addWidget(item)

    @pyqtSlot()
    async def getNotifications(self) -> tuple[list[Unread], list[Read]]:
        try:
            user_creds = sync_read_user_cred_file()
        except FileNotFoundError:
            print("No user credentials found, unable to retrieve notifications.")
            return [], []
        user_email = user_creds.get('email', '')
        if not user_email:
            return [], []
        asyncMoongoGet = asyncWrap(mongoGet)
        data = await asyncMoongoGet(database=self.dbName, collection=self.collection, limit=int(1e2), email=user_email, connection=self.connection)
        if not data:
            return [], []
        unreads = [d for d in data if d.get('status', None).lower() == 'unread']
        reads = [d for d in data if d.get('status', None).lower() == 'read']
        return [Unread(**unread) for unread in unreads], [Read(**read) for read in reads]

    def showPopup(self):
        if self.unreadsCount > 0:
            print("Should show popup now!")
            try:
                parent = self.parent() or self
            except AttributeError:
                parent = self
            popup = Popup(count=self.unreadsCount, parent=parent or self) # Popup shows automatically by calling its own `spawn` method with a timer./
            moveWidget(popup, parent=parent or self, x="right", y="bottom")
            stackOnCurrentWindow(popup)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    import sys
    from qasync import QApplication, QEventLoop

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = Notifications()
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()
  