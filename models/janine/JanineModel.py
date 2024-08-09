from typing import Optional, List, Dict, Any

from janine.RichText import TextCompletion
from janine.RichAudio import AudioStreamCompletion
from janine.RichVision import VisionCompletion
from janine.RichFile import FileCompletion

from models.api.requests import RequestManager
from databases.mongodb.JanineDB import janineDB

class Janine(TextCompletion, AudioStreamCompletion, VisionCompletion, FileCompletion):
    """
    A class that integrates various completion capabilities for different message types.
    It inherits from TextCompletion, AudioStreamCompletion, VisionCompletion, and FileCompletion.
    """
    def __init__(self):
        """
        Initializes a new instance of the Janine class, inheriting from TextCompletion, 
        AudioStreamCompletion, VisionCompletion, and FileCompletion. It sets up the 
        request manager and database for the instance.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        This function is responsible for completing a message based on its type.

        Parameters:
        history (List[Dict[str, Any]]): A list of previous messages and their content.
        frames (Optional[List]): A list of frames for image or video messages.
        transcription (Optional[str]): The transcription of an audio message.
        textInput (Optional[str]): The text content of the message.
        messageType (str): The type of the message. It can be one of 'text', 'image', 'video', 'file' or 'audio'.

        Returns:
        Any: The completion result based on the message type.
        """
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
        """
        This function retrieves the last message from the request manager,
        processes it, and completes the message using the CompleteMessage function.

        Returns:
        Any: The completion result based on the message type.
        """
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
