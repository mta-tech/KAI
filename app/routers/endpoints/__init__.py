from abc import ABC, abstractmethod

from app.data import Storage
from app.server.config import Settings


class Endpoint(ABC):
    @abstractmethod
    def __init__(self, settings: Settings, storage: Storage):
        self.settings = settings
        self.storage = storage
