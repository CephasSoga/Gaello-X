import os
from typing import Dict

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLayout, QLineEdit, QMessageBox

from app.windows.Fonts import RobotoRegular
from app.windows.NewAccountPlan import NewAccountPlan
from utils.appHelper import setRelativeToMainWindow, showWindow
from utils.paths import getPath
from databases.mongodb.UsersAuth import UserCredentials, userAuthInstance

class NewAccountSetup(QFrame):
    def __init__(self, parent=None):
        super(NewAccountSetup, self).__init__(parent)
        path = getPath(os.path.join("assets", "UI", "newAccountSetup.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.userAuth = userAuthInstance

        self.initUI()

    def initUI(self):
        self.abstractContens()
        self.setWFlags()
        self.connectSlots()
        self.setFonts()
        
        # Set the window modality flag
        #self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowModality(Qt.WindowModal)
        self.setWindowModality(Qt.NonModal)



        # Install event filter to manage focus and placeholder issues
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.FocusIn, QEvent.FocusOut, QEvent.WindowActivate, QEvent.WindowDeactivate):
            self.handleFocusEvents()

        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                return
        return super().eventFilter(obj, event)

    def handleFocusEvents(self):
        # Handle properties loss whefocus shifts for some QLineEdits
        for widget in [self.passwordEdit, self.confirmPasswordEdit, self.firstNameEdit, self.lastNameEdit, self.emailEdit]:
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: rgb(0, 0, 0);
                    color: rgb(250, 250, 250);
                    border-style: none;
                    border-radius: 24px;
            }
        """)
            
        for widget in [self.companyNameEdit, self.activityComboBox, self.cityEdit, self.countryEdit, self.zipCodeEdit]:
             widget.setStyleSheet("""
                QWidget {
                    border-radius: 0px;
                    color: rgb(255, 255, 255);
                    background-color: rgba(20, 20, 20, 100);
                    font: 9pt "Quicksand";
            }
        """)


    def abstractContens(self):
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordEdit.setEchoMode(QLineEdit.Password)

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) 

    def connectSlots(self):
        self.close_.clicked.connect(self.close)
        self.confirmPasswordEdit.textChanged.connect(self.onPasswordConfirmation)
        self.submitButton.clicked.connect(self.submit)   
        self.cancelButton.clicked.connect(self.close)

    def onPasswordConfirmation(self):
        password = self.passwordEdit.text()
        confirmedPassword = self.confirmPasswordEdit.text()
        if password and confirmedPassword and password != confirmedPassword:
            self.passwordMatchLabel.setText("Passwords do not match")
            self.passwordMatchLabel.setStyleSheet("color: red;")
        elif password and confirmedPassword and password == confirmedPassword:
            self.passwordMatchLabel.setText("Passwords match")
            self.passwordMatchLabel.setStyleSheet("color: green;")

        else:
            self.passwordMatchLabel.clear()

    def spawnAccountPlanSelector(self):
        parent = self.parent()
        self.accountPlanSelector = NewAccountPlan(parent)
        self.accountPlanSelector.hide()
        if not parent:
            showWindow(self.accountPlanSelector)
        else:
            setRelativeToMainWindow(self.accountPlanSelector, parent, 'center')
        self.close()

    def submit(self):
        firstName = self.firstNameEdit.text()
        lastName = self.lastNameEdit.text()
        email = self.emailEdit.text()
        tempPassword = self.passwordEdit.text()
        confirmedPassword = self.confirmPasswordEdit.text()

        if not all([firstName, lastName, email, tempPassword, confirmedPassword]):
            QMessageBox.warning(self, "Missing fields", "Please fill in all fields")
            return

        if tempPassword == confirmedPassword:
            password = tempPassword
        else:
            QMessageBox.warning(self, "Passwords do not match", "Please confirm your password")
            return
        
        companyName = self.companyNameEdit.text()
        activity = self.activityComboBox.currentText()
        city = self.cityEdit.text()
        country = self.countryEdit.text()
        zipCode = self.zipCodeEdit.text()

        pesonalAccount = self.personalAccountRadioButton.isChecked()
        companyAccount = self.companyAccountRadioButton.isChecked()

        if not pesonalAccount and not companyAccount:
            QMessageBox.warning(self, "Invalid Account Type", "Please select an account type")
            return

        prospected = False

        prospectedBySocialMedia = self.socialMediaCheckBox.isChecked()
        prospectedByEmail = self.emailCheckBox.isChecked()
        prospectedbyOnlineAd = self.onlineAdCheckBox.isChecked()
        prospectedByAFellow = self.fellowTraderCheckBox.isChecked()
        prospectedByOther = self.otherCheckBox.isChecked()
        if any([prospectedBySocialMedia, prospectedByEmail, prospectedbyOnlineAd, prospectedByAFellow, prospectedByOther]):
            prospected = True

        
        userInfo = {
            "user" : {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "password": password,
            },

            "company" : {
                "name": companyName,
                "activity": activity,
                "city": city,
                "country": country,
                "zipCode": zipCode,
            },

            "accountType": {
                "personal": pesonalAccount,
                "company": companyAccount
            },

            "prospected": {
                "prospected": prospected,
                "how":{
                    "socialMedia": prospectedBySocialMedia,
                    "email": prospectedByEmail,
                    "onlineAd": prospectedbyOnlineAd,
                    "fellowTrader": prospectedByAFellow,
                    "other": prospectedByOther
                }
            }

        }

        # TODO: ship to mongo database
        credentials = UserCredentials(**userInfo)
        registration = self.userAuth.register(credentials)
        print("registration?: ", registration)

        self.spawnAccountPlanSelector()

    def saveCredentials(credentials: Dict):
        pass

    def setFonts(self):
        font = RobotoRegular(9) or QFont("Arial", 9)
        for item in self.children():
            if not isinstance(item, QLayout):
                item.setFont(font)

