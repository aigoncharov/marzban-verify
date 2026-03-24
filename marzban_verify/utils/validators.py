import re


def normalize_email(email: str) -> str:
    email = email.lower()
    local, domain = email.rsplit("@", 1)

    if "+" in local:
        local = local[: local.index("+")]

    return f"{local}@{domain}"


def is_valid_email(email):
    """Check if email format is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
