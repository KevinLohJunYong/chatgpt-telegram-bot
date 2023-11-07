import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update,context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I'm a ChatGPT bot. Send me a message and I will respond to you")

async def unknown_command(update: Update,context: CallbackContext) -> None:
    await update.message.reply_text("Sorry, I didn't understand that command.")

async def handle_text(update: Update,context: CallbackContext) -> None:
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    response = response.choices[0].message.content
    await update.message.reply_text(response)


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown_command)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)

    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    application.add_handler(message_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
