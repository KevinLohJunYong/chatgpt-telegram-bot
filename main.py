import os
import asyncio
from TelegramCommandHandler import TelegramCommandHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
from OpenAIHandler import OpenAIHandler

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

application = Application.builder().token(TELEGRAM_TOKEN).build()
TelegramCommandHandler = TelegramCommandHandler()
loop = asyncio.get_event_loop()
bot = application.bot
OpenAIHandler = OpenAIHandler(openai.api_key, bot, loop)

def main():
    start_handler = CommandHandler('start', TelegramCommandHandler.start_command)
    help_handler = CommandHandler('help', TelegramCommandHandler.help_command)
    unknown_handler = MessageHandler(filters.COMMAND, TelegramCommandHandler.unknown_command)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), OpenAIHandler.handle_text)
    audio_handler = MessageHandler(filters.VOICE, OpenAIHandler.handle_audio)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_handler)
    application.add_handler(message_handler)
    application.add_handler(audio_handler)

    application.run_polling()

if __name__ == '__main__':
    main()

