import os
from typing import Optional, Callable

from pymongo.database import Database
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import QFrame, QDialog

from utils.paths import getFrozenPath
from utils.appHelper import setRelativeToMainWindow, adjustForDPI

class ChatTitleSelector(QFrame):
    titleSet = pyqtSignal(str)
    def __init__(self, parent = None):
        super(ChatTitleSelector, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "newChatTitle.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.connectSlots()


    def setWFlags(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        
    def connectSlots(self):
        self.continueButton.clicked.connect(self.continue_)
        self.cancelButton.clicked.connect(self.close)

    def continue_(self):
        title = self.chatTitleEdit.text()
        if title:
            self.titleSet.emit(title)
            self.close()
        else:
            raise ValueError("Title cannot be empty")
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)


class ChatTitle(QFrame):
    isClicked = pyqtSignal()
    def __init__(self, title: str, db: Database, func: Optional[Callable[[str], None]] = None, parent = None, gdparent = None):
        super(ChatTitle, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "chatTitle.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.title = title
        self.db = db
        self.func = func
        self.parent_ = parent

        self.initUI()
    
    def initUI(self):
        self.setWFlags()
        self.setContents()
        self.connectSlots()
        self.installEventFilter(self)  # Install the event filter

    def setWFlags(self):
        self.setWindowFlag(Qt.FramelessWindowHint)

    def setContents(self):
        try:
            title = self.title
        except IndexError: # for a new chat, it won't work the samee as the timestamp is not added on title initialization
            title = self.title
        self.label.setText(title)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            # Convert global position to widget-relative position
            pos = self.mapFromGlobal(event.globalPos())
            if self.rect().contains(pos):
                self.isClicked.emit()
                if self.func:
                    self.func(self.title)
                return True
            return super().eventFilter(obj, event)
        return super().eventFilter(obj, event)
    
    def connectSlots(self):
        self.deleteButton.clicked.connect(self.deleteConfirm)
        self.editButton.clicked.connect(self.editChatTitle)

    def deleteConfirm(self):
        confirmation = ConfirmDrop()
        setRelativeToMainWindow(confirmation, self.parent_, "center")
        confirmation.yes.connect(self.deleteSelf)
        confirmation.no.connect(self.close)

    def deleteSelf(self):
        self.db.drop_collection(self.title)
        self.db['metadata'].delete_one({'chat.title': self.title})
        self.deleteLater()

    def editChatTitle(self):
        titleSelector = ChatTitleSelector()
        setRelativeToMainWindow(titleSelector, self.parent_, "center")
        titleSelector.titleSet.connect(self.editTitle)
        titleSelector.show()

    def editTitle(self, title: str):
        self.db['metadata'].update_one({'chat.title': self.title}, {'$set': {'chat.title': title}})
        self.db[self.title].rename(title)
        self.title = title
        self.setContents()

class ConfirmDrop(QDialog):
    yes = pyqtSignal()
    no = pyqtSignal()
    def __init__(self, parent=None):
        super(ConfirmDrop, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "confirmDrop.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()

    def setWFlags(self):
        self.setWindowFlag(Qt.FramelessWindowHint)

    def connectSlots(self):
        self.yesButton.clicked.connect(self.yesFunc)
        self.noButton.clicked.connect(self.noFunc)

    def yesFunc(self):
        self.yes.emit()
        self.close()

    def noFunc(self):
        self.no.emit()
        self.close()
