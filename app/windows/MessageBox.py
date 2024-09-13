from PyQt5.QtWidgets import QMessageBox
from app.windows.Styles import msgBoxStyleSheet


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
        
    def level(self, level: str):

        level = {
            "question": QMessageBox.Question,
            "information": QMessageBox.Information,
            "warning": QMessageBox.Warning,
            "critical": QMessageBox.Critical
            }.get(level.lower())
        
        if level is not None:
            self.setIcon(level)
        else:
            raise ValueError("Invalid level provided")
        
    def title(self, title: str):
        self.setWindowTitle(title)

    def message(self, message: str):
        self.setText(message)
