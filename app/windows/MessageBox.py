import asyncio
from typing import *

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, QMetaObject, Qt
from app.windows.Styles import msgBoxStyleSheet

# import resources
import app.config.resources

class MessageBox(QMessageBox):
    def __init__(self, title: str = None, message: str = None, level: str = None, buttons: tuple[str, str] | tuple[str] = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(msgBoxStyleSheet)

        if title is not None:
            self.setWindowTitle(title)
        if message is not None:
            self.setText(message)

        if level is not None:
            self.setIcon(getattr(QMessageBox, level.capitalize(), None) or QMessageBox.Critical)
       
        if buttons is not None:
            self.buttons(buttons)

        self.thread_exec_result = None
        
    def buttons(self, options: tuple[str, str] | tuple[str] = ("Ok", "Cancel")):
        buttons = {
            ("ok", "cancel"): QMessageBox.Ok | QMessageBox.Cancel,
            ("yes", "no"): QMessageBox.Yes | QMessageBox.No,
            ("ok", ): QMessageBox.Ok
        }.get(tuple(option.lower() for option in options))
        if buttons is not None:
            self.setStandardButtons(buttons)
            return self
        else:
            raise ValueError("Invalid buttons provided")
        
    def level(self, level: str):

        level = {
            "question": QMessageBox.Question,
            "information": QMessageBox.Information,
            "warning": QMessageBox.Warning,
            "critical": QMessageBox.Critical
            }.get(level.lower())
        
        if level is not None:
            self.setIcon(level)
            return self
        else:
            raise ValueError("Invalid level provided")
        
    def title(self, title: str):
        self.setWindowTitle(title)
        return self

    def message(self, message: str):
        self.setText(message)
        return self

    def exec_on_thread(self):
        self.worker = MessageBoxWorker(self)
        self.worker.result_signal.connect(self.return_result)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()
        return self


    def return_result(self, result: int):
        if hasattr(result, 'thread_exec_result'):
            self.thread_exec_result = None # clean up result first
        self.thread_exec_result = result
        return self.thread_exec_result
        

class MessageBoxWorker(QThread):
    result_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, message_box: MessageBox):
        super().__init__()
        self.message_box = message_box
        self.message_box.moveToThread(self)

    def run(self, *args, **kwargs):
       result = self.message_box.exec_(*args, **kwargs)
       self.result_signal.emit(result)
       self.finished_signal.emit()

            
    
