import os
import ctypes
import platform

import audioread

def getAudioLength(file_path):
    """
    Calculate the duration of an audio file.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        float: The duration of the audio file in seconds.

    Raises:
        audioread.NoBackendError: If no suitable audio backend is found.
        audioread.DecodeError: If there is an error decoding the audio file.

    Example:
        >>> getAudioLength("path/to/audio.mp3")
        123.456
    """
    with audioread.audio_open(file_path) as f:
        duration = f.duration
        return duration

def hideFolder(folder_path):
    """
    Hides a folder based on the current operating system.

    Args:
        folder_path (str): The path to the folder to be hidden.

    Raises:
        ctypes.WinError: If the folder cannot be hidden on Windows.
        NotImplementedError: If the operating system is not supported.

    Returns:
        None
    """
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


