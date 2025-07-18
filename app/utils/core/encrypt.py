from cryptography.fernet import Fernet

# from app.server.config import Settings


class FernetEncrypt:
    def __init__(self):
        from app.server.config import Settings
        settings = Settings()
        self.fernet_key = Fernet(settings.ENCRYPT_KEY)

    def encrypt(self, input: str) -> str:
        if not input:
            return ""
        return self.fernet_key.encrypt(input.encode()).decode("utf-8")

    def decrypt(self, input: str) -> str:
        if input == "":
            return ""
        return self.fernet_key.decrypt(input).decode("utf-8")
