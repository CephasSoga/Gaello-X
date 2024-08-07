import sys
import asyncio
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSlot
from qasync import QEventLoop, QApplication as QAsyncApplication

from app.windows.Spinner import Spinner
from app.windows.MainWindow import MainWindow
from app.windows.WarningFrame import Warning
from utils.connection import deviceIsConnected

INIT_TIMEOUT = 3
SLEEP_SEC = 1

class WorkerThread(QThread):
    loadingStarted = pyqtSignal()
    loadingFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.loaded = False

    def run(self):
        self.loadingStarted.emit()
        self.initializeMainWindow()
        self.loadingFinished.emit()

    def initializeMainWindow(self):
        # Simulating heavy loading task
        for _ in range(INIT_TIMEOUT):
            QThread.sleep(SLEEP_SEC)  # Simulates long task
            QAsyncApplication.processEvents()  # Keep the UI responsive
        self.loaded = True

class Client(QObject):
    def __init__(self):
        super().__init__()
        self.app = QAsyncApplication(sys.argv)
        self.app.setStyle("Oxygen")

        self.spinner = Spinner()
        self.worker_thread = WorkerThread()
        self.worker_thread.loadingStarted.connect(self.spinner.start)
        self.worker_thread.loadingFinished.connect(self.spinner.stop)
        self.worker_thread.loadingFinished.connect(self.showMainWindow)

    def showMainWindow(self):
        self.window = MainWindow()
        self.window.show()

    def raiseConnectionError(self):
        self.warningBox = Warning()
        self.warningBox.warning(
            "Connection Error.",
            "Device is not connected."
        )
        self.warningBox.show()

    def run(self):
        if not deviceIsConnected():
            self.raiseConnectionError()
            self.installEventFilter(self)
            self.warningBox.installEventFilter(self.warningBox)
            sys.exit(self.app.exec_())

        else:
            self.worker_thread.start()
            loop = QEventLoop(self.app)
            asyncio.set_event_loop(loop)

            with loop:
                loop.run_forever()
            sys.exit(self.app.exec_())
 
