import os
from PyQt5 import uic
from utils.paths import getFrozenPath

# import resources
import app.config.resources

class GaelloUI:
    
    def loadFromFile(item, ui_file: str):
        path = getFrozenPath(os.path.join("assets", "UI", ui_file))
        if os.path.exists(path):
            uic.loadUi(path, item)
        else:
            raise FileNotFoundError(f"{path} not found")
