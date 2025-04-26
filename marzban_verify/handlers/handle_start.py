from telegram import Update
from telegram.ext import ContextTypes

from marzban_verify.core.verification_code_storage import verification_code_storage


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    verification_code_storage.remove(chat_id)
    await update.message.reply_text("Welcome! Please send me your email address to verify it.")
