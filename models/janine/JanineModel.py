from typing import Optional, List, Dict, Any

from janine.RichText import TextCompletion
from janine.RichAudio import AudioStreamCompletion
from janine.RichVision import VisionCompletion
from janine.RichFile import FileCompletion

from models.api.requests import RequestManager
from databases.mongodb.JanineDB import janineDB

class Janine(TextCompletion, AudioStreamCompletion, VisionCompletion, FileCompletion):
    def __init__(self):
        TextCompletion.__init__(self)
        AudioStreamCompletion.__init__(self)
        VisionCompletion.__init__(self)
        FileCompletion.__init__(self)

        self.requestManager = RequestManager()
        self.database = janineDB

    async def CompleteMessage(self,
        history: List[Dict[str, Any]] = [],
        frames: Optional[List] = None,
        transcription: Optional[str] = None,
        textInput: Optional[str]= '',
        messageType: str="text",
        ) -> Any:

        if messageType == "text":
            return await self.textCompletion(
                history=history,
                textInput=textInput,
            )
        
        elif messageType == "image":
            return await self.visionCompletion(
                history=history,
                frames=frames,
                transcription = transcription,
                textInput=textInput,
            )

        elif messageType == "audio":
            textResponse  = await self.textCompletion(
                history=history,
                transcription = transcription,
                textInput=textInput,
            )
            return await self.textToAudioFile(textResponse)
        
        elif messageType == "video":
            return await self.visionCompletion(
                history=history,
                frames=frames,
                transcription = transcription,
                textInput=textInput,
            )
    
        elif messageType == "file":
            return "Not Yet Implemented."

        else:
            raise ValueError(f"Message type must be one of 'text', 'image', 'video', 'file' or 'audio'")
        
    async def remoteCompleteMessage(self,
        ) -> Any:
        self.database.deleteExcess()
        history = self.database.history()

        message = await self.requestManager.getLast()
        body = message['body']['content']
        frames = body.get('frames')
        transcription = body.get('transcription')
        textInput = body.get('text')
        messageType = body.get('type')

        return await self.CompleteMessage(
            history=history,
            frames=frames,
            transcription=transcription,
            textInput=textInput,
            messageType=messageType,
        )

janineInstance = Janine()