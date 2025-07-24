from abc import ABC, abstractmethod
from typing import Any


class BaseReader(ABC):
    """Abstract base for file readers."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def read(self, file_path: str) -> Any:
        """Read file and return raw data."""
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        """Return format identifier."""
        pass


def get():
    """Runner function to get BaseReader class."""
    return BaseReader 