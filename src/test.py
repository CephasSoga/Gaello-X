from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Minimize Window Example")
        
        # Create a button to minimize the window
        minimize_button = QPushButton("Minimize Window")
        minimize_button.clicked.connect(self.minimize_window)
        
        # Set layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(minimize_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def minimize_window(self):
        self.showMinimized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
