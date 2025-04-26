import random
import string
from dataclasses import dataclass


@dataclass
class VerificationInfo:
    username: str
    code: str


class VerificationCodeStorage:
    def __init__(self):
        # { [chat_id: str]: VerificationInfo }
        self._verification_codes: dict[str, VerificationInfo] = {}

    def generate(self, chat_id, username):
        code = "".join(random.choices(string.digits, k=6))
        self._verification_codes[chat_id] = VerificationInfo(username=username, code=code)
        return code

    def get(self, chat_id):
        return self._verification_codes.get(chat_id, None)

    def remove(self, chat_id):
        self._verification_codes.pop(chat_id, None)


verification_code_storage = VerificationCodeStorage()
