from telegram.ext import Application, CommandHandler, MessageHandler, filters

from marzban_verify.core.startup_mail_check import send_startup_test_email
from marzban_verify.handlers.handle_message import handle_message
from marzban_verify.handlers.handle_start import start
from marzban_verify.utils.config import BOT_TOKEN


async def _post_init(application: Application) -> None:
    await send_startup_test_email()


def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(_post_init).build()

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
