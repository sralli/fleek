from abc import ABC, abstractmethod
from typing import Any, List, Dict


class BaseCleaner(ABC):
    """Abstract base for data cleaners."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def clean(self, **kwargs) -> List[Dict]:
        """Clean and preprocess raw data using **kwargs."""
        pass
    
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """Validate cleaned data structure using **kwargs."""
        pass


def get():
    """Runner function to get BaseCleaner class."""
    return BaseCleaner 