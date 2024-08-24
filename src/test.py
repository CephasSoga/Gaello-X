from PyQt5.QtWidgets import QMessageBox, QApplication
import sys

def show_custom_message_box():
    msg_box = QMessageBox()
    
    # Set the title and text of the QMessageBox
    msg_box.setWindowTitle("Custom Message")
    msg_box.setText("This is a custom message box with a styled appearance.")
    
    # Add standard buttons
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    # Apply the custom stylesheet
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #f0f0f0;  /* Background color of the QMessageBox */
            font: 14px 'Arial';  /* Font size and family */
            color: #333333;  /* Text color */
        }
        QPushButton {
            background-color: #4CAF50;  /* Button background color */
            color: white;  /* Button text color */
            border-radius: 5px;  /* Rounded corners */
            padding: 5px 10px;  /* Padding inside the button */
        }
        QPushButton:hover {
            background-color: #45a049;  /* Button color on hover */
        }
        QPushButton:pressed {
            background-color: #388E3C;  /* Button color when pressed */
        }
        QLabel {
            color: #333333;  /* Label text color */
        }
    """)

    # Show the QMessageBox
    msg_box.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    show_custom_message_box()
    sys.exit(app.exec_())
