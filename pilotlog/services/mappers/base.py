from abc import ABC, abstractmethod
from typing import Dict
from django.db import models


class BaseMapper(ABC):
    """Abstract base for data mappers."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def map(self, **kwargs) -> Dict:
        """Map source record to target model fields using **kwargs."""
        pass
    
    @abstractmethod
    def get_model(self) -> models.Model:
        """Return target Django model class."""
        pass


def get():
    """Runner function to get BaseMapper class."""
    return BaseMapper 