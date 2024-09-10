import os
import shutil

from app.versions.backup import VersionBackup

class VersionUpdater:
    backup_manager = VersionBackup()

    def update(self):
        backup_created = self.backup_manager.create_backup()
        if not backup_created:
            raise RuntimeError("Failed to create backup")
        
        try:
            path_to_binary = "gaello.exe" #path to binary file
            self.exec_downloaded_binary(path_to_binary)
        except Exception as e:
            raise RuntimeError(f"Failed to update: {e}")
        
        # now, as .exe will install non-interactively to a temp folder, check if such folder exits and is not empty
        target_temp_dir = "" # placehaolder
        target_app_dir = self.backup_manager.get_where_application_is_installed("Gaello")
        if not target_app_dir:
            raise RuntimeError("Failed to update. Application not found")
        try:
            if os.path.exists(target_temp_dir) and os.path.isdir(target_temp_dir) and len(os.listdir(target_temp_dir)) > 0:
                # copy temp to app installation location
                shutil.copytree(target_temp_dir, target_app_dir)
                # then remove temp dir
                shutil.rmtree(target_temp_dir)
            else: # something went wrong so we restore backup
                self.backup_manager.restore_backup()
                raise RuntimeError("Failed to update. Restored backup")
        except Exception as e:
            raise RuntimeError(f"Failed to update: {e}")
        finally:
            self.backup_manager.clean_up_backup()

    def exec_downloaded_binary(self, binary_path: str):
        try:
            os.startfile(binary_path)
        except Exception as e:
            raise RuntimeError(f"Failed to update: {e}")

if __name__ == "__main__":
    # script shall be executed as subprocess
    updater = VersionUpdater()
    updater.update()
    
    