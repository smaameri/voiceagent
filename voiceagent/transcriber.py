import assemblyai as aai

from typing import Callable


class Transcriber:
    def __init__(
            self,
            api_key: str,
            on_data: Callable,
            sample_rate: int = 16000,
            silence_threshold: int = 1800,
    ):
        aai.settings.api_key = api_key
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.on_data = on_data

        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=self.sample_rate,
            on_data=self.aai_on_data,
            on_error=self.aai_on_error,
            on_open=self.aai_on_open,
            on_close=self.aai_on_close,
            end_utterance_silence_threshold=self.silence_threshold
        )

    def aai_on_open(self, session_opened: aai.RealtimeSessionOpened):
        return

    def aai_on_data(self, transcript: aai.RealtimeTranscript):
        self.on_data(transcript.text or "", isinstance(transcript, aai.RealtimeFinalTranscript))

    def aai_on_error(self, error: aai.RealtimeError):
        print("An error occurred:", error)

    def aai_on_close(self):
        return

    def connect(self):
        self.transcriber.connect()

    def stream_from_source(self, stream):
        self.transcriber.stream(stream)

    def close(self):
        self.transcriber.close()
