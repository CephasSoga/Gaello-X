import winreg
import shutil
import tempfile

from utils.logs import Logger

logger = Logger("VersionControl")

class VersionBackup:
    appDir = None
    backupDir = None

    def get_where_application_is_installed(self, app_name: str):
        logger.log("info", "Querying Windows registry for app installation path...")
        app_path_match = None
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
                    display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                    if app_name.lower() in display_name.lower():
                        install_path = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
                        logger.log("info", f"Valid path found: {install_path}")
                        winreg.CloseKey(subkey)  # Close each key after reading
                        app_path_match = install_path
                        return install_path
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(subkey)
            
            # check if no ma
            if app_path_match is None:
                logger.log("info", "Application not found.")

        except Exception as e:
            logger.log("error", "Error accessing registry.", e)
        return None
    
    def create_backup(self):
        self.appDir = self.get_where_application_is_installed("Gaello")
        if not self.appDir:
            logger.log("error", "Application not found.")
            return None

        try:
            self.backupDir = tempfile.mkdtemp()
            logger.log("info", f"Backup directory created at: {self.backupDir}")
            logger.log("info", "Creating backup...")
            shutil.copytree(self.appDir, self.backupDir, dirs_exist_ok=True)
            logger.log("info", "Backup created successfully.")
            return self.backupDir
        except Exception as e:
            logger.log("error", "Error creating backup.", e)
            return None
    
    def restore_backup(self):
        if not self.backupDir or not self.appDir:
            return False

        try:
            logger.log("info", "Restoring backup...")
            shutil.rmtree(self.appDir)
            shutil.copytree(self.backupDir, self.appDir, dirs_exist_ok=True)
            logger.log("info", "Backup restored successfully.")
            return True
        except Exception as e:
            logger.log("error", "Error restoring backup.", e)
            return False
        
    def delete_backup(self):
        if not self.backupDir:
            logger.log("info", "Backup not found.")
            return False

        try:
            logger.log("info", "Deleting backup...")
            shutil.rmtree(self.backupDir)
            logger.log("info", "Backup deleted successfully.")
            return True
        except Exception as e:
            logger.log("error", "Error deleting backup.", e)
            return False            