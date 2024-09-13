import os
import shutil

from app.versions.backup import VersionBackup

class VersionUpdater:
    # This class will simply replace the old binaries of the app with the new ones.
    # It will also backup the old binaries and restore them if necessary.
    # It relies on the successful backup creatio, as well as a completed download.
    # path of the download is later passed as an argument and should be carefully checked
    backup_manager = VersionBackup()

    def replace_binary(self, old_binary_dir: str, new_binary_dir: str):
        try:
            if os.path.exists(old_binary_dir) and os.path.isdir(old_binary_dir) and len(os.listdir(old_binary_dir)) > 0:
               shutil.rmtree(old_binary_dir)
            if os.path.exists(new_binary_dir) and os.path.isdir(new_binary_dir) and len(os.listdir(new_binary_dir)) > 0:
               shutil.copytree(new_binary_dir, old_binary_dir, dirs_exist_ok=True)
               return True
            return False
        except shutil.Error as e:
            raise RuntimeError(f"File copy error: {e}")
        except OSError as e:
            raise RuntimeError(f"OS error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")
        
    def restart_app(self, app_path: str):
        import sys
        os.execl(app_path, sys.executable, sys.executable, *sys.argv)
        
    def update_app(self, app_name_str: str, binary_download_path: str):
        if not os.path.exists(binary_download_path) or not os.path.isdir(binary_download_path):
            raise RuntimeError("Invalid binary download path")
        
        backup_path = self.backup_manager.create_backup()
        if not backup_path:
            raise RuntimeError("Failed to create backup")

        try:
            old_binary_dir = self.backup_manager.get_where_application_is_installed(app_name_str)
            new_binary_dir = binary_download_path
            self.replace_binary(old_binary_dir=old_binary_dir, new_binary_dir=new_binary_dir)
        except Exception as e:
            # something went wrong, restore backup
            self.backup_manager.restore_backup()
            raise
        finally:
            self.backup_manager.clean_up_backup()
            # now restart the app
            app_path = self.backup_manager.get_where_application_is_installed(app_name_str) # get app path again
            if not os.path.exists(app_path):
                raise RuntimeError("Failed to restart app")
            self.restart_app(app_path)

if __name__ == "__main__":
    # script shall be executed as subprocess
    app_name = "Gaello"
    binary_download_path = "path_to_downloaded_binary"  # Example
    updater = VersionUpdater()
    updater.update_app(app_name_str=app_name, binary_download_path=binary_download_path)