import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

def stackOnCurrentWindow(window:QWidget) -> None:
    """
    Hides the given window if it is currently visible, otherwise shows it.

    Args:
        window (QWidget): The window to stack on the current window.

    Returns:
        None
    """
    if window.isVisible():
        window.hide()
    else:
        window.show()

def stackOnWindow(window:QWidget, parentWindow:QWidget) -> None:
    """
    Set the given window as a child of the parent window and stack it on top of it.

    Args:
        window (QWidget): The window to stack on the parent window.
        parentWindow (QWidget): The parent window to stack the window on.

    Returns:
        None
    """
    window.setParent(parentWindow)
    window.setWindowFlags(Qt.FramelessWindowHint)
    if window.isVisible():
        window.hide()
    else:
        window.show()


def setRelativeToMainWindow(stackedWindow:QWidget, parentWindow:QWidget, option:str="right", modal:bool=False) -> None:
    """
    Positions the given window as a child of the parent window and stacks it on top of it.
    The window's position is calculated relative to the parent window's geometry based on the provided option.

    Parameters:
    - stackedWindow (QWidget): The window to stack on the parent window.
    - parentWindow (QWidget): The parent window to stack the window on.
    - option (str): The positioning option. It can be one of the following:
        - "right": Positions the window to the right of the parent window.
        - "left": Positions the window to the left of the parent window.
        - "center": Positions the window in the center of the parent window.
        Default is "right".
    - modal (bool): If True, the window will be modal, meaning it will block user interaction with other windows.
        Default is False.

    Returns:
    - None
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
    """
    Opens the specified URL in a new browser window.

    Args:
        url (str): The URL to open.

    Returns:
        None

    Raises:
        webbrowser.Error: If there is an error opening the URL.
    """
    webbrowser.open(
        url=url,
        new=2,
        autoraise=True,
    )

def clearLayout(layout: QVBoxLayout | QHBoxLayout | QGridLayout):
    """
	Clears all widgets from the specified layout.
	Args:
		layout (QVBoxLayout|QHBoxLayout|QGridLayout): The layout to clear.
	Returns:
		None
	"""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
