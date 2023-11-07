from telegram import Update
from telegram.ext import CallbackContext
import openai

class OpenAIHandler:
    def __init__(self,openai_api_key):
        self.openai_api_key = openai_api_key

    async def handle_text(self,update: Update, context: CallbackContext) -> None:
        user_message = update.message.text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        response = response.choices[0].message.content
        await update.message.reply_text(response)