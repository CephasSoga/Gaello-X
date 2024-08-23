import os
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

from app.config.fonts import RobotoRegular, MontserratRegular, FontSizePoint
from app.windows.InsightItems import InsightItem
from app.inferential.ExportInsights import insights
from utils.paths import getFrozenPath
from utils.appHelper import adjustForDPI
from app.config.renderer import ViewController

class JanineInsights(QWidget):

    def __init__(self, parent=None):
        super(JanineInsights, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI" , "insightsWidget.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setupWFlags()
        self.connectSlots()
        self.setupLayout()
        self.setContents()
        self.setFonts()

    def setupLayout(self):
        self.insightslayout = QGridLayout()
        self.insightslayout.setContentsMargins(*ViewController.SCROLL_MARGINS)
        self.insightslayout.setAlignment(Qt.AlignTop)
        self.insightslayout.setSpacing(ViewController.DEFAULT_SPACING)
        self.widget = QWidget()
        self.widget.setLayout(self.insightslayout)

        self.scrollArea.setWidget(self.widget)
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setupWFlags(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)


    def connectSlots(self):
        self.close_.clicked.connect(self.close)


    def eventFilter(self, obj, event):
        if event.type() == Qt.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.hide()
        return super().eventFilter(obj, event)
    
    def setContents(self):
        for idx, insight in enumerate(insights):
            max_per_row = 3
            row = idx // max_per_row
            col = idx % max_per_row
            insight_widget = InsightItem(insight.imagePath, insight.title, insight.content, None)
            self.insightslayout.addWidget(insight_widget, row, col)


    def setFonts(self):
        size = FontSizePoint
        regularFont = RobotoRegular(size.MEDIUM) or QFont("Arial", size.MEDIUM)
        tinyFont = MontserratRegular(size.TINY) or QFont("Arial", size.TINY)
        self.filterLabel.setFont(regularFont)
        self.tuneLabel.setFont(regularFont)
        self.temperatureLabel.setFont(tinyFont)
        self.audacityLabel.setFont(tinyFont)
        self.cycleLabel.setFont(tinyFont)
        self.subjectsCombo.setFont(tinyFont)
        self.locationsCombo.setFont(tinyFont)
        self.assetsCombo.setFont(tinyFont)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = JanineInsights()
    window.show()

    sys.exit(app.exec_())