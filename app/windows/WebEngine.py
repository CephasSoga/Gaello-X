import os

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

from utils.paths import getFrozenPath

# import resources
import app.config.resources

class DocWebEngineView():
    def __init__(self) -> None:
        self.initUI()
    
    def initUI(self):
        self.web = QWebEngineView()

        self.web.setWindowFlags(
            self.web.windowFlags() | Qt.FramelessWindowHint
        )

        self.web.setFixedSize(800, 600)
        path = getFrozenPath(os.path.join("assets", "html", "docs.html"))  
        self.web.load(QUrl.fromLocalFile(path))
