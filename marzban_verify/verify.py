from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import random
import string
from email.message import EmailMessage
import logging
from datetime import datetime
import os
import smtplib
import asyncio
import dns.resolver
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Store verification codes and received emails
verification_codes = {}

SMTP_PORT = 4200


class DirectMailer:
    def __init__(self, sender_domain="localhost", helo_name=None):
        self.sender_domain = sender_domain
        self.helo_name = helo_name or socket.gethostname()

    def get_mx_records(self, domain):
        """Get MX records for a domain, sorted by priority."""
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            return sorted(
                [(rdata.preference, str(rdata.exchange).rstrip(".")) for rdata in mx_records], key=lambda x: x[0]
            )
        except dns.resolver.NoAnswer:
            logger.warning(f"No MX records found for {domain}")
            # Try A record as fallback
            try:
                a_records = dns.resolver.resolve(domain, "A")
                return [(0, str(rdata)) for rdata in a_records]
            except dns.resolver.NoAnswer:
                logger.error(f"No A records found for {domain}")
                return []
        except Exception as e:
            logger.error(f"Error resolving MX records for {domain}: {e}")
            return []

    def deliver_to_mx(self, mx_host, message, rcpt_to):
        """Attempt delivery to a specific MX server."""
        try:
            with smtplib.SMTP(mx_host, 25, timeout=10) as server:
                server.set_debuglevel(1)  # Enable debug output

                # Say HELO
                server.ehlo(self.helo_name)

                # Set envelope from/to
                server.mail(message["From"])
                server.rcpt(rcpt_to)

                # Send the message
                server.data(message.as_string().encode("utf-8"))
                return True

        except (socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Connection error to {mx_host}: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error with {mx_host}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error delivering to {mx_host}: {e}")
            return False

    async def send_mail(self, from_addr, to_addr, message):
        """Send email by looking up MX records and attempting delivery."""
        # Extract domain from recipient address
        to_domain = to_addr.split("@")[1]

        # Get MX records
        mx_records = self.get_mx_records(to_domain)
        if not mx_records:
            logger.error(f"No MX or A records found for {to_domain}")
            return False

        # Try each MX in order of preference
        for preference, mx_host in mx_records:
            logger.info(f"Attempting delivery to MX {mx_host} (preference {preference})")

            if self.deliver_to_mx(mx_host, message, to_addr):
                logger.info(f"Successfully delivered to {mx_host}")
                return True

            logger.warning(f"Failed to deliver to {mx_host}, trying next MX")

        logger.error(f"All MX servers failed for {to_domain}")
        return False


mailer = DirectMailer(
    sender_domain=os.environ["DOMAIN"],  # Replace with your domain
    helo_name=os.environ["DOMAIN"],  # Replace with your SMTP hostname
)


BOT_TOKEN = os.environ["TG_BOT_TOKEN"]


def is_valid_email(email):
    """Check if email format is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def generate_verification_code():
    """Generate a 6-digit verification code."""
    return "".join(random.choices(string.digits, k=6))


async def send_verification_email(email: str, code: str):
    """Send verification email through direct MX delivery."""
    try:
        # Create the email message
        msg = EmailMessage()
        msg.set_content(
            f"Your verification code is: {code}\n\n" "Please enter this code in the Telegram bot to verify your email."
        )

        msg["Subject"] = "Email Verification Code"
        msg["From"] = f"noreply@{mailer.sender_domain}"
        msg["To"] = email
        msg["Message-ID"] = (
            f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{random.randint(1000, 9999)}@{mailer.sender_domain}>"
        )
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        # Send the message
        success = await mailer.send_mail(msg["From"], email, msg)

        if success:
            logger.info(f"Verification email sent to {email}")
            return True
        else:
            logger.error(f"Failed to send verification email to {email}")
            return False

    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    verification_codes.pop(chat_id, None)
    await update.message.reply_text("Welcome! Please send me your email address to verify it.")


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received email address."""
    email = update.message.text.strip()

    if not is_valid_email(email):
        await update.message.reply_text(
            "Invalid email format. Please enter a valid email address.\nIf you already have the code, it means that we lost it on our side and you need to request it again.\nI know, it sucks. Life is dark and full of terrors (sigh)..."
        )
        return

    if not email.endswith("@skoltech.ru"):
        await update.message.reply_text("Use your @skoltech.ru email address.")
        return

    # Generate and store verification code
    code = generate_verification_code()
    verification_codes[update.effective_chat.id] = {"email": email, "code": code}

    # Send verification email
    if await send_verification_email(email, code):
        await update.message.reply_text(
            f"A verification code has been sent to {email}. " "Please enter the 6-digit code here."
        )
    else:
        await update.message.reply_text(
            "Sorry, there was an error sending the verification email. " "Please wait 5 mins and try again."
        )


async def handle_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification code input."""
    user_code = update.message.text.strip()
    chat_id = update.effective_chat.id

    stored_code = verification_codes[chat_id]["code"]
    stored_email = verification_codes[chat_id]["email"]

    if user_code == stored_code:
        await update.message.reply_text(f"Email {stored_email} has been successfully verified!")
        # Clean up stored code
        del verification_codes[chat_id]
    else:
        await update.message.reply_text(
            "Invalid verification code. Please try again.\nCheck your spam folder.\nIf you still can't find it, restart the verification process with /start."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in verification_codes:
        await handle_email(update, context)
    else:
        await handle_verification_code(update, context)


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
