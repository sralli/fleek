from abc import ABC, abstractmethod
from typing import Dict, List
from django.db import models


class BaseImporter(ABC):
    """Abstract base for database importers."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def import_records(self, **kwargs) -> Dict:
        """Import records into database using **kwargs."""
        pass


def get():
    """Runner function to get BaseImporter class."""
    return BaseImporter 