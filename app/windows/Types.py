import  time
import mimetypes
import asyncio
from pathlib import Path

import wave
import random
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal

from utils.time import time_, date
from utils.paths import constructPath
from models.janine.JanineModel import janineInstance
from utils .envHandler import getenv

APP_BASE_PATH = getenv('APP_BASE_PATH')

class TextMessage:
    """
    A class representing a text message.

    Attributes
    ----------
    text : str
        The content of the text message.
    origin : str
        The origin of the text message. Default is "User".

    Methods
    -------
    toString():
        Returns a dictionary representation of the text message.
    """
    def __init__(self, text:str, origin:str="User"):
        """
        Constructs all the necessary attributes for the TextMessage object.

        Parameters
        ----------
        text : str
            The content of the text message.
        origin : str, optional
            The origin of the text message. Default is "User".
        """
        self.text = text
        self.origin = origin

    def toString(self):
        """
        Returns a dictionary representation of the text message.

        Returns
        -------
        dict
            A dictionary with the following keys:
            - role: The role of the message sender ("user" or "system").
            - content: A dictionary containing the message details:
                - text: The content of the text message.
                - origin: The origin of the text message.
                - type: The type of the message ("text").
                - date: The date when the message was sent.
                - time: The time when the message was sent.
        """
        if self.origin == "User":
            role = "user"
        else:
            role = "system"
        return {
            "role": role,
            "content": {
                "text": self.text,
                "origin": self.origin,
                "type": "text",
                "date": date(),
                "time": time_()
            }
        }
    
