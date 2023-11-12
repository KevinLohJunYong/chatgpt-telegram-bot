import os
import asyncio
from TelegramCommandHandler import TelegramCommandHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
from OpenAIHandler import OpenAIHandler
from RateLimiterDB import RateLimiterDB
from UsersPromptsDB import UsersPromptsDB

openai = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

application = Application.builder().token(TELEGRAM_TOKEN).build()
loop = asyncio.get_event_loop()
bot = application.bot

TelegramCommandHandler = TelegramCommandHandler()
rate_limiter_db = RateLimiterDB()
users_prompts_db = UsersPromptsDB()
OpenAIHandler = OpenAIHandler(openai.api_key, bot, loop, rate_limiter_db,users_prompts_db)

def main():
    print(rate_limiter_db.print_redis_contents())
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

