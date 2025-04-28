import json
import logging
import os

# Required

BOT_TOKEN: str = os.environ["TG_BOT_TOKEN"]
MARZBAN_ADMIN_API_TOKEN: str = os.environ["MARZBAN_ADMIN_API_TOKEN"]
MARZBAN_API_BASE_URL: str = os.environ["MARZBAN_API_BASE_URL"]
ALLOWED_EMAIL_POSTFIX: str = os.environ["ALLOWED_EMAIL_POSTFIX"]
# Values: "DIRECT", "EXCHANGE"
MAIL_DELIVERY = os.environ["MAIL_DELIVERY"]

# Optional

USER_CONFIG = {
    "data_limit": 51 * (10**9),
    "data_limit_reset_strategy": "month",
    # It is going to be added to the current date when user creates an account
    "expire": 7776000,
    "inbounds": {
        "vless": ["VLESS TCP REALITY"],
    },
    "proxies": {
        "vless": {
            "flow": "xtls-rprx-vision",
        }
    },
}
if os.environ.get("USER_CONFIG", None) is not None:
    USER_CONFIG = json.loads(os.environ["USER_CONFIG"])

LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.INFO)