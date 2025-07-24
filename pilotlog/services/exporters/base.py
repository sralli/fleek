from abc import ABC, abstractmethod
from typing import Dict
from django.db.models import QuerySet


class BaseExporter(ABC):
    """Abstract base class for data exporters."""
    
    @abstractmethod
    def export(self, aircraft_queryset: QuerySet, flights_queryset: QuerySet, output_path: str) -> Dict:
        """Export data to specified output path."""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Return format identifier."""
        pass


def get():
    """Runner function to get BaseExporter class."""
    return BaseExporter 