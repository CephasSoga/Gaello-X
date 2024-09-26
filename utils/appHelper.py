import sys
import webbrowser
from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QApplication, QDesktopWidget

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

def moveWidget(widget: QWidget, parent: QWidget = None, x: str = 'left', y: str = 'top'):
    """
    Moves the specified widget to the edge of the screen based on the provided x and y coordinates.
    If a parent widget is provided, the widget will be moved relative to the parent's geometry.
    If no parent widget is provided, the widget will be moved relative to the primary screen.

    This function can lead to overlapping when the new coords conflict with exisiting widgets.
    If such behaviour is not desired, use the `moveWithoutOverlap` function instead.

    Parameters:
    - widget (QWidget): The widget to be moved.
    - parent (QWidget, optional): The parent widget. If not provided, the primary screen will be used. Defaults to None.
    - x (str, optional): The x-coordinate position. It can be either 'center' or 'left' or 'right'. Defaults to 'left'.
    - y (str, optional): The y-coordinate position. It can be either 'center' or 'top' or 'bottom'. Defaults to 'top'.

    Raises:
    - ValueError: If the provided x or y coordinates are not valid.

    Returns:
    - None
    """
    if not parent:
        geometry = QApplication.desktop().screenGeometry()
    else:
        widget.setParent(parent)
        geometry = parent.geometry()

    if x == 'left':
        new_x = 0
    elif x == 'right':
        new_x = geometry.width() - widget.width()
    elif x == 'center':
        new_x = (geometry.width() - widget.width()) // 2
    else:
        raise ValueError("x must be 'left' or 'right'.")

    if y == 'top':
        new_y = 0
    elif y == 'bottom':
        new_y = geometry.height() - widget.height()
    elif y == 'center':
        new_y = (geometry.height() - widget.height()) // 2
    else:
        raise ValueError("y must be 'top' or 'bottom'.")

    widget.move(new_x, new_y)


def moveWithoutOverlap(widget: QWidget, parent: QWidget = None, x: str = 'left', y: str = 'top'):
    """
    Moves the specified widget to the edge of the screen based on the provided x and y coordinates.
    If a parent widget is provided, the widget will be moved relative to the parent's geometry.
    If no parent widget is provided, the widget will be moved relative to the primary screen.

    This function takes into account the positions of other widgets to avoid overlapping.

    Parameters:
    - widget (QWidget): The widget to be moved.
    - parent (QWidget, optional): The parent widget. If not provided, the primary screen will be used. Defaults to None.
    - x (str, optional): The x-coordinate position. It can be either 'left' or 'right'. Defaults to 'left'.
    - y (str, optional): The y-coordinate position. It can be either 'top' or 'bottom'. Defaults to 'top'.

    Raises:
    - ValueError: If the provided x or y coordinates are not valid.

    Returns:
    - None
    """
    if not parent:
        desktop = QDesktopWidget()
        geometry = desktop.screenGeometry()
    else:
        geometry = parent.geometry()

    if x == 'left':
        new_x = 0
    elif x == 'right':
        new_x = geometry.width() - widget.width()
    else:
        raise ValueError("x must be 'left' or 'right'.")

    if y == 'top':
        new_y = 0
    elif y == 'bottom':
        new_y = geometry.height() - widget.height()
    else:
        raise ValueError("y must be 'top' or 'bottom'.")

    # Check if there are any other visible windows on the screen
    windows = desktop.topLevelWidgets()
    for window in windows:
        if window != widget and window.isVisible():
            window_geometry = window.geometry()
            if x == 'left':
                if window_geometry.right() > new_x:
                    new_x = window_geometry.right()
            elif x == 'right':
                if window_geometry.left() < new_x + widget.width():
                    new_x = window_geometry.left() - widget.width()

            if y == 'top':
                if window_geometry.bottom() > new_y:
                    new_y = window_geometry.bottom()
            elif y == 'bottom':
                if window_geometry.top() < new_y + widget.height():
                    new_y = window_geometry.top() - widget.height()

    widget.move(new_x, new_y)

    
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
    # Remove and delete all widgets in the layout
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()  # Safely delete the widget
            layout.removeWidget(widget)  # Remove from layout

    # Optionally remove any remaining layout items
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QHBoxLayout | QVBoxLayout | QGridLayout):
            clearLayout(item)
        else:
            layout.removeItem(item)

    # Ensure the layout is fully cleared
    layout.update()

