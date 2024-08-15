import re
from PyQt5.QtWidgets import QApplication, QTextEdit, QMainWindow
from PyQt5.QtCore import Qt, QTimer

class PathTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.on_text_changed)
        self.highlighted_text = None

    def on_text_changed(self):
        # Temporarily disconnect the signal to avoid recursion
        self.textChanged.disconnect(self.on_text_changed)
        
        # Get the text from the QTextEdit
        text = self.toPlainText()
        # Regex pattern for matching file paths
        pattern = r'/[a-zA-Z0-9_./-]+|[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'
        # Find all matches
        matches = re.findall(pattern, text)
        # Call your function with each path found
        self.highlight_text(matches)
        
        # Reconnect the signal after the update
        self.textChanged.connect(self.on_text_changed)

    def highlight_text(self, paths):
        # Start with plain text
        text = self.toPlainText()
        # Replace each path with an HTML span element with styling
        for path in paths:
            text = text.replace(path, f'<span style="background-color: yellow;">{path}</span>')
        # Set the formatted HTML text back to QTextEdit
        self.setHtml(text)

# Example usage
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_edit = PathTextEdit()
        self.setCentralWidget(self.text_edit)
        self.setWindowTitle("Path Detection in QTextEdit")
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
