import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
from TelegramCommandHandler import TelegramCommandHandler
from OpenAIHandler import OpenAIHandler

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

telegram_command_handler = TelegramCommandHandler()
open_ai_handler = OpenAIHandler(openai.api_key)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', telegram_command_handler.start_command)
    help_handler = CommandHandler('help', telegram_command_handler.help_command)
    unknown_handler = MessageHandler(filters.COMMAND,  telegram_command_handler.unknown_command)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), open_ai_handler.handle_text)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_handler)
    application.add_handler(message_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
