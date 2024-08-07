import os
from pathlib import Path

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame

from utils.appHelper import *
from app.windows.Fonts import loadFont
from app.windows.PaymentForm import PaymentForm

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
rootDir = os.path.dirname(parentDir)
os.chdir(rootDir)


class NewAccountPlan(QFrame):
    def __init__(self, parent=None):
        super(NewAccountPlan, self).__init__(parent)
        path = os.path.join(parentDir, "UI/newAccountPlan.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            exit()

        self.paymentForm = None

        # Set the window modality flag
        self.setWindowModality(Qt.NonModal)

        self.initUI()

    def initUI(self):
        self.setWFlags()
        self.connectSlots()
        self.setFonts()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)

    def connectSlots(self):
        self.close_.clicked.connect(self.close)
        self.freeTierButton.clicked.connect(self.submitFreeTier)
        self.standardTierButton.clicked.connect(self.submitStandardTier)
        self.advancedTierButton.clicked.connect(self.submitAdvancedTier)

    def submitFreeTier(self):
        parent = self.parent()
        self.paymentForm = PaymentForm(serverPath=Path('server/free.js'))
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def submitStandardTier(self):
        parent = self.parent()
        self.paymentForm = PaymentForm(serverPath=Path('server/standard.js'))
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def submitAdvancedTier(self):
        parent = self.parent()
        self.paymentForm = PaymentForm(serverPath=Path('server/advanced.js'))
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def setFonts(self):
        boldFontFam = loadFont(f'{parentDir}' "/" + r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Bold.ttf")
        if boldFontFam:
            boldFont = QFont(boldFontFam)
            boldFont.setPointSize(9)
        else:
            boldFont = QFont("Arial", 9)

        for titleItem in [self.FreeTierTitle, self.StandardTierTitle, self.AdvancedTierTitle]:
            titleItem.setFont(boldFont)

        mediumFontFam = loadFont(f'{parentDir}' "/" + r"rsrc\fonts\Quicksand\static\Quicksand-Medium.ttf")
        if mediumFontFam:
            mediumFont = QFont(mediumFontFam)
            mediumFont.setPointSize(9)
        else:
            mediumFont = QFont("Arial", 9)

        for priceItem in [self.FreeTierPrice, self.StandardTierPrice, self.AdvancedTierPrice]:
            priceItem.setFont(mediumFont)

        lightFontFam = loadFont(f'{parentDir}' "/" + r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Bold.ttf")
        if lightFontFam:
            lightFont = QFont(lightFontFam)
            lightFont.setPointSize(9)
        else:
            lightFont = QFont("Arial", 9)

        for label in [self.freelabel1, self.freelabel2, self.freelabel3, self.stdlabel1, self.stdlabel2, self.stdlabel3,
                      self.advlabel1, self.advlabel2]:
            label.setFont(lightFont)

        buttonFontFam = loadFont(f'{parentDir}' "/" + r"rsrc/fonts/Roboto_Mono/static/RobotoMono-Medium.ttf")
        if buttonFontFam:
            buttonFont = QFont(buttonFontFam)
            buttonFont.setPointSize(9)
        else:
            buttonFont = QFont("Arial", 9)

        for button in [self.freeTierButton, self.standardTierButton, self.advancedTierButton]:
            button.setFont(buttonFont)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)
    
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = NewAccountPlan()
    window.show()
    sys.exit(app.exec_())
