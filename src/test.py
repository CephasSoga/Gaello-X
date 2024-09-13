from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMetaObject, Qt

class MessageBox(QMessageBox):
    def __init__(self, title: str = None, message: str = None, level: str = None, buttons: tuple[str, str] | tuple[str] = None, parent=None):
        super().__init__(parent)
        # Set the style, title, message, icon, and buttons as needed


        if title is not None:
            self.setWindowTitle(title)
        if message is not None:
            self.setText(message)

        if level is not None:
            self.setIcon(getattr(QMessageBox, level.capitalize(), None) or QMessageBox.Critical)
       
        if buttons is not None:
            self.buttons(buttons)
        
    def buttons(self, options: tuple[str, str] | tuple[str] = ("Ok", "Cancel")):
        buttons = {
            ("ok", "cancel"): QMessageBox.Ok | QMessageBox.Cancel,
            ("yes", "no"): QMessageBox.Yes | QMessageBox.No,
            ("ok", ): QMessageBox.Ok
        }.get(tuple(option.lower() for option in options))
        if buttons is not None:
            self.setStandardButtons(buttons)
        else:
            raise ValueError("Invalid buttons provided")

    def exec_on_thread(self):
        # Create a worker to run the message box in a non-blocking way
        self.worker = MessageBoxWorker(self)
        self.worker.result_signal.connect(self.return_result)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def return_result(self, result: int):
        # Handle the result back in the main thread
        if result == QMessageBox.Yes:
            print("User clicked Yes")
        else:
            print("User clicked No")


class MessageBoxWorker(QThread):
    result_signal = pyqtSignal(int)
    
    def __init__(self, msg_box: MessageBox):
        super().__init__()
        self.msg_box = msg_box

    def run(self):
        # Use QMetaObject to ensure exec_ is called in the main thread
        result = QMetaObject.invokeMethod(self.msg_box, "exec_", Qt.BlockingQueuedConnection)
        self.result_signal.emit(result)
