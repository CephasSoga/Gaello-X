import os
from typing import Optional, Callable

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import QFrame

from utils.paths import getFrozenPath

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
        else:
            return super().eventFilter(obj, event)


class ChatTitle(QFrame):
    def __init__(self, title: str,  func: Optional[Callable[[str], None]] = None, parent = None):
        super(ChatTitle, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "chatTitle.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.title = title
        self.func = func

        self.initUI()
    
    def initUI(self):
        self.setWFlags()
        self.setContents()
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
                if self.func:
                    self.func(self.title)
                self.setStyleSheet(
                    """
                    background-color: rgba(10, 10, 10, 180);
                    border-style: solid;
                    border-width: 2px;
                    border-radius: 12px;
                    border-color: rgb(200, 200, 200);
                    """
                )  # Focus style
                return True
            else:
                self.setStyleSheet(
                    """
                    background-color: rgba(0, 0, 0, 0);
                    border-style: solid;
                    border-width: 2px;
                    border-radius: 12px;
                    border-color: rgb(200, 200, 200);
                    """
                )  # No focus
                return True
        return super().eventFilter(obj, event)