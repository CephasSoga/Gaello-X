import os

from PyQt5.QtGui import QFontDatabase, QFont
from utils.paths import resourcePath

def loadFont(fontPath):
    fontId = QFontDatabase.addApplicationFont(fontPath)
    if fontId == -1:
        print(f"Failed to load font from {fontPath}")
        return None
    fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
    return fontFamily

# staticly load fonts
# Roboto Mono
robotoLight = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Roboto_Mono", "static", "RobotoMono-Light.ttf"
    )
)
robotoRegular = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Roboto_Mono", "static", "RobotoMono-Regular.ttf"
    )
)
robotoMedium = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Roboto_Mono", "static", "RobotoMono-Medium.ttf"
    )
)
robotoSemiBold = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Roboto_Mono", "static", "RobotoMono-SemiBold.ttf"
    )
)
robotoBold = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Roboto_Mono", "static", "RobotoMono-Bold.ttf"
    )
)
# Montserrat
montserratLight = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Montserrat", "static", "Montserrat-Light.ttf"
    )
)
montserratRegular = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Montserrat", "static", "Montserrat-Regular.ttf"
    )
)
montserratMedium = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Montserrat", "static", "Montserrat-Medium.ttf"
    )
)
montserratBold = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Montserrat", "static", "Montserrat-Bold.ttf"
    )
)
# Quicksand
quicksandLight = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Quicksand", "static", "Quicksand-Light.ttf"
    )
)
quicksandRegular = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Quicksand", "static", "Quicksand-Regular.ttf"
    )
)
quicksandMedium = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Quicksand", "static", "Quicksand-Medium.ttf"
    )
)
quicksandBold = resourcePath(
    os.path.join(
        "assets",
        "fonts", "Quicksand", "static", "Quicksand-Bold.ttf"
    )
)
#Exo2
exo2Light = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Exo_2", "static", "Exo2-Light.ttf"
    )
)
exo2Regular = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Exo_2", "static", "Exo2-Regular.ttf"
    )
)
exo2Medium = resourcePath(
    os.path.join(
        "assets",
        "fonts", "Exo_2", "static", "Exo2-Medium.ttf"
    )
)
exo2Bold = resourcePath(
    os.path.join(
        "assets", 
        "fonts", "Exo_2", "static", "Exo2-Bold.ttf"
    )
)

class Font(QFont):
    def __init__(self, fontPath, pointSize):
        super().__init__()
        self.setFamily(fontPath)
        self.setPointSize(pointSize)

class RobotoLight(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(robotoLight), pointSize)

class RobotoRegular(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(robotoRegular), pointSize)

class RobotoMedium(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(robotoMedium), pointSize)

class RobotoSemiBold(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(robotoSemiBold), pointSize)

class RobotoBold(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(robotoBold), pointSize)

class MontserratLight(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(montserratLight), pointSize)

class MontserratRegular(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(montserratRegular), pointSize)

class MontserratMedium(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(montserratMedium), pointSize)

class MontserratBold(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(montserratBold), pointSize)

class QuicksandLight(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(quicksandLight), pointSize)

class QuicksandRegular(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(quicksandRegular), pointSize)

class QuicksandMedium(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(quicksandMedium), pointSize)

class QuicksandBold(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(quicksandBold), pointSize)

class Exo2Light(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(exo2Light), pointSize)

class Exo2Regular(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(exo2Regular), pointSize)

class Exo2Medium(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(exo2Medium), pointSize)

class Exo2Bold(Font):
    def __init__(self, pointSize):
        super().__init__(loadFont(exo2Bold), pointSize)


class FontSizePoint:
    """sets fonts size constants reltive to screen resolution."""
    EXTRA = 16
    BIGGER = 14
    BIG = 12
    MEDIUM = 10
    SMALL = 9
    TINY = 8
