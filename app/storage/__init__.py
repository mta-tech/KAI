import typesense

from app.core.config import Settings


class DB:
    _client = None

    @classmethod
    def _initialize_client(cls):
        cls._client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": Settings.TYPESENSE_HOST,
                        "port": Settings.TYPESENSE_PORT,
                        "protocol": Settings.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": Settings.TYPESENSE_API_KEY,
                "connection_timeout_seconds": Settings.TYPESENSE_TIMEOUT,
            }
        )

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._initialize_client()
        return cls._client
