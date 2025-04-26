import asyncio
import os

from exchangelib import Account, Configuration, Credentials, Mailbox, Message


async def send_verification_email(email: str, subject: str, body: str):
    """Send verification email through EWS"""
    EWS_MAIL_LOGIN = os.environ["EWS_MAIL_LOGIN"]
    EWS_MAIL_PASSWORD = os.environ["EWS_MAIL_PASSWORD"]
    EWS_MAIL_SERVER = os.environ["EWS_MAIL_SERVER"]
    EWS_MAIL_ADDRESS = os.environ["EWS_MAIL_ADDRESS"]

    creds = Credentials(username=EWS_MAIL_LOGIN, password=EWS_MAIL_PASSWORD)
    config = Configuration(server=EWS_MAIL_SERVER, credentials=creds)
    account = Account(
        primary_smtp_address=EWS_MAIL_ADDRESS,
        config=config,
        autodiscover=False,
        access_type="delegate",
    )
    message = Message(
        account=account,
        subject=subject,
        body=body,
        to_recipients=[
            Mailbox(email_address=email),
        ],
    )

    await asyncio.get_running_loop().run_in_executor(None, lambda m: m.send(), message)
    return True
