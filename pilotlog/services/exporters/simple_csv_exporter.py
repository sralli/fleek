import csv
import logging
from typing import Dict
from django.db.models import QuerySet

from .base import BaseExporter

logger = logging.getLogger(__name__)


class SimpleCsvExporter(BaseExporter):
    """Simple CSV exporter for basic logbook data."""
    
    def export(self, aircraft_queryset: QuerySet, flights_queryset: QuerySet, output_path: str) -> Dict:
        """Export simplified logbook data as basic CSV."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Simple combined header
                writer.writerow([
                    'Date', 'Aircraft_Registration', 'Aircraft_Type', 'From', 'To', 
                    'Flight_Time_Hours', 'PIC_Time_Hours', 'Night_Time_Hours', 'Remarks'
                ])
                
                # Flight data with aircraft info
                for flight in flights_queryset.select_related('aircraft__meta', 'departure', 'arrival'):
                    writer.writerow([
                        flight.flight_date.strftime('%Y-%m-%d'),
                        flight.aircraft.meta.reference,
                        f"{flight.aircraft.meta.make} {flight.aircraft.meta.model}",
                        flight.departure.icao_code,
                        flight.arrival.icao_code,
                        self._format_decimal_time(flight.flight_time),
                        self._format_decimal_time(flight.pic_time),
                        self._format_decimal_time(flight.night_time),
                        flight.remarks
                    ])
            
            return {
                'success': True,
                'exported': flights_queryset.count(),
                'flights_count': flights_queryset.count(),
                'output': output_path,
                'message': f'Exported {flights_queryset.count()} flights to simple CSV format'
            }
            
        except Exception as e:
            logger.error(f"Simple CSV export failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_format_name(self) -> str:
        return "Simple CSV"
    
    def _format_decimal_time(self, minutes: int) -> str:
        """Convert minutes to decimal hours."""
        if not minutes:
            return '0.0'
        return f"{minutes / 60:.1f}"


def get():
    """Runner function to get SimpleCsvExporter class."""
    return SimpleCsvExporter 