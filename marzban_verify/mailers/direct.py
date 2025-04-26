import os
import random
import smtplib
import socket
from datetime import datetime
from email.message import EmailMessage

import dns.resolver

from marzban_verify.utils.logging import logger


class DirectMailer:
    def __init__(self, sender_domain, hello_name, smtp_port):
        self.sender_domain = sender_domain
        self.hello_name = hello_name
        self.smtp_port = smtp_port

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
            with smtplib.SMTP(mx_host, self.smtp_port, timeout=10) as server:
                server.set_debuglevel(1)  # Enable debug output

                # Say HELO
                server.ehlo(self.hello_name)

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


async def send_verification_email(email: str, subject: str, body: str):
    """Send verification email through direct MX delivery."""
    smtp_port = 25
    if os.environ["DIRECT_MAILER_SMTP_PORT"]:
        smtp_port = int(os.environ["DIRECT_MAILER_SMTP_PORT"])

    mailer = DirectMailer(
        sender_domain=os.environ["DIRECT_MAILER_SENDER_DOMAIN"] or "localhost",  # Replace with your domain
        hello_name=os.environ["DIRECT_MAILER_HELLO_NAME"] or socket.gethostname(),  # Replace with your SMTP hostname
        smtp_port=smtp_port,
    )

    # Create the email message
    msg = EmailMessage()
    msg.set_content(body)

    msg["Subject"] = subject
    msg["From"] = f"noreply@{mailer.sender_domain}"
    msg["To"] = email
    msg["Message-ID"] = (
        f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{random.randint(1000, 9999)}@{mailer.sender_domain}>"
    )
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    # Send the message
    success = await mailer.send_mail(msg["From"], email, msg)
    return success
