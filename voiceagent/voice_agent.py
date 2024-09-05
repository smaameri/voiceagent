from .transcriber import Transcriber
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from typing import Iterator, Callable
import assemblyai as aai
from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk


class VoiceAgent:
    def __init__(
            self,
            assemblyai_api_key: str,
            elevenlabs_api_key: str,
            disable_microphone_on_response: bool = False
    ):
        self.assemblyai_api_key = assemblyai_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.transcriber = Transcriber(
            api_key=assemblyai_api_key,
            on_data=self.on_data

        )
        self.elevenlabs_client = ElevenLabs(
            api_key=self.elevenlabs_api_key,
        )
        self.input_stream = None
        self.disable_microphone_on_response = disable_microphone_on_response
        self.on_message_callback = None
        self.on_partial_message_callback = None
        self.on_response_complete_callback = None
        self.response_stream_iterator = None

    def on_data(self, transcript: str, is_final: bool):
        if not transcript:
            return
        if is_final:
            self.on_final_transcript(transcript)
        else:
            self.on_partial_transcript(transcript)

    def start(self):
        self.transcriber.connect()
        self.input_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream_from_source(self.input_stream)

    def on_message(self, callback: Callable):
        self.on_message_callback = callback

    def on_partial_message(self, callback: Callable):
        self.on_partial_message_callback = callback

    def on_partial_transcript(self, transcript: str):  # <1>
        if self.on_partial_message_callback:
            self.on_partial_message_callback(transcript)

    def on_final_transcript(self, transcript: str):  # <1>
        if self.on_message_callback:
            response = self.on_message_callback(transcript)
            if isinstance(response, str):
                self.text_to_speech(iter([response]))
            elif isinstance(response, Stream):
                self.text_to_speech(self.yield_openai_text_stream(response))
            elif self.response_stream_iterator:
                self.text_to_speech(self.response_stream_iterator(response))
            else:
                raise TypeError(
                    "Stream type is not supported. Currently only streaming for OpenAI responses is supported by"
                    + " default. Otherwise you need to provide your own response stream iterator which returns/fields"
                    + " a result of type Iterator[str]. You can set you customer Iterator by calling the"
                    + " set_response_stream_iterator method")

    def set_response_stream_iterator(self, iterator: Callable):
        self.response_stream_iterator = iterator

    def on_response(self, callback: Callable):
        self.on_response_complete_callback = callback

    def yield_openai_text_stream(self, chat_completion: Stream[ChatCompletionChunk]) -> Iterator[str]:
        full_message = ""
        for chunk in chat_completion:
            text = chunk.choices[0].delta.content or ""
            full_message += text
            yield text
        self.response_complete(full_message)

    def response_complete(self, response: str):
        if self.on_response_complete_callback:
            self.on_response_complete_callback(response)

    def text_to_speech(self, text_stream: Iterator[str]):
        if self.disable_microphone_on_response:
            self.input_stream._stream.stop_stream()

        audio = self.elevenlabs_client.generate(
            text=text_stream,
            voice="Rachel",
            model="eleven_multilingual_v2",
            stream=True
        )

        stream(audio)

        if self.disable_microphone_on_response:
            self.input_stream._stream.start_stream()
