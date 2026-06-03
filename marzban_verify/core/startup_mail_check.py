import marzban_verify.mailers.direct as direct_mailer
import marzban_verify.mailers.exchange as exchange_mailer
from marzban_verify.utils.config import MAIL_DELIVERY, get_self_email
from marzban_verify.utils.logging import logger


async def send_startup_test_email() -> None:
    """Send a test email to self on startup. Raises if delivery fails."""

    if MAIL_DELIVERY == "DIRECT":
        mailer = direct_mailer
    elif MAIL_DELIVERY == "EXCHANGE":
        mailer = exchange_mailer
    else:
        raise Exception(f"Unsupported mailer {MAIL_DELIVERY}")

    self_email = get_self_email()
    subject = "marzban-verify startup self-test"
    body = "If you can read this, mail delivery is working at startup time."

    logger.info(f"Sending startup self-test email to {self_email} via {MAIL_DELIVERY}")
    sent = await mailer.send_verification_email(self_email, subject, body)
    if not sent:
        raise RuntimeError(f"Startup self-test email FAILED via {MAIL_DELIVERY} to {self_email}")
    logger.info("Startup self-test email sent successfully")
