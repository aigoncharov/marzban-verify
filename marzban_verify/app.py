from telegram.ext import Application, CommandHandler, MessageHandler, filters

from marzban_verify.handlers.handle_message import handle_message
from marzban_verify.handlers.handle_start import start
from marzban_verify.utils.config import BOT_TOKEN


def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    # Start the bot
    application.run_polling()
