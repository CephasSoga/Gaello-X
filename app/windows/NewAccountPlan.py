import os
import json
from pathlib import Path

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QMessageBox

from utils.appHelper import setRelativeToMainWindow
from utils.databases import mongoUpdate
from utils.envHandler import getenv
from utils.paths import getFrozenPath
from app.windows.Fonts import RobotoMedium, RobotoBold, QuicksandMedium, RobotoLight
from app.windows.PaymentForm import PaymentForm
from app.windows.NewAccountOk import AccountAllSet,  AccountInitFailure


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
        base_path = getenv("APP_BASE_PATH")
        credentials_path = os.path.join(base_path, "credentials", "credentials.json")
        try:
            with open(credentials_path, 'r') as credentials_file:
                credentials = json.load(credentials_file)

            email: str = credentials.get('email', '')
            return email
        except FileNotFoundError:
            QMessageBox.warning(self, "Credentials were deleted.", "Error: Credentials were deleted. Login again to recreate the file.")
            self.close()
            return
        
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Credentials file is corrupted.", "Error: Credentials file is corrupted. Please, try again.")
            self.close()
            return

        except Exception as e:
            QMessageBox.warning(self, "Error retrieving user's email.", f"Error: {str(e)}")
            self.close()
            return
        
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
            QMessageBox.warning(self, "Missing Credentials", "Close this App and retry creating an account.")
        

    def submitStandardTier(self):
        parent = self.parent()
        serverPathStr = getFrozenPath(os.path.join('server', 'standard.js'))
        self.paymentForm = PaymentForm(serverPath=Path(serverPathStr))
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def submitAdvancedTier(self):
        parent = self.parent()
        serverPathStr = getFrozenPath(os.path.join('server', 'advanced.js'))
        self.paymentForm = PaymentForm(serverPath=Path(serverPathStr))
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    def setFonts(self):
        boldFont = RobotoBold(9) or QFont("Arial", 9)
        for titleItem in [self.FreeTierTitle, self.StandardTierTitle, self.AdvancedTierTitle]:
            titleItem.setFont(boldFont)

        mediumFont = QuicksandMedium(9) or QFont("Arial", 9)
        for priceItem in [self.FreeTierPrice, self.StandardTierPrice, self.AdvancedTierPrice]:
            priceItem.setFont(mediumFont)

        lightFont = RobotoLight(9) or QFont("Arial", 9)
        for label in [self.freelabel1, self.freelabel2, self.freelabel3, self.stdlabel1, self.stdlabel2, self.stdlabel3,
                      self.advlabel1, self.advlabel2]:
            label.setFont(lightFont)

        buttonFont = RobotoMedium(9) or QFont("Arial", 9)
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
