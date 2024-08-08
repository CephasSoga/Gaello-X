import os
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

from app.windows.Fonts import RobotoRegular, MontserratRegular
from app.windows.InsightItems import InsightItem
from app.inferential.ExportInsights import insights


currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
os.chdir(parentDir)

class JanineInsights(QWidget):

    def __init__(self, parent=None):
        super(JanineInsights, self).__init__(parent)
        path = os.path.join("UI" , "insightsWidget.ui")
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.initUI()

    def initUI(self):
        self.setupWFlags()
        self.connectSlots()
        self.setupLayout()
        self.setContents()
        self.setFonts()

    def setupLayout(self):
        self.insightslayout = QGridLayout()
        self.insightslayout.setContentsMargins(20, 20, 20, 20)
        self.insightslayout.setAlignment(Qt.AlignTop)
        self.insightslayout.setSpacing(10)
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
        regularFont = RobotoRegular(10) or QFont("Arial", 10)
        tinyFont = MontserratRegular(8) or QFont("Arial", 8)
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