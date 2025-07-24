import csv
import logging
from typing import Dict
from django.db.models import QuerySet

from .base import BaseExporter

logger = logging.getLogger(__name__)


class ForeFlightExporter(BaseExporter):
    """ForeFlight template-compliant CSV exporter."""
    
    def export(self, **kwargs) -> Dict:
        """
        Export complete logbook in ForeFlight template format.
        
        Args:
            **kwargs: aircraft_queryset, flights_queryset, output_path
        """
        # Step 1: Declaration of variables
        aircraft_queryset = kwargs.get('aircraft_queryset')
        flights_queryset = kwargs.get('flights_queryset') 
        output_path = kwargs.get('output_path')
        result = dict()
        
        try:
            # Step 2: Processing
            # Step 2a: Open CSV file for writing
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Step 2b: Write ForeFlight header structure
                writer.writerow(['ForeFlight Logbook Import'] + [''] * 58)
                writer.writerow([''] * 59)
                
                # Step 2c: Write Aircraft Table section
                self._write_aircraft_section(writer, aircraft_queryset)
                
                # Step 2d: Write empty rows between sections
                for _ in range(5):
                    writer.writerow([''] * 59)
                
                # Step 2e: Write Flights Table section
                self._write_flights_section(writer, flights_queryset)
            
            # Step 2f: Build success result
            result = {
                'success': True,
                'exported': aircraft_queryset.count() + flights_queryset.count(),
                'aircraft_count': aircraft_queryset.count(),
                'flights_count': flights_queryset.count(),
                'output': output_path,
                'message': f'Exported {aircraft_queryset.count()} aircraft and {flights_queryset.count()} flights to ForeFlight format'
            }
            
        except Exception as e:
            logger.error(f"ForeFlight export failed: {e}")
            result = {'success': False, 'error': str(e)}
        
        # Step 3: Return
        return result
    
    def get_format_name(self) -> str:
        return "ForeFlight"
    
    def _write_aircraft_section(self, writer, aircraft_queryset: QuerySet):
        """Write Aircraft Table section."""
        writer.writerow(['Aircraft Table'] + [''] * 58)
        aircraft_types = ['Text', 'Text', 'Text', 'YYYY', 'Text', 'Text', 'Text', 'Text', 
                        'Text', 'Text', 'Boolean', 'Boolean', 'Boolean', 'Boolean'] + [''] * 45
        writer.writerow(aircraft_types)
        
        # Aircraft headers
        aircraft_headers = ['AircraftID', 'EquipmentType', 'TypeCode', 'Year', 'Make', 'Model',
                          'Category', 'Class', 'GearType', 'EngineType', 'Complex', 
                          'HighPerformance', 'Pressurized', 'TAA'] + [''] * 45
        writer.writerow(aircraft_headers)
        
        # Aircraft data
        for ac in aircraft_queryset.select_related('meta'):
            row = [
                ac.meta.reference,
                f"{ac.meta.make} {ac.meta.model}",
                ac.meta.model,
                '',  # Year not in our data
                ac.meta.make,
                ac.meta.model,
                self._map_category(ac.meta.category),
                self._map_class(ac.meta.aircraft_class),
                'Tricycle',  # Default gear type
                'Piston' if ac.meta.power == 1 else 'Turbine',
                ac.meta.complex,
                ac.meta.high_perf,
                False,  # Pressurized not in our data
                ac.meta.efis
            ] + [''] * 45
            writer.writerow(row)
    
    def _write_flights_section(self, writer, flights_queryset: QuerySet):
        """Write Flights Table section."""
        writer.writerow(['Flights Table'] + [''] * 31 + ['#;type;runway;airport;comments'] + [''] * 10 + ['name;role;email'] + [''] * 14)
        
        # Flights data types row
        flights_types = ['Date', 'Text', 'Text', 'Text', 'Text', 'hhmm', 'hhmm', 'hhmm', 'hhmm', 
                       'hhmm', 'hhmm', 'Decimal', 'Decimal', 'Decimal', 'Decimal', 'Decimal', 
                       'Decimal', 'Decimal', 'Number', 'Decimal', 'Number', 'Number', 'Number', 
                       'Number', 'Number', 'Decimal', 'Decimal', 'Decimal', 'Decimal', 'Decimal', 
                       'Decimal', 'Number', 'Packed Detail', 'Packed Detail', 'Packed Detail', 
                       'Packed Detail', 'Packed Detail', 'Packed Detail', 'Decimal', 'Decimal', 
                       'Decimal', 'Decimal', 'Text', 'Text', 'Packed Detail', 'Packed Detail', 
                       'Packed Detail', 'Packed Detail', 'Packed Detail', 'Packed Detail', 
                       'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Text', 'Decimal', 
                       'Decimal', 'Number', 'Date', 'DateTime', 'Boolean', 'Text']
        writer.writerow(flights_types)
        
        # Flights headers
        flights_headers = [
            'Date', 'AircraftID', 'From', 'To', 'Route', 'TimeOut', 'TimeOff', 'TimeOn', 'TimeIn',
            'OnDuty', 'OffDuty', 'TotalTime', 'PIC', 'SIC', 'Night', 'Solo', 'CrossCountry',
            'NVG', 'NVGOps', 'Distance', 'DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs',
            'NightLandingsFullStop', 'AllLandings', 'ActualInstrument', 'SimulatedInstrument',
            'HobbsStart', 'HobbsEnd', 'TachStart', 'TachEnd', 'Holds', 'Approach1', 'Approach2',
            'Approach3', 'Approach4', 'Approach5', 'Approach6', 'DualGiven', 'DualReceived',
            'SimulatedFlight', 'GroundTraining', 'InstructorName', 'InstructorComments',
            'Person1', 'Person2', 'Person3', 'Person4', 'Person5', 'Person6', 'FlightReview',
            'Checkride', 'IPC', 'NVGProficiency', 'FAA6158', '[Text]CustomFieldName',
            '[Numeric]CustomFieldName', '[Hours]CustomFieldName', '[Counter]CustomFieldName',
            '[Date]CustomFieldName', '[DateTime]CustomFieldName', '[Toggle]CustomFieldName',
            'PilotComments'
        ]
        writer.writerow(flights_headers)
        
        # Flights data
        for flight in flights_queryset.select_related('aircraft__meta', 'departure', 'arrival'):
            row = [
                flight.flight_date.strftime('%m/%d/%Y'),
                flight.aircraft.meta.reference,
                flight.departure.icao_code,
                flight.arrival.icao_code,
                flight.route,
                '', '', '', '', '', '',  # Time fields not in our data
                self._format_decimal_time(flight.flight_time),
                self._format_decimal_time(flight.pic_time),
                self._format_decimal_time(flight.sic_time),
                self._format_decimal_time(flight.night_time),
                '',  # Solo not in our data
                self._format_decimal_time(flight.cross_country_time),
                '', '', '',  # NVG fields not in our data
                flight.day_landings,
                flight.day_landings,
                flight.night_landings,
                flight.night_landings,
                flight.day_landings + flight.night_landings,
                self._format_decimal_time(flight.instrument_time),
                '', '', '', '', '', '', '', '', '', '', '', '',  # Empty fields
                self._format_decimal_time(flight.instructor_time),
                self._format_decimal_time(flight.dual_time),
                '', '', '', '',  # More empty fields
                '', '', '', '', '', '',  # Person fields
                '', '', '', '', '',  # Boolean fields
                '', '', '', '', '', '', '',  # Custom fields
                flight.remarks
            ]
            writer.writerow(row)
    
    def _format_decimal_time(self, minutes: int) -> str:
        """Convert minutes to decimal hours for ForeFlight."""
        if not minutes:
            return ''
        return f"{minutes / 60:.1f}"
    
    def _map_category(self, category: int) -> str:
        """Map category number to ForeFlight category."""
        return {1: 'Airplane', 2: 'Helicopter', 3: 'Glider', 4: 'Balloon'}.get(category, 'Airplane')
    
    def _map_class(self, aircraft_class: int) -> str:
        """Map class number to ForeFlight class."""
        return {
            1: 'Single Engine Land', 2: 'Multi Engine Land',
            3: 'Single Engine Sea', 4: 'Multi Engine Sea'
        }.get(aircraft_class, 'Single Engine Land')


def get():
    """Runner function to get ForeFlightExporter class."""
    return ForeFlightExporter 