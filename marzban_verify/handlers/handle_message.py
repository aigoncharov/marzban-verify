from telegram import Update
from telegram.ext import ContextTypes

from marzban_verify.core.verification_code_storage import verification_code_storage
from marzban_verify.handlers.handle_email import handle_email
from marzban_verify.handlers.handle_verification_code import handle_verification_code


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if verification_code_storage.get(chat_id) is None:
        await handle_email(update, context)
    else:
        await handle_verification_code(update, context)
