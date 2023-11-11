import asyncio
from telegram import Update, Bot
from telegram.ext import CallbackContext
import os
from openai import OpenAI

open_ai_client = OpenAI()


class OpenAIHandler:
    def __init__(self,openai_api_key,bot: Bot,loop,rate_limiter_db):
        self.openai_api_key = openai_api_key
        self.bot = bot
        self.loop = loop
        self.rate_limiter_db = rate_limiter_db

    async def handle_text(self,update: Update, context: CallbackContext) -> None:
        if self.rate_limiter_db.is_user_rate_limited(update.message.chat_id):
            await update.message.reply_text("You are sending msg too fast. Try again later.")
            return
        user_message = update.message.text
        if user_message.lower().startswith('image:'):
            await self.handle_image(update,context)
        elif user_message.lower().startswith('audio:'):
            await self.handle_text_to_speech(update,context)
        else:
            await self.handle_gpt_response(update,context)

    async def handle_gpt_response(self,update,context):
        user_message = update.message.text
        response = open_ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        response = response.choices[0].message.content
        await update.message.reply_text(response)

    async def handle_text_to_speech(self,update,context):
        user_message = update.message.text
        chat_id = update.message.chat_id
        prompt = user_message[len('audio:'):].strip()
        await update.message.reply_text("Your audio request has been received, processing...")
        try:
             response = open_ai_client.audio.speech.create(
             model="tts-1",
             voice="alloy",
             input=prompt
             )
             self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_audio(chat_id=chat_id, audio=response))
        except Exception as e:
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                                  text="Sorry, an error occurred while generating your audio."))
    async def handle_image(self,update,context) -> None:
        user_message = update.message.text
        chat_id = update.message.chat_id
        prompt = user_message[len('image:'):].strip()
        await update.message.reply_text("Your image request has been received, processing...")
        try:
            response = open_ai_client.images.generate(model="dall-e-3",prompt=prompt, n=1)
            print(response)
            image_url = response.data[0].url
            print(image_url)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_photo(chat_id=chat_id, photo=image_url))
        except Exception as e:
            print("handle_image exception")
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                            text="Sorry, an error occurred while generating your image."))

    async def process_image(self):
        await self.image_queue_processor.start_processing()

    async def handle_audio(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file = await context.bot.get_file(update.message.voice.file_id)
        audio_file_path = os.path.join(temp_dir, f"{update.message.voice.file_id}.ogg")
        await file.download(audio_file_path)
        await update.message.reply_text("Your audio has been received, transcribing...")
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = open_ai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                self.loop.call_soon_threadsafe(asyncio.create_task,
                                          self.bot.send_message(chat_id=chat_id,
                                                                text=f"Transcribed text: {transcript}"))
        except Exception as e:
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                            text="Sorry, an error occurred while transcribing your audio."))
        finally:
            os.remove(audio_file_path)
