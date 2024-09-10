import winreg
import shutil
import tempfile

from utils.logs import Logger

logger = Logger("VersionControl")

class VersionBackup:
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
    
    def create_backup(self):
        self.appDir = self.get_where_application_is_installed("Gaello")
        try:
            if self.appDir:
                self.backupDir = tempfile.mkdtemp()
                logger.log("info", "Backup directory created:", self.backupDir)
                logger.log("info", "Creating backup...")
                shutil.copytree(self.appDir, self.backupDir, dirs_exist_ok=True)
                logger.log("info", "Backup created successfully.")
                return True
            else:
                logger.log("info", "Application not found.")
                return False
        except Exception as e:
            logger.log("error", "Error creating backup:", e)
            return False
        
    def restore_backup(self):
        try:
            if self.backupDir:
                logger.log("info", "Restoring backup...")
                shutil.rmtree(self.appDir)
                shutil.copytree(self.backupDir, self.appDir, dirs_exist_ok=True)
                logger.log("info", "Backup restored successfully.")
                return True
            else:
                logger.log("info", "Backup not found.")
                return False
        except Exception as e:
            logger.log("error", "Error restoring backup:", e)
            return False
        
    def delete_backup(self):
        try:
            if self.backupDir:
                logger.log("info", "Deleting backup...")
                shutil.rmtree(self.backupDir)
                logger.log("info", "Backup deleted successfully.")
                return True
            else:
                logger.log("info", "Backup not found.")
                return False
        except Exception as e:
            logger.log("error", "Error deleting backup:", e)
            return False