import os
from cryptography.fernet import Fernet


SMTP_ENCRYPTION_KEY = os.getenv("SMTP_ENCRYPTION_KEY")

if not SMTP_ENCRYPTION_KEY:
    raise RuntimeError("No SMTP_ENCRYPTION_KEY in enviroment variables!")

try:
    fernet = Fernet(SMTP_ENCRYPTION_KEY.encode())
except Exception as e:
    raise RuntimeError("SMTP_ENCRYPTION_KEY incorrect format") from e


def encrypt_secret(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_secret(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
