import os
import sys
import json
import winreg
import shutil
import tempfile
import asyncio
import aiohttp
import threading
import subprocess
from typing import Callable

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox

from utils.logs import Logger
from utils.envHandler import getenv
from utils.paths import getFileSystemPath
from app.windows.Patterns import GaelloUI

logger = Logger("VersionControl")

class Version (QObject):
    progress = pyqtSignal(int)

    def __init__(
        self,
        version: float,
        name: str,
        target_resolutions: list[str],
        url: str,
    ):
        self.version = version
        self.name = name
        self.target_resolutions = target_resolutions
        self.url = url

    c

class VersionBackUp:
    appDir = None 
    backupDir = None

    def get_where_application_is_installed(self, app_name: str):
        # get where the app is installed
        logger.log("info", "Querying Windows registry for app installation path...")
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, 
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 
                0, 
                winreg.KEY_READ
            )
            for i in range(0, winreg.QueryInfoKey(registry_key)[0]):
                subkey_name = winreg.EnumKey(registry_key, i)
                subkey = winreg.OpenKey(registry_key, subkey_name)
                try:
                    try:
                        display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                    except FileNotFoundError:
                        display_name = ""
                    if app_name.lower() in display_name.lower():
                        install_path = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
                        logger.log("info", "Valid path found:", install_path)
                        return install_path
                except FileNotFoundError:
                    continue
        except Exception as e:
           logger.log("info", f"Error accessing registry.", e)
        return None

    async def create_backup(self):
        self.appDir = self.get_where_application_is_installed("Gaello")
        try:
            # Create a temporary directory for backup
            self.backupDir = tempfile.mkdtemp(prefix="gaello_backup_")
            logger.log("info",f"Backup directory created: {self.backupDir}")

            # Copy the current application files to the backup folder
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, shutil.copytree, self.appDir, self.backupDir, dirs_exist_ok=True)

            logger.log("info", "Backup created successfully.")
            return True
        except Exception as e:
            logger.log("error", f"Error creating backup.", e)
            return False
        
    async def restore_backup(self):
        if self.backupDir:
            try:
                # Restore the files from the backup folder
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, shutil.copytree, self.backupDir, self.appDir, dirs_exist_ok=True)
                logger.log("info", "Backup restored successfully.")
                return True
            except Exception as e:
                logger.log("error", f"Error restoring backup.", e)
                return False
            finally:
                # Delete the backup folder
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, shutil.rmtree, self.backupDir)
        else:
            logger.log("warning", "No backup found to restore.")
            return False

    async def clean_up_backup(self):
        def remove_backup_folder():
            if self.backupDir:
                try:
                    # Delete the backup folder
                    shutil.rmtree(self.backupDir)
                    logger.log("info", "Backup deleted successfully.")
                    return True
                except Exception as e:
                    logger.log("error", f"Error deleting backup: {e}")
                    return False
            else:
                logger.log("warning", "No backup to delete.")
                return False

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, remove_backup_folder) 

class VersionManager(QWidget, GaelloUI):
    progress = pyqtSignal(float)

    def __init__(
            self,
            parent: QWidget | None = ..., 
            flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        QWidget.__init__(parent, flags)
        GaelloUI.__init__()

        self.loadFromFile("updateDownload.ui")

        self.progress.connect(self.update_label)

    async def download(self, version: Version):
        async with aiohttp.ClientSession() as session:
            async with session.get(version.url) as response:
                if response.status == 200:
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        total_size = int(content_length)
                        downloaded = 0
                        chunk_size = 1024 * 1024  # 1 MB
                        try:
                            with open("gaello.exe", "wb") as f:
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
                
    async def check_for_update(self, url: str):
        current_version_data = self.read_version()
        current_version = Version(**current_version_data)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        version_data = await response.json()
                        latest_version = Version(**version_data)
                        if latest_version > current_version:
                            logger.log("info", f"New version {latest_version.version} available.")
                            return latest_version
                        else:
                            logger.log("info", f"You are using the latest version ({current_version.version}).")
                            return None
                    except Exception as e:
                        logger.log("error", f"Error checking version: {e}")
                        return None
                else:
                    logger.log("error", f"Version check failed with status {response.status}.")
                    return None

    def read_version(self):
        targetFile = getFileSystemPath(
            os.path.join(
                getenv("APP_BASE_PATH"),
                "_data",
                "version.json"
            )
        )
        with open(targetFile, "r") as f:
            return json.load(f)
        
    def write_version(self, version: Version):
        targetFile = getFileSystemPath(
            os.path.join(
                getenv("APP_BASE_PATH"),
                "_data",
                "version.json"
            )
        )
        with open(targetFile, "w") as f:
            json.dump(version, f)
        
    def update_label(self, percentage: float):
        self.progressLabel.setText(f"Download progress: {percentage:.2f}%")

    async def main_task(self):
        version_url = getenv("VERSION_CONTROL_URL")
        newer_version = await self.check_for_update(version_url)
        if newer_version is None:
            return

        permission = self.prompt_user_for_download()
        if not permission:
            return

        logger.log("info", f"Downloading version {newer_version.version}...")
        download = await self.download(newer_version)
        if not download:
            return

        backup_manager = VersionBackUp()
        backup_sucessfull = await backup_manager.create_backup()

        if not backup_sucessfull:
            return

        user_wants_to_update_now = self.prompt_user_for_update()
        if not user_wants_to_update_now:
            return
        
        self.warn_for_restart()
        await asyncio.sleep(3)
        self.open_exe("gaello.exe")
        sys.exit(0)

    def prompt_user_for_download(self) -> bool:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("New version available. Would you like to download it?")
        msgBox.setWindowTitle("Update Available")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        return msgBox.exec_() == QMessageBox.Yes
    
    def prompt_user_for_update(self) -> bool:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Would you like to update now?")
        msgBox.setWindowTitle("Update Available")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        return msgBox.exec_() == QMessageBox.Yes
    

    def warn_for_restart(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Update downloaded. Please restart the application.")
        msgBox.setWindowTitle("Update Downloaded")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()


    @staticmethod
    def open_exe(path: str):
        try:
            # Open the .exe file asynchronously (it won't block your Python script)
            subprocess.Popen([path])
            logger.log("info", f"Opened {path}")
        except Exception as e:
            logger.log("error", f"Failed to open {path}", e)