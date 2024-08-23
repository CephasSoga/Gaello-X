from PyQt5.QtWidgets import QApplication,QMainWindow, QWidget,QFrame
from PyQt5 import uic
import sys
import os

class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("assets", "1366x768", "UI", "header.ui"), self)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Test()

    window.show()

    sys.exit(app.exec_())