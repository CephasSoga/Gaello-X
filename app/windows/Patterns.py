import os
from PyQt5 import uic
from utils.paths import getFrozenPath

class GaelloUI:
    def loadUI(self, ui_file: str):
        path = getFrozenPath(os.path.join("assets", "UI", ui_file))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
