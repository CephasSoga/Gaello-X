@echo off

:: Path to the bundled FFmpeg binary
SET "FFMPEG_PATH=%~dp0assets\binaries\ffmpeg\bin"

:: Check if the bundled FFmpeg exists
if exist "%FFMPEG_PATH%\ffmpeg.exe" (
    echo Using bundled FFmpeg.
    echo Checking version...
    "%FFMPEG_PATH%\ffmpeg.exe" -version

    :: Temporarily add bundled FFmpeg to the system PATH
    SET "PATH=%FFMPEG_PATH%;%PATH%"

    echo FFmpeg has been added to the PATH for this session.
) else (
    echo Bundled FFmpeg not found. Attempting to use system FFmpeg...
    
    :: Check if FFmpeg is installed system-wide
    ffmpeg -version > nul 2>&1
    if %errorlevel% neq 0 (
        echo FFmpeg is not installed on the system. Exiting...
        exit /b
    ) else (
        echo System-wide FFmpeg is available.
    )
)

:: Call your application or any other command that needs FFmpeg
:: For example, starting your PyQt5 application
python src/main.py

:: Keep the command prompt open (useful for debugging)
pause
