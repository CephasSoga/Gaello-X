import os
import signal
import subprocess
from pathlib import Path

from PyQt5 import uic

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame
from pymongo import MongoClient

from app.windows.MessageBox import MessageBox
from app.config.fonts import RobotoBold, FontSizePoint
from app.windows.NewAccountOk import AccountAllSet, AccountInitFailure
from utils.appHelper import setRelativeToMainWindow
from utils.databases import mongoGet
from utils.appHelper import browse
from utils.system import restoreSystemPath, killPortProcess
from utils.paths import getFrozenPath, resourcePath
from models.reader.cache import cached_credentials

# import resources
import app.config.resources

PORT = 8888
IP = 'http://localhost'

class PaymentForm(QFrame):

    success = pyqtSignal()
    failure = pyqtSignal()

    def __init__(self, connection: MongoClient, nodeAppPath: Path | str, execPath: Path | str = ".", parent=None):
        path = getFrozenPath(os.path.join("assets", "UI", "paymentForm.ui"))
        super(PaymentForm, self).__init__(parent)
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
      
        self.connection = connection
        self.nodeAppPath = nodeAppPath
        self.execPath = execPath
        self.nodeProcess = None
        self.email: str = None
        self.timer = QTimer()

        QTimer.singleShot(100, self.handOverToBrowser)
        QTimer.singleShot(1000, self.activelyTryValidation)

        self.initUI()
        

    def initUI(self):
        self.setupWFlags()
        self.setFonts()
        self.connectSlots()

    def setupWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)


    def setFonts(self):
        size = FontSizePoint
        font = RobotoBold(size.SMALL) or QFont('Arial', size.SMALL)
        for item in self.children():
            item.setFont(font)

    def connectSlots(self):
        self.cancelButton.clicked.connect(self.close)
        self.continueButton.clicked.connect(self.validateUser)

    def getEmail(self):
        if self.email:
            return self.email
        else:
            self.email = cached_credentials.get("email", "")
            if not self.email:
                messageBox = MessageBox()
                messageBox.level("warning")
                messageBox.title("Unable to find user credentials")
                messageBox.message("Unable to find user credentials.\nCredentials Json file might be missing or corrupted.\nPlease, try again.")
                messageBox.buttons(("ok",))
                messageBox.exec_()
                return None
            return self.email

    def validatePayment(self) -> bool:
        if not self.email:
           return False
        data = mongoGet(database="UsersAuth", collection="users", query={"user.email": self.email}, connection=self.connection)
        if not data:
            return False
        subscriptionField = data[0].get('subscription', {}) 
        subscriptionStatus = subscriptionField.get('status', '')
        return subscriptionStatus.lower() == 'active'
    
    def handOverToBrowser(self):
        self.getEmail()
        if self.email:
            print("Email found: ", self.email)
            self.start_node_server()
            browse(f'{IP}:{PORT}')
        else:
            print("Email not found")
            self.renderFailure()

    def validationResult(self):
        return self.validatePayment()

    def validateUser(self):
        if self.validationResult() == True:
            self.timer.stop()
            self.spawnTerminated()
        else:
            self.continueButton.clicked.disconnect()
            self.continueButton.clicked.connect(self.continueWithBadStatus)

    def continueWithBadStatus(self):
        self.timer.stop()
        self.renderFailure()
            

    def activelyTryValidation(self):
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.validateUser)
        self.timer.start()


    def spawnTerminated(self):
        if self.validatePayment():
            parent = self.parent()
            allSet = AccountAllSet()
            allSet.hide()
            setRelativeToMainWindow(allSet, parent, 'center')
            self.close()
        else:
            self.renderFailure()

    def renderFailure(self):
        parent = self.parent()
        paymentFailed = AccountInitFailure()
        paymentFailed.hide()
        setRelativeToMainWindow(paymentFailed, parent, 'center')
        self.close()
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.stop_node_server()
        super().closeEvent(event)

    def start_node_server(self):
        if self.nodeProcess is None:
            try:
                killPortProcess(PORT) # free port first
                self.nodeProcess = subprocess.Popen(
                    [self.nodeAppPath], 
                    cwd=self.execPath, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    shell=True, 
                    text=True
                )
            except Exception as e:
                messageBox = MessageBox()
                messageBox.level("critical")
                messageBox.title("Server Error")
                messageBox.message(f"Unable to start server. Error: {str(e)}")
                messageBox.buttons(("ok",))
                messageBox.exec_()
                self.close()
                return
            finally:
                # Ensure the system’s default DLL search path on Windows systems is restored
                restoreSystemPath()

    def stop_node_server(self):
        if self.nodeProcess is not None:
            messageBox = MessageBox()
            try:
                self.nodeProcess.send_signal(signal.SIGTERM)
                self.nodeProcess.wait()
                self.nodeProcess = None
                killPortProcess(PORT) # free port then
                messageBox.level("information")
                messageBox.title("Server stopped")
                messageBox.message("Node.js server stopped")
                messageBox.buttons(("ok",))
                messageBox.exec_()
            except Exception as e:
                messageBox.level("critical")
                messageBox.title("Server Error")
                messageBox.message(f"Unable to stop server. Error: {str(e)}")
                messageBox.buttons(("ok",))
                messageBox.exec_()
            finally:
                self.nodeProcess = None
    

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    window = PaymentForm()
    window.show()
    app.exec_()