import asyncio

from telegram import Update, Bot
from telegram.ext import CallbackContext
import openai

class TaskHandler:
    def __init__(self,openai_api_key):
        self.openai_api_key = openai_api_key



    def audio_task_processor(bot: Bot, loop: asyncio.AbstractEventLoop):
        while True:
            chat_id, audio_file_path = audio_task_queue.get()
            try:
                with open(audio_file_path, "rb") as audio_file:
                    transcript = openai.Audio.translate(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                    loop.call_soon_threadsafe(asyncio.create_task,
                                              bot.send_message(chat_id=chat_id, text=f"Transcribed text: {transcript}"))
            except Exception as e:
                print(e)
                loop.call_soon_threadsafe(asyncio.create_task, bot.send_message(chat_id=chat_id,
                                                                                text="Sorry, an error occurred while transcribing your audio."))