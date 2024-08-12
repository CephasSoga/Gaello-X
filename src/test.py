from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash_pix = QPixmap('splash.png')
    splash = QSplashScreen(splash_pix)
    splash.show()

    # Timer to close the splash screen after 3000 milliseconds (3 seconds)
    QTimer.singleShot(3000, lambda: splash.finish(MainWindow()))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
