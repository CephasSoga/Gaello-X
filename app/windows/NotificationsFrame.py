import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *

from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI

class Notifications(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Notifications, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "notifications.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
