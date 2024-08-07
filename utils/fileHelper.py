import os
import ctypes
import platform

import audioread

def getAudioLength(file_path):
    with audioread.audio_open(file_path) as f:
        duration = f.duration
        return duration

def hideFolder(folder_path):
    system = platform.system()
    
    if system == 'Windows':
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_HIDDEN)
        if not ret:
            raise ctypes.WinError()
    elif system in ['Linux', 'Darwin']:  # Darwin is macOS
        folder_dir = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        hidden_folder_path = os.path.join(folder_dir, '.' + folder_name)
        os.rename(folder_path, hidden_folder_path)
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")


