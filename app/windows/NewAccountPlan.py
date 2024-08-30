import os
from pathlib import Path

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QMessageBox

from utils.appHelper import setRelativeToMainWindow, adjustForDPI
from utils.databases import mongoUpdate
from utils.paths import getFrozenPath
from app.config.fonts import RobotoMedium, RobotoBold, QuicksandMedium, RobotoLight, FontSizePoint
from app.windows.PaymentForm import PaymentForm
from app.windows.NewAccountOk import AccountAllSet,  AccountInitFailure
from app.handlers.AuthHandler import sync_read_user_cred_file


class NewAccountPlan(QFrame):
    def __init__(self, parent=None):
        super(NewAccountPlan, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "newAccountPlan.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.paymentForm = None

        # Set the window modality flag
        self.setWindowModality(Qt.NonModal)

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
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

    def getEmail(self):
        email: str = sync_read_user_cred_file().get("email", "")
        if not email:
            QMessageBox.warning(
                None, 
                "Unable to find user credentials", 
                "Credentials Json file might be missing or corrupted. Please, try again."
            )
            return None
        return email

    def submitFreeTier(self):
        parent = self.parent()
        email = self.getEmail()
        if email:
            res = mongoUpdate(
                database='UsersAuth', 
                collection='users', 
                query={'user.email': email}, 
                update={'$set': {'subscription': 'free', 'status': 'ACTIVE', 'authorizationLevel': 1}}
            )
            if res:
                allSet = AccountAllSet()
                allSet.hide()
                setRelativeToMainWindow(allSet, parent, 'center')
                self.close()
            else:
                paymentFailed = AccountInitFailure()
                paymentFailed.hide()
                setRelativeToMainWindow(paymentFailed, parent, 'center')
                self.close()
        else:
            QMessageBox.warning(None, "Missing Credentials", "Close this App and retry creating an account.")
        

    def submitStandardTier(self):
        parent = self.parent()
        nodeAppPath = getFrozenPath(os.path.join('assets', 'binaries', 'checkouts','standard', 'Gaello-webpaypal-standard-tier.exe'))
        execPath = getFrozenPath(".")
        self.paymentForm = PaymentForm(nodeAppPath=nodeAppPath, execPath=execPath)
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def submitAdvancedTier(self):
        parent = self.parent()
        nodeAppPath = getFrozenPath(os.path.join('assets', 'binaries', 'checkouts','advanced', 'Gaello-webpaypal-advanced-tier.exe'))
        execPath = getFrozenPath(".")
        self.paymentForm = PaymentForm(nodeAppPath=nodeAppPath, execPath=execPath)
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def setFonts(self):
        size = FontSizePoint
        boldFont = RobotoBold(size.SMALL) or QFont("Arial", size.SMALL)
        for titleItem in [self.FreeTierTitle, self.StandardTierTitle, self.AdvancedTierTitle]:
            titleItem.setFont(boldFont)

        mediumFont = QuicksandMedium(size.SMALL) or QFont("Arial", size.SMALL)
        for priceItem in [self.FreeTierPrice, self.StandardTierPrice, self.AdvancedTierPrice]:
            priceItem.setFont(mediumFont)

        lightFont = RobotoLight(size.SMALL) or QFont("Arial", size.SMALL)
        for label in [self.freelabel1, self.freelabel2, self.freelabel3, self.stdlabel1, self.stdlabel2, self.stdlabel3,
                      self.advlabel1, self.advlabel2]:
            label.setFont(lightFont)

        buttonFont = RobotoMedium(size.SMALL) or QFont("Arial", size.SMALL)
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
