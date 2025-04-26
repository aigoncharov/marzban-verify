from datetime import datetime

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from marzban_verify.core.verification_code_storage import verification_code_storage
from marzban_verify.utils.config import MARZBAN_ADMIN_API_TOKEN, MARZBAN_API_BASE_URL, USER_CONFIG


async def handle_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification code input."""
    user_code = update.message.text.strip()
    chat_id = update.effective_chat.id

    stored_verification_info = verification_code_storage.get(chat_id)

    assert stored_verification_info is not None

    if user_code == stored_verification_info.code:
        try:
            await update.message.reply_text("Code is correct. Creating a user...")

            user_config = USER_CONFIG
            user_config["username"] = stored_verification_info.username
            if "expire" in user_config:
                user_config["expire"] += int(datetime.now().timestamp())
            if "status" not in user_config:
                user_config["status"] = "active"

            headers = {"Authorization": f"Bearer {MARZBAN_ADMIN_API_TOKEN}"}
            async with aiohttp.ClientSession(base_url=MARZBAN_API_BASE_URL, headers=headers) as session:
                async with session.delete(f"/api/user/{stored_verification_info.username}"):
                    pass
                async with session.post(
                    "/api/user",
                    json=user_config,
                ) as resp:
                    if not resp.ok:
                        raise Exception(f"Failed to create user: {await resp.text()}")

                    body = await resp.json()
                    subscription_url = body["subscription_url"]

                    assert subscription_url is not None
                    assert subscription_url != ""

                    await update.message.reply_text(
                        f"Email has been successfully verified!\nYour subscription URL:\n\n{subscription_url}\n\nUse it in your VPN client. Also use it in the browser to see your current traffic limit."
                    )
                    # Clean up stored code
                    verification_code_storage.remove(chat_id)
        except Exception as ex:
            await update.message.reply_text(
                f"Something went wrong. Try again in 5 mins. If it does not help, reach out to support.\nError:\n{ex}"
            )
    else:
        await update.message.reply_text(
            "Invalid verification code. Please try again.\nCheck your spam folder.\nIf you still can't find it, restart the verification process with /start."
        )
