import typesense

from app.core.config import Settings


class DB:
    _client = None
    @classmethod
    def _initialize_client(cls):
        setting = Settings()
        cls._client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": setting.TYPESENSE_HOST,
                        "port": setting.TYPESENSE_PORT,
                        "protocol": setting.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": setting.TYPESENSE_API_KEY,
                "connection_timeout_seconds": setting.TYPESENSE_TIMEOUT,
            }
        )

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._initialize_client()
        return cls._client
