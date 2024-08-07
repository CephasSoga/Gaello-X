import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

def stackOnCurrentWindow(window:QWidget) -> None:
    if window.isVisible():
        window.hide()
    else:
        window.show()

def stackOnWindow(window:QWidget, parentWindow:QWidget) -> None:
    window.setParent(parentWindow)
    window.setWindowFlags(Qt.FramelessWindowHint)
    if window.isVisible():
        window.hide()
    else:
        window.show()


def setRelativeToMainWindow(stackedWindow:QWidget, parentWindow:QWidget, option:str="right", modal:bool=False) -> None:
    """
    Set the position of the stacked window relative to the parent window.
    """
    stackedWindow.setParent(parentWindow)
    stackedWindow.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    parentWindow.installEventFilter(stackedWindow)
    
    # Calculate new position relative to the parent window's geometry
    parentGeometry = parentWindow.geometry()
    stackedGeometry = stackedWindow.geometry()
    
    if option == "right":
        new_x = parentGeometry.x() + parentGeometry.width() - stackedGeometry.width()
        new_y = parentGeometry.y()
    elif option == "left":
        new_x = parentGeometry.x()
        new_y = parentGeometry.y()
    elif option == "center":
        new_x = parentGeometry.x() + (parentGeometry.width() - stackedGeometry.width()) // 2
        new_y = parentGeometry.y() + (parentGeometry.height() - stackedGeometry.height()) // 2
    else:
        raise ValueError("Option must be 'right', 'left' or 'center'.")
    
    # Ensure the new position is within screen bounds
    new_x = max(0, new_x)
    new_y = max(0, new_y)
    
    stackedWindow.move(new_x, new_y)
    
    if modal:
        stackedWindow.setWindowModality(Qt.ApplicationModal)
    
    if stackedWindow.isVisible():
        stackedWindow.hide()
    else:
        stackedWindow.show()

def showWindow(window: QWidget):
    window.show()

def browse(url: str):
    webbrowser.open(
        url=url,
        new=2,
        autoraise=True,
    )

def clearLayout(layout: QVBoxLayout|QHBoxLayout|QGridLayout):
    """
    Clears all widgets from the layout.
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
