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
    def __init__(self, text:str, origin:str="User"):
        self.text = text
        self.origin = origin

    def toString(self):
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
        self.isRecording = False


class VoiceMail:
    def __init__(self, filePath:Path, origin:str="User"):
        self.filePath = filePath
        self.origin = origin
        self.transcription = None
        self.transcriptionFuture = asyncio.ensure_future(self.handleTranscript(self.filePath))
        self.transcriptionFuture.add_done_callback(self.setTranscriptionResult)



    async def toString(self):
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
        return await janineInstance.audioTranscript(filePath)

    async def handleTranscript(self, filePath):
        return await self.transcript(filePath)

    def setTranscriptionResult(self, future):
        try:
            self.transcription = future.result()
        except Exception as e:
            print(f"Error setting transcription result: {e}")
            self.transcription = ""

    def getTranscriptionSync(self):
        if self.transcriptionFuture.done():
            return self.transcription
        else:
            raise RuntimeError("Transcription result is not available yet. Await the future.")



class Multimedia:
    def __init__(self, filePath:Path, text:str="", origin:str="User"):
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
        mimeType, _ = mimetypes.guess_type(self.filePath)
        if mimeType:
            if mimeType.startswith("image"): return "image"
            if mimeType.startswith("video"): return "video"
            if mimeType.startswith("audio"): return "audio"
        return None

    async def transcript(self):
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
            return await self.transcript()

    def setTranscriptionResult(self, future):
        try:
            self.transcription = future.result()
        except Exception as e:
            print(f"Error setting transcription result: {e}")
            self.transcription = ""

    def getTranscriptionSync(self):
        if self.transcriptionFuture.done():
            return self.transcription
        else:
            raise RuntimeError("Transcription result is not available yet. Await the future.")

    async def handleFrames(self):
        return await self.extractFramePaths()
    
    def setFramesResult(self, future):
        try:
            self.frames = future.result()
        except Exception as e:
            print(f"Error setting frames result: {e}")
            self.frames = []

    def getFramesResultSync(self):
        if self.framesFuture.done():
            return self.frames
        else:
            raise RuntimeError("Frames result is not available yet. Await the future.")

    async def toString(self):
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
    def __init__(self, content: TextMessage|VoiceMail|Multimedia):
        self.content = content
        if isinstance(self.content, VoiceMail) or isinstance(self.content, Multimedia):
            self.filePath = self.content.filePath
