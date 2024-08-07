import asyncio
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from pyqtspinner.spinner import WaitingSpinner
from typing import Callable, Optional


class Worker(QThread):
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, func: Optional[Callable] = None, funcType:str='sync'):
        super().__init__()
        self.func = func
        self.funcType = funcType

    def run(self, *args, **kwargs):
        if self.func is not None:
            
            if self.funcType=="sync":
                self.started.emit()
                self.func(*args, **kwargs)
                self.finished.emit()

            elif self.funcType=="async":
                self.started.emit()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.func(*args, **kwargs))
                loop.close()
                self.finished.emit()

            else:
                raise ValueError("funcType must be'sync' or 'async'")


class Spinner(QWidget):
    def __init__(self,w=400, h=400, parent=None):
        super(Spinner, self).__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: rgba(150, 100, 150, 100)")

        self.spinner = WaitingSpinner(
            self,
            roundness=100.0,
            fade=80.0,
            radius=20,
            lines=100,
            line_length=10,
            line_width=10,
            speed=1.5707963267948966,
            color=QColor(150, 250, 150, 100)
        )

        self.resize(w, h)  # Adjust size as needed

        self.center()

    def center(self):
        screen = QDesktopWidget().availableGeometry().center()
        frameGeometry = self.frameGeometry()
        frameGeometry.moveCenter(screen)
        self.move(frameGeometry.topLeft())

    def start(self):
        self.show()
        self.spinner.start()

    def stop(self):
        self.spinner.stop()
        self.hide()