class Recorder(QThread):
    """
    A class for recording audio using the PyAudio library.

    Attributes
    ----------
    recorded : pyqtSignal(str)
        A PyQt signal that is emitted when recording is completed, passing the file path of the recorded audio.
    progress : pyqtSignal(float)
        A PyQt signal that is emitted during recording, passing the elapsed time in seconds.

    Methods
    -------
    run()
        Starts the recording process. Emits the progress signal periodically and saves the recorded audio to a file.
    stop()
        Stops the recording process.
    """
    recorded = pyqtSignal(str)
    progress = pyqtSignal(float)

    def __init__(self):
        super(Recorder, self).__init__()

        self.isRecording = False
        extension = ".wav"
        suffix = random.randint(0, int(1e6))
        name = "user-voicemail"
        basePath = Path(APP_BASE_PATH)
        relativePath = f"static/exchanges/{name}{suffix}{extension}"
        self.outputFilePath = constructPath(basePath, relativePath)
        self.outputFilePath.parent.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Starts the recording process. Emits the progress signal periodically and saves the recorded audio to a file.
        """
        chunk = 1024
        foemat = pyaudio.paInt16
        channels = 1
        rate = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=foemat,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
        frames = []
        started = time.time()

        self.isRecording = True
        while self.isRecording:
            data = stream.read(chunk)
            frames.append(data)
            elapsed = time.time() - started
            self.progress.emit(elapsed)
        stream.stop_stream()
        stream.close()
        p.terminate()

        with self.outputFilePath.open("wb") as output:
            wf = wave.open(output, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(foemat))
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))
            wf.close()
        self.recorded.emit(str(self.outputFilePath))

    def stop(self):
        """
        Stops the recording process.
        """
        self.isRecording = False


class VoiceMail:
    """
    A class representing a voice mail message.

    Attributes
    ----------
    filePath : Path
        The file path of the recorded audio.
    origin : str
        The origin of the voice mail message. Default is "User".
    transcription : str
        The transcription of the recorded audio.
    transcriptionFuture : asyncio.Future
        A future object representing the asynchronous transcription process.

    Methods
    -------
    toString()
        Returns a dictionary representation of the voice mail message.
    transcript(filePath: Path)
        Asynchronously transcribes the audio file at the given file path.
    handleTranscript(filePath: Path)
        Handles the asynchronous transcription process.
    setTranscriptionResult(future: asyncio.Future)
        Sets the transcription result from the completed future.
    getTranscriptionSync()
        Returns the transcription result synchronously.
    """
    def __init__(self, filePath:Path, origin:str="User"):
        """
        Initializes a new instance of the VoiceMail class.

        Parameters:
            filePath (Path): The file path of the recorded audio.
            origin (str, optional): The origin of the voice mail message. Defaults to "User".

        Returns:
            None
        """
        self.filePath = filePath
        self.origin = origin
        self.transcription = None
        self.transcriptionFuture = asyncio.ensure_future(self.handleTranscript(self.filePath))
        self.transcriptionFuture.add_done_callback(self.setTranscriptionResult)



    async def toString(self):
        """
        Asynchronously converts the object to a dictionary representation.

        This method waits for the transcription future to complete, retrieves the transcription result synchronously,
        and determines the role based on the origin. It then returns a dictionary with the following keys:
        - "role": The role of the message sender ("user" or "system").
        - "content": A dictionary containing the message details:
            - "text": An empty string.
            - "transcription": The transcription result.
            - "origin": The origin of the audio message.
            - "type": The type of the message ("audio").
            - "frames": An empty list.
            - "date": The current date.
            - "time": The current time.

        Returns:
            dict: The dictionary representation of the object.
        """
        await self.transcriptionFuture
        transcriptionResult = self.getTranscriptionSync()
        if self.origin == "User":
            role = "user"
        else:
            role = "system"
        return {
            "role": role,
            "content": {
                "text": "",
                "transcription": transcriptionResult,
                "origin": self.origin,
                "type": "audio",
                "frames": [],
                "date": date(),
                "time": time_()
            }
        }
    
    async def transcript(self, filePath:Path):
        """
        Asynchronously generates the transcript of an audio file.

        Args:
            filePath (Path): The path to the audio file.

        Returns:
            str: The transcript of the audio file.

        Raises:
            None
        """
        return await janineInstance.audioTranscript(filePath)

    async def handleTranscript(self, filePath):
        """
        Asynchronously handles the transcription of an audio file.

        Args:
            filePath (str): The path to the audio file.

        Returns:
            str: The transcript of the audio file.
        """
        return await self.transcript(filePath)

    def setTranscriptionResult(self, future):
        """
        Sets the transcription result from a given future.

        Args:
            future: A future containing the transcription result.

        Returns:
            None

        Raises:
            Exception: If an error occurs while setting the transcription result.
        """
        try:
            self.transcription = future.result()
        except Exception as e:
            print(f"Error setting transcription result: {e}")
            self.transcription = ""

    def getTranscriptionSync(self):
        """
        Checks if the transcription future is done and returns the transcription if available.

        Returns:
            The transcription if available.

        Raises:
            RuntimeError: If the transcription result is not available yet.
        """
        if self.transcriptionFuture.done():
            return self.transcription
        else:
            raise RuntimeError("Transcription result is not available yet. Await the future.")



class Multimedia:
    """
    A class representing multimedia content, such as images, videos, or audio files.

    Attributes:
    filePath (Path): The file path of the multimedia file.
    text (str): The text associated with the multimedia file.
    origin (str): The origin of the multimedia file.

    Methods:
    type_(): Returns the type of the multimedia file based on its MIME type.
    transcript(): Asynchronously generates the transcription of the multimedia file.
    extractFramePaths(): Asynchronously extracts frame paths based on the type of multimedia file.
    handleTranscript(): Asynchronously handles the transcription of the multimedia file.
    setTranscriptionResult(future: concurrent.futures.Future): Sets the transcription result from a given future.
    getTranscriptionSync(): Returns the transcription result synchronously.
    handleFrames(): Asynchronously handles the extraction of frame paths from the multimedia file.
    setFramesResult(future: concurrent.futures.Future): Sets the frames result from a given future.
    getFramesResultSync(): Returns the frames result synchronously.
    toString(): Asynchronously converts the object to a dictionary representation.
    """
    def __init__(self, filePath:Path, text:str="", origin:str="User"):
        """
        Initializes a new instance of the Multimedia class.

        Args:
            filePath (Path): The file path of the multimedia file.
            text (str, optional): The text associated with the multimedia file. Defaults to an empty string.
            origin (str, optional): The origin of the multimedia file. Defaults to "User".

        Returns:
            None

        Initializes the following attributes:
            - filePath (Path): The file path of the multimedia file.
            - text (str): The text associated with the multimedia file.
            - origin (str): The origin of the multimedia file.
            - type (str): The type of the multimedia file.
            - transcription (None): The transcription of the multimedia file.
            - transcriptionFuture (Future): A future representing the transcription task.
            - frames (None): The frames of the multimedia file.
            - framesFuture (Future): A future representing the frames extraction task.

        Initializes the transcription and frames tasks asynchronously using the `handleTranscript` and `handleFrames` methods respectively.
        Adds a callback to the transcription future to set the transcription result using the `setTranscriptionResult` method.
        Adds a callback to the frames future to set the frames result using the `setFramesResult` method.
        """
        self.filePath = filePath
        self.text = text
        self.origin = origin
        self.type = self.type_()
        self.transcription = None
        self.transcriptionFuture = asyncio.ensure_future(self.handleTranscript())
        self.transcriptionFuture.add_done_callback(self.setTranscriptionResult)
        self.frames = None
        self.framesFuture = asyncio.ensure_future(self.handleFrames())
        self.framesFuture.add_done_callback(self.setFramesResult)

    def type_(self):
        """
        Returns the type of the multimedia file based on its MIME type.

        This function uses the `mimetypes.guess_type()` function to determine the MIME type of the file.
        If the MIME type is not None, the function checks if it starts with "image", "video", or "audio".
        If it does, it returns the corresponding type ("image", "video", or "audio").
        If the MIME type is None or does not start with any of the above, the function returns None.

        Returns:
            str or None: The type of the multimedia file ("image", "video", "audio") or None if the MIME type is not recognized.
        """
        mimeType, _ = mimetypes.guess_type(self.filePath)
        if mimeType:
            if mimeType.startswith("image"): return "image"
            if mimeType.startswith("video"): return "video"
            if mimeType.startswith("audio"): return "audio"
        return None

    async def transcript(self):
        """
        Asynchronously generates the transcription of the multimedia file.

        This function checks the type of the multimedia file and returns the corresponding transcription.
        If the type is "image", an empty string is returned.
        If the type is "audio", the function tries to get the audio transcript using `janineInstance.audioTranscript()`.
        If an exception occurs, an error message is printed and an empty string is returned.
        If the type is "video", the function tries to extract the audio from the video using `janineInstance.async_extract_audio()`.
        If an exception occurs, an error message is printed and an empty string is returned.
        If successful, the function gets the audio transcript using `janineInstance.audioTranscript()`.

        Returns:
            str: The transcription of the multimedia file.
        """
        if self.type == "image":
                return ""
        if self.type == "audio":
            try:
                return await janineInstance.audioTranscript(self.filePath)
            except Exception as e:
                print(f"Error getting audio transcript from audio: {e}")
                return ""
        if self.type == "video":
            try:
                extractedAudioPath = await janineInstance.async_extract_audio(self.filePath)
                return await janineInstance.audioTranscript(extractedAudioPath)
            except Exception as e:
                print(f"Error getting audio transcript from video: {e}")
                return ""
            
    async def extractFramePaths(self):
        """
        Asynchronously extracts frame paths based on the type of multimedia file.
        If the type is "image", it tries to extract a single frame path using `janineInstance.async_single_frame`.
        If the type is "audio", it returns an empty list.
        If the type is "video", it tries to extract multiple frame paths using `janineInstance.async_videoframes`.

        Returns:
            List[str]: A list of frame paths extracted from the multimedia file.
        """
        if self.type == "image":
                try:
                    path = await janineInstance.async_single_frame(self.filePath)
                    path = [str(path)]
                    return path
                except Exception as e:
                    print(f"Error creating image frame {e}")
                    return []
        if self.type == "audio":
            return []
        if self.type == "video":
            try:
                framePaths = await janineInstance.async_videoframes(self.filePath)
                framePaths = [str(x) for x in framePaths]
                return framePaths
            except Exception as e:
                print(f"Error creating  video frames {e}")
                return []
            
    async def handleTranscript(self):
        """
        Asynchronously handles the transcription of the multimedia file.
        
        Returns:
            str: The transcription of the multimedia file.
        """
        return await self.transcript()

    def setTranscriptionResult(self, future):
        """
        Sets the transcription result from a given future.

        Args:
            future (concurrent.futures.Future): A future containing the transcription result.

        Returns:
            None

        Raises:
            Exception: If an error occurs while setting the transcription result.

        This method tries to get the result from the given future and assigns it to the `transcription` attribute.
        If an exception occurs during this process, it prints an error message and sets the `transcription` attribute to an empty string.
        """
        try:
            self.transcription = future.result()
        except Exception as e:
            print(f"Error setting transcription result: {e}")
            self.transcription = ""

    def getTranscriptionSync(self):
        """
        Checks if the transcription future is done and returns the transcription if available.

        Returns:
            The transcription if available.

        Raises:
            RuntimeError: If the transcription result is not available yet.
        """
        if self.transcriptionFuture.done():
            return self.transcription
        else:
            raise RuntimeError("Transcription result is not available yet. Await the future.")

    async def handleFrames(self):
        """
        Asynchronously handles the extraction of frame paths from the multimedia file.

        Returns:
            List[str]: A list of frame paths extracted from the multimedia file.
        """
        return await self.extractFramePaths()
    
    def setFramesResult(self, future):
        """
        Sets the frames result from a given future.

        Args:
            future (concurrent.futures.Future): A future containing the frames result.

        Returns:
            None

        Raises:
            Exception: If an error occurs while setting the frames result.

        This method tries to get the result from the given future and assigns it to the `frames` attribute.
        If an exception occurs during this process, it prints an error message and sets the `frames` attribute to an empty list.
        """
        try:
            self.frames = future.result()
        except Exception as e:
            print(f"Error setting frames result: {e}")
            self.frames = []

    def getFramesResultSync(self):
        """
        Checks if the frames future is done and returns the frames if available.

        Returns:
            The frames if available.

        Raises:
            RuntimeError: If the frames result is not available yet.
        """
        if self.framesFuture.done():
            return self.frames
        else:
            raise RuntimeError("Frames result is not available yet. Await the future.")

    async def toString(self):
        """
        Asynchronously converts the object to a dictionary representation.

        This method waits for the transcription future and frames future to complete, retrieves the transcription result synchronously,
        and determines the role based on the origin. It then returns a dictionary with the following keys:
        - "role": The role of the message sender ("user" or "system").
        - "content": A dictionary containing the message details:
            - "text": The content of the message.
            - "transcription": The transcription result.
            - "origin": The origin of the message.
            - "type": The type of the message.
            - "frames": The frames result.
            - "date": The current date.
            - "time": The current time.

        Returns:
            dict: The dictionary representation of the object.
        """
        await self.transcriptionFuture
        await self.framesFuture
        transcriptionResult = self.getTranscriptionSync()
        framesResult = self.getFramesResultSync()
        if self.origin == "User":
            role = "user"
        else:
            role = "system"
        return {
            "role": role,
            "content":{
                "text": self.text,
                "transcription": transcriptionResult,
                "origin": self.origin,
                "type": self.type,
                "frames": framesResult,
                "date": date(),
                "time": time_()
            }
        }

class Message:
    """
    A class representing a message, which can contain text, voice mail, or multimedia content.

    Attributes:
    content (TextMessage|VoiceMail|Multimedia): The content of the message.

    Methods:
    __init__(self, content: TextMessage|VoiceMail|Multimedia): Initializes a new instance of the class with the given content.
    """
    def __init__(self, content: TextMessage|VoiceMail|Multimedia):
        """
        Initializes a new instance of the class with the given content.

        Parameters:
            content (TextMessage|VoiceMail|Multimedia): The content of the message.

        Returns:
            None
        """
        self.content = content
        if isinstance(self.content, VoiceMail) or isinstance(self.content, Multimedia):
            self.filePath = self.content.filePath
