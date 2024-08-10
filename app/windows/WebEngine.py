import os

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

from utils.paths import getPath

class DocWebEngineView():
    def __init__(self) -> None:
        self.initUI()
    
    def initUI(self):
        self.web = QWebEngineView()

        self.web.setWindowFlags(
            self.web.windowFlags() | Qt.FramelessWindowHint
        )

        self.web.setFixedSize(800, 600)
        path = getPath(os.path.join("assets", "html", "docs.html"))  
        path = path = os.path.join(r"html\test.html")
        self.web.load(QUrl.fromLocalFile(path))
