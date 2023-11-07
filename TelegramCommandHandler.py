from telegram import Update
from telegram.ext import CallbackContext

class TelegramCommandHandler:
    def __init__(self):
        pass

    async def start_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Hello! I'm a ChatGPT bot. Send me a message and I will respond to you")

    async def help_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Send me any message and I will try to respond!")

    async def unknown_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Sorry, I didn't understand that command.")
