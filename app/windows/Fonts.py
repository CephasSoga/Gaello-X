from PyQt5.QtGui import QFontDatabase

def loadFont(fontPath):
    fontId = QFontDatabase.addApplicationFont(fontPath)
    if fontId == -1:
        print(f"Failed to load font from {fontPath}")
        return None
    fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
    return fontFamily