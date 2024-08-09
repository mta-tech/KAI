from abc import ABC, abstractmethod

from app.data import Storage


class Repository(ABC):
    @abstractmethod
    def __init__(self, storage: Storage):
        self.storage = storage