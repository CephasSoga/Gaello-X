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
    """
    A worker thread that emits signals to start and finish loading tasks.
    """
    loadingStarted = pyqtSignal()
    loadingFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.loaded = False

    def run(self):
        """
        Emits loadingStarted signal, initializes the main window, and emits loadingFinished signal.
        """
        self.loadingStarted.emit()
        self.initializeMainWindow()
        self.loadingFinished.emit()

    def initializeMainWindow(self):
        """
        Simulates a heavy loading task by sleeping for a specified duration and keeping the UI responsive.
        """
        # Simulating heavy loading task
        for _ in range(INIT_TIMEOUT):
            QThread.sleep(SLEEP_SEC)  # Simulates long task
            QAsyncApplication.processEvents()  # Keep the UI responsive
        self.loaded = True

class Client(QObject):
    """
    The main client class that initializes the application, handles connection errors, and starts the worker thread.
    """
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
        """
        Shows the main window.
        """
        self.window = MainWindow()
        self.window.show()

    def raiseConnectionError(self):
        """
        Raises a connection error warning.
        """
        self.warningBox = Warning()
        self.warningBox.warning(
            "Connection Error.",
            "Device is not connected."
        )
        self.warningBox.show()

    def run(self):
        """
        Checks if the device is connected. If not, raises a connection error warning.
        If the device is connected, starts the worker thread and runs the application's event loop.
        """
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
 
