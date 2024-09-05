# Voice Agent

A python package that makes it easy to interact with LLM's using voice

## Installation
```bash
pip install voiceagent
```

# Description
Voice Agent currently uses AssemblyAI for Speech to Text and ElevenLabs for Text to Speech

You can configure it to work with any LLM of your choice, for example OpenAI,
or set it up to work with LangChain also. You are free to make the LLM setup
as complex as you like, e.g adding Agents, RAG, Memory, or any other features
you like

Voice Agent aims to make it easy to setup your LLM application the way you like,
while also making it easy to get setup with voice

The current flow of requests looks like:
1. Microphone -> Speech To Text (using AssemblyAI)
2. LLM -> Can setup any code you like here to work with the text from the user query
3. Speaker -> Text To Speech (using ElevenLabs)

Getting setup should look as easy as:

```python
from os import getenv
from voiceagent.voice_agent import VoiceAgent

voice_agent = VoiceAgent(
    assemblyai_api_key=getenv('ASSEMBLYAI_API_KEY'),
    elevenlabs_api_key=getenv('ELEVENLABS_API_KEY')
)

def on_message_callback(message):
    print(f"Your message from the microphone: {message}", end="\r\n")
    # add any application code you want here to handle the user request
    # e.g. send the message to the OpenAI Chat API
    return "{response from the LLM}"

voice_agent.on_message(on_message_callback)

print("------------------------------------")
print("Voice Agent started. Start chatting!")
print("------------------------------------")
voice_agent.start()
```

And that is the message returned from `on_message_callback` gets sent to the speakers.
That means you can focus only on writing your application code, and not worry about
speech-to-text and text-to-speech conversions from the microphone and speakers

# Example
The below example shows how to setup OpenAI to work with Voice Agent, so that
you can talk to ChatGPT from your microphone, and hear back it's response from
the speakers.

For convenience, the example script also streams the chat and responses to the command line

```python
from os import getenv
from voiceagent.voice_agent import VoiceAgent
from openai import OpenAI

voice_agent = VoiceAgent(
    assemblyai_api_key=getenv('ASSEMBLYAI_API_KEY'),
    elevenlabs_api_key=getenv('ELEVENLABS_API_KEY')
)

openai_client = OpenAI(
    api_key=getenv('OPENAI_API_KEY'),
)

green = "\033[0;32m"
white = "\033[0;39m"


def on_partial_message_callback(message):
    print(f"{green}You: {message}", end="\r")


def on_message_callback(message):
    print(f"{green}You: {message}", end="\r\n")
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{message}. Keep responses no longer than 20 words",
            }
        ],
        model="gpt-3.5-turbo",
        stream=True
    )
    return chat_completion


def on_response_callback(response):
    print(f"{white}Assistant: {response}", end="\r\n")


voice_agent.on_partial_message(on_partial_message_callback)
voice_agent.on_message(on_message_callback)
voice_agent.on_response(on_response_callback)

print("------------------------------------")
print("Voice Agent started. Start chatting!")
print("------------------------------------")
voice_agent.start()
```

# Event hooks
There are a few event hook you can use from when the user speaks into the microphone
until the audio goes out on the speakers.

In order of the request flow, these event hooks are:

`on_partial_message` - This is called when the user is speaking into the
    microphone, and the speech-to-text conversion is still ongoing. For example
    the user is still speaking into the microphone, so the speech-to-text
    conversion is streaming in real time, but still not finalised. Once there
    is a pause in the user's speech, the message is then considered complete
    and the `on_message` event is called

`on_message` - This is called when the user has finished speaking into the
    microphone (user has paused speaking for more than 1.8 seconds),
    and the speech-to-text conversion is complete, and now ready to be sent
    to an LLM for processing

`on_response` - This is called when the LLM has processed the user's message.
We can use this to access the response returned from the LLM

# Future Work

### Support more Speech-to-Text and Text-to-Speech libraries
Currently the setup is hardcoded to work with AssemblyAI and ElevenLabs. Would
be nice to make it easy to swap these out for other libraries

### Web application examples
Would be nice to setup some web application example that show how to use Voice
Agent via a browser based application

# Current Issues

### Echo Issues
When I tested with certain headsets, or even used the computer speaker and
microphones, the microphone would pick up the speaker's audio,
resulting in ongoing loop of the LLM essentially chatting with itself. Using
a headset where the microphone was a good distance away from the speaker resolved
this

### Latency Issues
Latency could definitely be better for a smoother conversation experience.




