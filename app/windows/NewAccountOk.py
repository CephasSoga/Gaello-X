import os

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLayout

from app.windows.Fonts import loadFont


currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)


class AccountAllSet(QFrame):
    def __init__(self, parent=None):
        super(AccountAllSet, self).__init__(parent)
        path = os.path.join(r"UI/accountOk.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()
        self.setFonts()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def connectSlots(self):
        #self.close_.clicked.connect(self.close)
        pass

    def setFonts(self):
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Regular.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(16)
        else:
            font = QFont("Arial", 16)

        for item in self.children():
            if not isinstance(item, QLayout):
                item.setFont(font)

            elif isinstance(item, QFrame):
                for subItem in item.children():
                    subItem.setFont(font)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)
    

class AccountInitFailure(QFrame):
    def __init__(self, parent=None):
        super(AccountInitFailure, self).__init__(parent)
        path = os.path.join(r"UI/accountNotOk.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()
        self.setFonts()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint| Qt.Window)

    def connectSlots(self):
        #self.close_.clicked.connect(self.close)
        pass

    def setFonts(self):
        fontFam = loadFont(r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Regular.ttf")
        if fontFam:
            font = QFont(fontFam)
            font.setPointSize(16)
        else:
            font = QFont("Arial", 16)

        for item in self.children():
            if not isinstance(item, QLayout):
                item.setFont(font)

            elif isinstance(item, QFrame):
                for subItem in item.children():
                    subItem.setFont(font)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)

