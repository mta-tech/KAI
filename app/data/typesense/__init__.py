import typesense

from app.server.config import Settings



class TypeSenseDB:
    def __init__(self, setting: Settings) -> None:
        self.client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": setting.TYPESENSE_HOST,
                        "port": setting.TYPESENSE_PORT,
                        "protocol": setting.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": setting.TYPESENSE_API_KEY,
                # "connection_timeout_seconds": setting.TYPESENSE_TIMEOUT,
            }
        )
