import sys
import asyncio
from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt, QTimer
from qasync import QEventLoop, QApplication as QAsyncApplication

from pymongo.mongo_client import MongoClient

from app.windows.Spinner import Spinner
from app.windows.MainWindow import MainWindow
from app.config.scheduler import Schedule
from app.windows.WarningFrame import Warning
from utils.connection import deviceIsConnected
from utils.logs import Logger

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
    async_tasks = []
    old_len = 0
    accumulated_tasks_cont = 0 

    logger = Logger("Client")

    def __init__(self, connection: MongoClient):
        super().__init__()
        Qt.AA_EnableHighDpiScaling = True  # Set this attribute before creating QAsyncApplication
        self.app = QAsyncApplication(sys.argv)
        #self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.app.setStyle("Oxygen")

        self.connection = connection

        self.spinner = Spinner()
        self.worker_thread = WorkerThread()
        self.worker_thread.loadingStarted.connect(self.spinner.start)
        self.worker_thread.loadingFinished.connect(self.spinner.stop)
        self.worker_thread.loadingFinished.connect(self.showMainWindow)

    def showMainWindow(self):
        """
        Shows the main window.
        """
        self.window = MainWindow(connection=self.connection, async_tasks=self.async_tasks)
        self.window.show()
        # then schedule async tasks to complete
        QTimer.singleShot(Schedule.NO_DELAY, self.activelyCompleteNewTasks)
        if getattr(sys, 'frozen', False):
            # If the application is frozen (bundled executable) the pyinstall bootloader will close the splash screen
            import pyi_splash
            pyi_splash.close()

    def checkForNewTasks(self):
        if len(self.async_tasks) > self.old_len:
            async_tasks_len = len(self.async_tasks)
            diff = async_tasks_len - self.old_len
            start_pos = self.old_len
            end_pos = async_tasks_len
            self.old_len = async_tasks_len
            return diff, start_pos, end_pos
            
        
    async def completeNewTasks(self):
        result = self.checkForNewTasks()
        if result:
            diff, start_pos, end_pos = result
            self.accumulated_tasks_cont += diff
            if self.accumulated_tasks_cont >= Schedule.ACCUMULATED_TASKS:
                self.logger.log(
                    "info", 
                    f"Completing {self.accumulated_tasks_cont} tasks | Parallel Execution > [completed: {self.accumulated_tasks_cont - diff}] [pending: {diff}]"
                )
                self.accumulated_tasks_cont = 0
            news_tasks = self.async_tasks[start_pos:end_pos]
            try:
                await asyncio.gather(*news_tasks, return_exceptions=True)
            except Exception:
                raise

    def activelyCompleteNewTasks(self):
        self.timer = QTimer()
        self.timer.setInterval(Schedule.NO_DELAY) 
        self.timer.timeout.connect(lambda: asyncio.ensure_future(self.completeNewTasks()))
        self.timer.start()

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
        if getattr(sys, 'frozen', False):
            # If the application is frozen (bundled executable) the pyinstall bootloader will close the splash screen
            import pyi_splash
            pyi_splash.close()

    def run(self):
        """
        Checks if the device is connected. If not, raises a connection error warning.
        If the device is connected, starts the worker thread and runs the application's event loop.
        """
        if not deviceIsConnected():
            self.raiseConnectionError()
            self.installEventFilter(self)
            self.warningBox.installEventFilter(self.warningBox)

        else:
            self.worker_thread.start()
            loop = QEventLoop(self.app)
            asyncio.set_event_loop(loop)

            with loop:
                loop.run_forever()

        sys.exit(self.app.exec_())
 