def isEmptyLayout(layout: QVBoxLayout | QHBoxLayout | QGridLayout, mode: str = 'delay') -> bool:
    # if we are using deleteLater() to remove a widget
    # chcking layout count right after might unexpectedly return the count before delaetion
    # take that behavior into account
    """
    Checks if the specified layout is empty or not.

    Args:
        layout (QVBoxLayout|QHBoxLayout|QGridLayout): The layout to check.
        mode (str): The mode to check in. If 'delay', it will return True if the layout count is 1 or less, 
            meaning it is likely the layout is being cleared and will be empty soon. If 'no delay', it will return
            True only if the layout count is exactly 0.

    Returns:
        bool: True if the layout is empty, False otherwise.

    Raises:
        ValueError: If mode is not 'delay' or 'no delay'.
    """
    if mode == 'delay':
        return layout.count() <= 1
    elif mode == 'no delay':
        return layout.count() == 0
    else:
        raise ValueError("mode must be 'delay' or 'no delay'")



def isFrozen():
    """
    Checks if the application is frozen.

    Returns:
        bool: True if the application is frozen, False otherwise.
    """
    return getattr(sys, 'frozen', False)


def getDPI():
    import ctypes
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return dpi

def getScreenSize():
    import ctypes
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    w = screensize[0]
    h = screensize[1]
    return w, h

def adjustForDPI(widget: QWidget) -> Tuple[int, int]:
    """
    Adjusts the window size of the provided QWidget based on the system's DPI settings and screen resolution.

    Args:
        widget (QWidget): The QWidget instance to be resized.

    Returns:
        None
    """
    _BASE_W = 1920
    _SUPPORTED_RES_WIDTHS = [_BASE_W, 1366, 1600]
    _BASE_H = 1080
    _SUPPORTED_RES_HEIGHTS = [_BASE_H, 768, 900]
    _BASE_DPI = 144
    _SUPPORTED_DPI_SETTINGS = [_BASE_DPI, 96, 192]
    _BASE_SCALE = 1.5
    _SUPPORTED_SCALES = [_BASE_SCALE, 1.0, 1.2, 1.25, 1.4, 2.0]
    _CURRENT_W: int = getScreenSize()[0]
    _CURRENT_H: int = getScreenSize()[1]

    w_resize_factor = _CURRENT_W / _BASE_W
    h_resize_factor = _CURRENT_H / _BASE_H

    from PyQt5.QtGui import QGuiApplication
    dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
    scalingFactor = dpi / 96.0  # Default DPI
    
    if ( dpi not in _SUPPORTED_DPI_SETTINGS) or (scalingFactor not in _SUPPORTED_SCALES) or (_CURRENT_H not in _SUPPORTED_RES_HEIGHTS) or (_CURRENT_W not in _SUPPORTED_RES_WIDTHS):
        w_factor = scalingFactor * w_resize_factor
        h_factor = scalingFactor * h_resize_factor
        for child in widget.children():
            if not isinstance(child, QGridLayout | QVBoxLayout | QHBoxLayout):
                if isinstance(child, QPushButton):
                    continue # Buttons sometimes have complex stylsheet we don't want  to overwrite; and since they are usually small...
                elif isinstance(child, QLabel):
                    if child.pixmap() is not None: 
                        continue # Ignore labels that displays images
                    child.resize(
                        int(child.width() * w_factor), 
                        int(child.height() * h_factor)
                    )
                elif isinstance(child, QWidget) and not isinstance(child, QLabel | QPushButton):
                    child.resize(
                        int(child.width() *  w_factor), 
                        int(child.height() * h_factor)
                    )
        widget.resize(
            int(widget.width() * w_factor), 
            int(widget.height() * h_factor)
        )
    return _CURRENT_W, _CURRENT_H

def setChildRelativeToParentVisibleArea(widget: QWidget, parent: QWidget, x: str = 'center', y: str = 'center'):
    """
    Positions the given widget relative to the visible area of the parent widget based on the provided x and y coordinates.
    
    Parameters:
    - widget (QWidget): The widget to be positioned.
    - parent (QWidget): The parent widget of which the visible area is used for positioning.
    - x (str): The x-coordinate position. It can be either 'left', 'right' or 'center'. Default is 'center'.
    - y (str): The y-coordinate position. It can be either 'top', 'bottom' or 'center'. Default is 'center'.
    
    Raises:
    - ValueError: If the provided x or y coordinates are not valid.
    
    Returns:
    - None
    """


    widget.setParent(parent)
    
    visibleParentArea = parent.visibleRegion().boundingRect()
    if x == 'left':
        new_x = visibleParentArea.x()
    elif x == 'right':
        new_x = visibleParentArea.x() + visibleParentArea.width() - widget.width()
    elif x == 'center':
        new_x = visibleParentArea.x() + (visibleParentArea.width() - widget.width()) // 2
    else:
        raise ValueError(f'Invalid x value: {x}')


    if y == 'top':
        new_y = visibleParentArea.y()
    elif y == 'bottom':
        new_y = visibleParentArea.y() + visibleParentArea.height() - widget.height()
    elif y == 'center':
        new_y = visibleParentArea.y() + (visibleParentArea.height() - widget.height()) // 2
    else:
        raise ValueError(f'Invalid y value: {y}')

    widget.move(new_x, new_y)
    widget.show()