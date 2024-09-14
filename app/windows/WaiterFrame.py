import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
from PyQt5 import uic

from utils.paths import getFrozenPath, resourcePath
from utils.appHelper import adjustForDPI

# import resources
import app.config.resources

class Waiter(QFrame):
    def __init__(self, parent=None):
        super(Waiter, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "waiter.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setWFlags()
        self.setContents()

    def setWFlags(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setContents(self):
        self.Hlayout = QHBoxLayout()
        self.Hlayout.setAlignment(Qt.AlignTop)
        self.Hlayout.setContentsMargins(10, 0, 10, 10)
        self.container.setLayout(self.Hlayout)

        self.loadingMovie = QMovie(
            resourcePath(os.path.join("assets", "videos", "loading.gif"))#"rsrc/videos/loading.gif"
        )  # Corrected the file path
        self.loadingMovie.start()
        self.loadingLabel = QLabel(self)
        self.loadingLabel.setFixedSize(100, 20)  # Corrected the method usage
        self.loadingLabel.setMovie(self.loadingMovie)

        self.Hlayout.addWidget(self.loadingLabel, alignment=Qt.AlignRight)

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    waiter = Waiter()
    waiter.show()
    sys.exit(app.exec_())
