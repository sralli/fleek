import logging
from typing import Dict
from django.db import models

from ...models import Aircraft, Flight
from ..exporters.foreflight_exporter import get as get_foreflight_exporter

logger = logging.getLogger(__name__)


class ExportMaster(object):
    """Short, focused master service for export coordination."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Step 1: Declaration of variables
        ForeFlightExporterClass = get_foreflight_exporter()
        
        # Step 2: Processing
        # Step 2a: Initialize default exporter
        self.default_exporter = ForeFlightExporterClass()
    
    def export_logbook(self, **kwargs) -> Dict:
        """
        Coordinate logbook export using specified or default exporter.
        
        Args:
            **kwargs: output_path, exporter (optional)
        """
        # Step 1: Declaration of variables
        output_path = kwargs.get('output_path')
        exporter = kwargs.get('exporter')
        aircraft_qs = None
        flights_qs = None
        result = dict()
        
        try:
            # Step 2: Processing
            # Step 2a: Select exporter
            exporter = exporter or self.default_exporter
            
            # Step 2b: Get querysets
            aircraft_qs = self._get_aircraft_queryset()
            flights_qs = self._get_flights_queryset()
            
            # Step 2c: Export data
            kwargs_for_export = dict()
            kwargs_for_export['aircraft_queryset'] = aircraft_qs
            kwargs_for_export['flights_queryset'] = flights_qs
            kwargs_for_export['output_path'] = output_path
            result = exporter.export(**kwargs_for_export)
            
        except Exception as e:
            logger.error(f"Export coordination failed: {e}")
            result = {'success': False, 'error': str(e)}
        
        # Step 3: Return
        return result
    
    def _get_aircraft_queryset(self) -> models.QuerySet:
        """Get optimized aircraft queryset."""
        return Aircraft.objects.select_related('meta').all()
    
    def _get_flights_queryset(self) -> models.QuerySet:
        """Get optimized flights queryset."""
        return Flight.objects.select_related('aircraft__meta', 'departure', 'arrival').all()


def get():
    """Runner function to get ExportMaster class."""
    return ExportMaster 