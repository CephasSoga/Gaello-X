import ctypes

def get_dpi():
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return dpi

#print(f"System DPI: {get_dpi()}")


import ctypes

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

print(f"Screen resolution: {screensize[0]} x {screensize[1]}")


def adjustForDPI(widget: QWidget):
    """
    Adjusts the window size of the provided QWidget based on the system's DPI settings.

    Args:
        widget (QWidget): The QWidget instance to be resized.

    Returns:
        None
    """
    from PyQt5.QtGui import QGuiApplication
    dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
    scalingFactor = dpi / 96.0  # Default DPI
    print(f"DPI: {dpi}, Scaling Factor: {scalingFactor}")
    print("Resizing...")
    _w = widget.width() * scalingFactor
    _h = widget.height() * scalingFactor
    for child in widget.children():
        if not isinstance(child, QGridLayout| QVBoxLayout | QHBoxLayout) and isinstance(child, QWidget):
            if scalingFactor in [1.5]: # 1.5 included as the dev machine has a 144 dpi value and a 1.5 scaling factor. Test for other values as well.
                continue
            child.resize(
                int(child.width() * scalingFactor), 
                int(child.height() * scalingFactor)
            )
    widget.resize(int(_w), int(_h))
    # Adjust other UI elements as needed