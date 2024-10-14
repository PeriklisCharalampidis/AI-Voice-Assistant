import asyncio

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from api import AssistantFnc

# Load environment variables from .env file
load_dotenv()

# Define the entry point function for the voice assistant agent
async def entrypoint(ctx: JobContext):
    # Set up the initial chat context for the voice assistant
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by Livekit. Your interface with users will be voice. "
            "You should use short and concise responses, avoiding the use of unpronounceable punctuation."
        ),
    )
    
    # Proceed if ai_functions is an iterable and has items

    # Connect to the room and subscribe to audio tracks only
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    fnc_ctx = AssistantFnc()
    
    # Initialize the voice assistant with various modules:
    # VAD = Voice Activity Detection (to detect when the user is speaking)
    # STT = Speech to Text (to convert user speech into text)
    # TTS = Text to Speech (to convert responses back to audio)
    # chat_ctx = Context for the chat (in this case, initialized above)
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
    )

    # Start the assistant and connect it to the provided room
    assistant.start(ctx.room)

    # Allow the assistant to say an initial greeting and allow for interruptions
    await asyncio.sleep(1)
    await assistant.say("How can I help you today?", allow_interruptions=True)

# Explanation:
# - This is an asynchronous function because async IO is being used.
# - The assistant subscribes to audio tracks and handles them (Voice Activity Detection, Speech-to-Text, Text-to-Speech).
# - The assistant can scale to multiple rooms, connecting to the room provided by JobContext.

# Entry point to run the application
if __name__ == "__main__":
    # Run the app with the entrypoint function as the worker
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

# Explanation:
# - This section runs if the script is executed directly.
# - `cli.run_app` triggers the AI Voice Assistant by creating a new worker using the `entrypoint` function.
