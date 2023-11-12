import asyncio
from telegram import Update, Bot
from telegram.ext import CallbackContext
import os
from openai import OpenAI
import constants as c

open_ai_client = OpenAI()

class OpenAIHandler:
    def __init__(self,openai_api_key,bot: Bot,loop,rate_limiter_db,users_prompts_db):
        self.openai_api_key = openai_api_key
        self.bot = bot
        self.loop = loop
        self.rate_limiter_db = rate_limiter_db
        self.users_prompts_db = users_prompts_db

    async def handle_text(self,update: Update, context: CallbackContext) -> None:
        if self.rate_limiter_db.is_user_rate_limited(update.message.chat_id):
            await update.message.reply_text(c.RATE_LIMIT_MSG)
            return
        user_message = update.message.text
        self.users_prompts_db.add_user_prompt(update.effective_user.id,user_message)
        if user_message.lower().startswith('image:'):
            await self.handle_image(update,context)
        elif user_message.lower().startswith('audio:'):
            await self.handle_text_to_speech(update,context)
        else:
            await self.handle_gpt_response(update,context)

    async def handle_gpt_response(self,update,context):
        context_list = self.users_prompts_db.get_conversation_context(update.effective_user.id)
        formatted_context = " ".join(context_list)
        user_message = update.message.text
        print(context_list)
        print(formatted_context)
        user_prompt_with_context = f"Do not respond to Context. Context: The user has last asked: {formatted_context} " \
                                   f"Do not respond to Context. Please answer: {user_message}"
        print( user_prompt_with_context)
        response = open_ai_client.chat.completions.create(
            model=c.GPT_MODEL,
            messages=[{"role": "user", "content":  user_prompt_with_context}]
        )
        response = response.choices[0].message.content
        await update.message.reply_text(response)

    async def handle_text_to_speech(self,update,context):
        user_message = update.message.text
        chat_id = update.message.chat_id
        prompt = user_message[len('audio:'):].strip()
        await update.message.reply_text(c.PROCESSING_TEXT_TO_SPEECH_MSG)
        try:
             response = open_ai_client.audio.speech.create(
             model=c.TTS_MODEL,
             voice=c.VOICE,
             input=prompt
             )
             self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_audio(chat_id=chat_id, audio=response))
        except Exception as e:
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                                  text=c.TEXT_TO_SPEECH_ERROR_MSG))
    async def handle_image(self,update,context) -> None:
        user_message = update.message.text
        chat_id = update.message.chat_id
        prompt = user_message[len('image:'):].strip()
        await update.message.reply_text(c.PROCESSING_IMAGE_MSG)
        try:
            response = open_ai_client.images.generate(model=c.DALLE_MODEL,prompt=prompt, n=1)
            image_url = response.data[0].url
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_photo(chat_id=chat_id, photo=image_url))
        except Exception as e:
            print("handle_image exception")
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                            text=c.IMAGE_REQUEST_ERROR_MSG))

    async def handle_audio(self, update: Update, context: CallbackContext) -> None:
        if self.rate_limiter_db.is_user_rate_limited(update.message.chat_id):
            await update.message.reply_text(c.RATE_LIMIT_MSG)
            return
        chat_id = update.message.chat_id
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file = await context.bot.get_file(update.message.voice.file_id)
        audio_file_path = os.path.join(temp_dir, f"{update.message.voice.file_id}.ogg")
        await file.download(audio_file_path)
        await update.message.reply_text(c.TRANSCRIBING_AUDIO_MSG)
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = open_ai_client.audio.transcriptions.create(
                    model=c.WHISPER_MODEL,
                    file=audio_file,
                    response_format="text"
                )
                self.users_prompts_db.add_user_prompt(update.effective_user.id,transcript)
                self.loop.call_soon_threadsafe(asyncio.create_task,
                                          self.bot.send_message(chat_id=chat_id,
                                                                text=f"Transcribed text: {transcript}"))
        except Exception as e:
            print(e)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.bot.send_message(chat_id=chat_id,
                                                                            text=c.TRANSCRIBING_AUDIO_ERROR_MSG))
        finally:
            os.remove(audio_file_path)
