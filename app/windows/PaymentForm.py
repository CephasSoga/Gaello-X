import os
import time
import json
import signal
import subprocess
from pathlib import Path

from PyQt5 import uic

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QMessageBox

from app.windows.Fonts import RobotoBold
from app.windows.NewAccountOk import AccountAllSet, AccountInitFailure
from utils.appHelper import setRelativeToMainWindow
from utils.databases import mongoGet
from utils.envHandler import getenv
from utils.appHelper import browse
from utils.system import restoreSystemPath
from utils.paths import getPath

PORT = 8888
IP = 'http://localhost'
CONNECTION_TIMEOUT = 10

class PaymentForm(QFrame):

    success = pyqtSignal()
    failure = pyqtSignal()

    def __init__(self, execPath: Path | str = ".", serverPath: Path = Path('server/server.js'), parent=None):
        path = getPath(os.path.join("assets", "UI", "paymentForm.ui"))
        super(PaymentForm, self).__init__(parent)
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.execPath = execPath
        self.serverPath = serverPath
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
        font = RobotoBold(9) or QFont('Arial', 9)
        for item in self.children():
            item.setFont(font)

    def connectSlots(self):
        self.cancelButton.clicked.connect(self.close)
        self.continueButton.clicked.connect(self.validateUser)

    def getEmail(self):
        if self.email:
            return self.email
        base_path = getenv("APP_BASE_PATH")
        credentials_path = os.path.join(base_path, "credentials", "credentials.json")
        try:
            with open(credentials_path, 'r') as credentials_file:
                credentials = json.load(credentials_file)

            self.email = credentials.get('email', '')
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

    def validatePayment(self) -> bool:
        if not self.email:
           return False
        data = mongoGet(database="UsersAuth", collection="users", query={"user.email": self.email})
        if not data:
            return False
        subscriptionField = data[0].get('subscription', {}) 
        subscriptionStatus = subscriptionField.get('status', '')
        return subscriptionStatus.lower() == 'active'
    
    def handOverToBrowser(self):
        self.getEmail()
        if self.email:
            self.start_node_server()
            browse(f'{IP}:{PORT}')

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
    
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        self.stop_node_server()
        super().closeEvent(event)

    def start_node_server(self):
        if self.nodeProcess is None:
            try:
                self.nodeProcess = subprocess.Popen(
                    ['node', str(self.serverPath)], 
                    cwd=self.execPath, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                QMessageBox.information(self, 'Info', 'Node.js server started')

                stdout, stderr = self.nodeProcess.communicate(timeout=CONNECTION_TIMEOUT)

                if stdout and not stderr:
                        self.success.emit()
                else:
                    self.failure.emit()
            except subprocess.TimeoutExpired:
                self.failure.emit()
                QMessageBox.warning(self, "Server Timeout", "Unable to start server. Please check your internet connection.")
            except Exception as e:
                self.failure.emit()
                QMessageBox.warning(self, "Server Error", f"Unable to start server. Error: {str(e)}")
            finally:
                # Ensure the system’s default DLL search path on Windows systems is restored
                restoreSystemPath()

    def stop_node_server(self):
        if self.nodeProcess is not None:
            try:
                self.nodeProcess.send_signal(signal.SIGTERM)
                self.nodeProcess.wait()
                self.nodeProcess = None
                QMessageBox.information(self, 'Info', 'Node.js server stopped')
            except Exception as e:
                QMessageBox.warning(self, "Server Error", f"Unable to stop server. Error: {str(e)}")
            finally:
                self.nodeProcess = None
    

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    window = PaymentForm()
    window.show()
    app.exec_()