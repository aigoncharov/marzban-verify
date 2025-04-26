from telegram import Update
from telegram.ext import ContextTypes

import marzban_verify.mailers.direct as direct_mailer
import marzban_verify.mailers.exchange as exchange_mailer
from marzban_verify.core.verification_code_storage import verification_code_storage
from marzban_verify.utils.config import ALLOWED_EMAIL_POSTFIX, MAIL_DELIVERY
from marzban_verify.utils.logging import logger
from marzban_verify.utils.username import get_username
from marzban_verify.utils.validators import is_valid_email


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received email address."""

    if MAIL_DELIVERY == "DIRECT":
        mailer = direct_mailer
    elif MAIL_DELIVERY == "EXCHANGE":
        mailer = exchange_mailer
    else:
        raise Exception(f"Unsupported mailer {MAIL_DELIVERY}")

    try:
        chat_id = update.effective_chat.id
        email = update.message.text.strip()

        if not is_valid_email(email):
            await update.message.reply_text(
                "Invalid email format. Please enter a valid email address.\nIf you already have the code, it means that we lost it on our side and you need to request it again.\nI know, it sucks. Life is dark and full of terrors (sigh)..."
            )
            return

        if not email.endswith(ALLOWED_EMAIL_POSTFIX):
            await update.message.reply_text(f"Use your {ALLOWED_EMAIL_POSTFIX} email address.")
            return

        username = get_username(chat_id, email)
        code = verification_code_storage.generate(chat_id, username)

        subject = "Email Verification Code"
        message = (
            f"Your verification code is: {code}\n\nPlease enter this code in the Telegram bot to verify your email."
        )
        email_sent = await mailer.send_verification_email(email, subject, message)
        logger.info(f"Verification email sent to {email} via {MAIL_DELIVERY}")

        # Send verification email
        if email_sent:
            await update.message.reply_text(
                f"A verification code has been sent to {email}. Please enter the 6-digit code here."
            )
        else:
            await update.message.reply_text(
                "Sorry, there was an error sending the verification email. Please wait 5 mins and try again."
            )
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
