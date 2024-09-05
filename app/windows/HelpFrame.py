import os

from PyQt5 import uic
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame


from utils.paths import getFrozenPath
from utils.appHelper  import browse

class Help(QFrame):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "help.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()
        
    def initUI(self):
        self.connectSlots()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def connectSlots(self):
        self.docsButton.clicked.connect(self.readDocs)
        self.demoButton.clicked.connect(self.viewDemo)
        self.feedbackButton.clicked.connect(self.giveFeedback)
        self.contributeButton.clicked.connect(self.contributeToProject)

    def readDocs(self):
        link = "https://github.com/cepha/GaelloX"
        browse(link)
    def viewDemo(self):
        link = "https://github.com/cepha/GaelloX"
        browse(link)

    def giveFeedback(self):
        link = "https://github.com/cepha/GaelloX"
        browse(link)

    def contributeToProject(self):
        link = "https://github.com/cepha/GaelloX"
        browse(link)