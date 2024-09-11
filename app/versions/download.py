import os
import aiohttp
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget

from utils.logs import Logger
from app.versions.info import Version
from utils.paths import getFrozenPath

logger = Logger("VersionControl")


class VersionDownloadManager:
    progress = pyqtSignal(float)

    def __init__(
            self,
            path_to_store_binary: str | Path,
            parent: QWidget | None = None, 
            flags: Qt.WindowFlags | Qt.WindowType = Qt.FramelessWindowHint) -> None:
        super().__init__(parent, flags)
        path = getFrozenPath(os.path.join("assets", "UI", "updateDownload.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.path_to_store_binary = path_to_store_binary
        self.progress.connect(self.update_label)
    
    async def download_new_binary(self, version: Version):
        async with aiohttp.ClientSession() as session:
            async with session.get(version.url) as response:
                if response.status == 200:
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        total_size = int(content_length)
                        downloaded = 0
                        chunk_size = 1024 * 1024  # 1 MB
                        try:
                            with open(self.path_to_store_binary, "wb") as f:
                                while True:
                                    chunk = await response.read(chunk_size)
                                    if not chunk:
                                        break
                                    downloaded += len(chunk)  # Track downloaded bytes
                                    f.write(chunk)
                                    # Calculate percentage
                                    percentage = (downloaded / total_size) * 100
                                    self.progress.emit(percentage)  # Emit progress as a signal
                                    #print(f"Download progress: {downloaded}/{total_size} bytes")
                                return True
                        except Exception as e:
                            logger.log("error", f"Error downloading version {version.version}", e)
                            return False
                    else:
                        logger.log("error", f"Content-Length header not found.")
                        return False
                else:
                    logger.log("error", f"Download failed with status {response.status}.")
                    return False
        
    def update_label(self, percentage: float):
        self.progressLabel.setText(f"Download progress: {percentage:.2f}%")
