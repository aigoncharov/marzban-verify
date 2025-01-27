import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import random
import string
from email.parser import Parser
from email.policy import default
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Store verification codes and received emails
verification_codes = {}
received_emails = {}


class CustomSMTPHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        # Parse the email message
        parser = Parser(policy=default)
        email_data = parser.parsestr(envelope.content.decode("utf8"))

        # Store the received email
        for recipient in envelope.rcpt_tos:
            received_emails[recipient] = {
                "from": envelope.mail_from,
                "subject": email_data.get("subject", ""),
                "body": email_data.get_body(preferencelist=("plain",))[0].get_content(),
                "timestamp": datetime.now(),
            }
            logger.info(f"Received email for {recipient}")

        return "250 Message accepted for delivery"


class SMTPController:
    def __init__(self, handler):
        self.handler = handler
        self.controller = None

    async def start(self):
        self.controller = Controller(self.handler, hostname="127.0.0.1", port=1025)
        self.controller.start()
        logger.info(f"SMTP server started on {self.controller.hostname}:{self.controller.port}")

    def stop(self):
        if self.controller:
            self.controller.stop()
            logger.info("SMTP server stopped")


BOT_TOKEN = "your_bot_token"  # Replace with your bot token


def is_valid_email(email):
    """Check if email format is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def generate_verification_code():
    """Generate a 6-digit verification code."""
    return "".join(random.choices(string.digits, k=6))


async def send_verification_email(email: str, code: str):
    """Send verification email using the local SMTP server."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart()
        msg["From"] = "bot@localhost"
        msg["To"] = email
        msg["Subject"] = "Email Verification Code"

        body = f"Your verification code is: {code}\n\nPlease enter this code in the Telegram bot to verify your email."
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("127.0.0.1", 1025) as server:
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Welcome! Please send me your email address to verify it.")


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received email address."""
    email = update.message.text.strip()

    if not is_valid_email(email):
        await update.message.reply_text("Invalid email format. Please send a valid email address.")
        return

    # Generate and store verification code
    code = generate_verification_code()
    verification_codes[update.effective_chat.id] = {"email": email, "code": code}

    # Send verification email
    if await send_verification_email(email, code):
        await update.message.reply_text(
            f"A verification code has been sent to {email}. " "Please enter the 6-digit code here."
        )

        # Wait for the email to be received and display it (for testing)
        await asyncio.sleep(1)  # Give the SMTP server time to process
        if email in received_emails:
            email_data = received_emails[email]
            await update.message.reply_text(
                f"Debug - Received email:\n"
                f"From: {email_data['from']}\n"
                f"Subject: {email_data['subject']}\n"
                f"Body: {email_data['body']}"
            )
    else:
        await update.message.reply_text(
            "Sorry, there was an error sending the verification email. " "Please try again later."
        )


async def handle_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification code input."""
    user_code = update.message.text.strip()
    chat_id = update.effective_chat.id

    if chat_id not in verification_codes:
        await update.message.reply_text("Please send your email address first.")
        return

    stored_code = verification_codes[chat_id]["code"]
    stored_email = verification_codes[chat_id]["email"]

    if user_code == stored_code:
        await update.message.reply_text(f"Email {stored_email} has been successfully verified!")
        # Clean up stored code
        del verification_codes[chat_id]
    else:
        await update.message.reply_text("Invalid verification code. Please try again.")


async def main():
    """Start the bot and SMTP server."""
    # Start SMTP server
    smtp_handler = CustomSMTPHandler()
    smtp_controller = SMTPController(smtp_handler)
    await smtp_controller.start()

    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
                handle_email,
            )
        )
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r"^\d{6}$"), handle_verification_code)
        )

        # Start the bot
        await application.run_polling()
    finally:
        # Stop SMTP server
        smtp_controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
