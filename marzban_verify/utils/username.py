def get_username(tgid: int, email: str):
    handle = email.split("@")[0]
    handle = "".join(c for c in handle if c.isalnum())
    return f"{handle}_{tgid}"
