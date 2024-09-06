import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton

def customize_messagebox():
    # Create a QMessageBox
    msg_box = QMessageBox()
    msg_box.resize(800, 600)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Custom QMessageBox")
    msg_box.setText("Do you want to proceed? This is a test. And see..,.")

    # Customize the buttons with styles
    stylesheet = """
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            padding: 5px 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: rgb(0, 150, 0);
        }
        QPushButton:pressed {
            background-color: #a0a0a0;
        }
    """
    
    # Apply the stylesheet
    msg_box.setStyleSheet(stylesheet)
    
    # Add buttons to the message box
    yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
    no_button = msg_box.addButton("No", QMessageBox.NoRole)
    
    msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    customize_messagebox()
    sys.exit(app.exec_())
