from telegram import Update
from telegram.ext import CallbackContext
import constants as c

class TelegramCommandHandler:
    def __init__(self):
        pass

    async def start_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(c.START_COMMAND_MSG)

    async def help_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(c.HELP_COMMAND_MSG)

    async def unknown_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(c.UNKNOWN_COMMAND_MSG)
