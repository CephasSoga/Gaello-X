import os
from typing import Dict

from PyQt5 import uic

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLayout, QLineEdit
from pymongo import MongoClient

from app.windows.MessageBox import MessageBox
from app.config.fonts import RobotoRegular, FontSizePoint
from app.windows.NewAccountPlan import NewAccountPlan
from utils.appHelper import setRelativeToMainWindow, showWindow, adjustForDPI
from utils.paths import getFrozenPath
from databases.mongodb.UsersAuth import UserCredentials, UserAuthentification

# import resources
import app.config.resources

class NewAccountSetup(QFrame):
    def __init__(self, connection: MongoClient, parent=None):
        super(NewAccountSetup, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "newAccountSetup.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        # MongoDB connection string
        connection_str = os.getenv("MONGO_URI")
        self.connection = connection
        self.userAuth = UserAuthentification(connection_str=connection_str, connection=connection)

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
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
                pass
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
        self.accountPlanSelector = NewAccountPlan(connection=self.connection, parent=parent)
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
        
        messageBox = MessageBox()

        if not all([firstName, lastName, email, tempPassword, confirmedPassword]):
            messageBox.level("warning")
            messageBox.title("Missing fields")
            messageBox.message("Please fill in all fields")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            return

        if tempPassword == confirmedPassword:
            password = tempPassword
        else:
            messageBox.level("warning")
            messageBox.title("Passwords do not match")
            messageBox.message("Please confirm your password")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            return
        
        companyName = self.companyNameEdit.text()
        activity = self.activityComboBox.currentText()
        city = self.cityEdit.text()
        country = self.countryEdit.text()
        zipCode = self.zipCodeEdit.text()

        pesonalAccount = self.personalAccountRadioButton.isChecked()
        companyAccount = self.companyAccountRadioButton.isChecked()

        if not pesonalAccount and not companyAccount:
            messageBox.level("warning")
            messageBox.title("Invalid Account Type")
            messageBox.message("Please select an account type")
            messageBox.buttons(("ok",))
            messageBox.exec_()
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
        
        if registration ==True:
            client = self.connection
            welcome = self.welcomeNewUser(email, client)
            print("welcome?: ", welcome)

        self.spawnAccountPlanSelector()

    def saveCredentials(credentials: Dict):
        pass

    def welcomeNewUser(self, email: str, client: MongoClient):
        from datetime import datetime
        with open(os.path.join("assets", "txt", "welcome.txt")) as f:
            message_content = f.read()
        message = {
            "email": email,
            "title": "Welcome to the Gaello family!",
            "contnet": message_content,
            "date": datetime.now().date().isoformat(),
            "time": datetime.now().time().isoformat(),
            "status": "unread"
        }
        db = client['noftifications']
        collection = db['from_system']
        try:
            result = collection.insert_one(message)
            return result.inserted_id is not None
        except Exception as e:
            print(e)
            return False

    def setFonts(self):
        size = FontSizePoint
        font = RobotoRegular(size.SMALL) or QFont("Arial", size.SMALL)
        for item in self.children():
            if not isinstance(item, QLayout):
                item.setFont(font)

