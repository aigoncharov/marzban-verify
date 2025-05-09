def get_username(tgid: int, email: str):
    handle = email.split("@")[0]
    return f"{handle}_{tgid}"
