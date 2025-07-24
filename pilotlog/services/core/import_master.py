import logging
from typing import Dict
from django.db import transaction

from ...models import Aircraft, AircraftMeta, Airport, Flight
from ..readers.json_reader import get as get_json_reader
from ..cleaners.pilotlog_cleaner import get as get_pilotlog_cleaner
from ..mappers.aircraft_mapper import get as get_aircraft_mapper
from ..mappers.airport_mapper import get as get_airport_mapper
from ..mappers.flight_mapper import get as get_flight_mapper
from ..importers.database_importer import get as get_database_importer

logger = logging.getLogger(__name__)


class ImportMaster(object):
    """Short, focused master service for import coordination."""
    
    def __init__(self, **kwargs):
        super().__init__()
        # Step 1: Declaration of variables
        JsonReaderClass = get_json_reader()
        CleanerClass = get_pilotlog_cleaner()
        AircraftMapperClass = get_aircraft_mapper()
        AirportMapperClass = get_airport_mapper()
        FlightMapperClass = get_flight_mapper()
        ImporterClass = get_database_importer()
        
        # Step 2: Processing
        # Step 2a: Initialize service components
        self.reader = JsonReaderClass()
        self.cleaner = CleanerClass()
        self.aircraft_mapper = AircraftMapperClass()
        self.airport_mapper = AirportMapperClass()
        self.flight_mapper = FlightMapperClass()
        self.importer = ImporterClass()
    
    def import_aircraft(self, **kwargs) -> Dict:
        """
        Coordinate complete import from JSON file: airports, aircraft, flights.
        
        Args:
            **kwargs: file_path
        """
        # Step 1: Declaration of variables
        file_path = kwargs.get('file_path')
        raw_data = None
        cleaned_data = list()
        airport_count = int()
        meta_count = int()
        aircraft_count = int()
        flight_count = int()
        
        # Step 2: Processing
        try:
            # Step 2a: Read and clean data
            kwargs_for_reader = dict()
            kwargs_for_reader['file_path'] = file_path
            raw_data = self.reader.read(**kwargs_for_reader)
            
            kwargs_for_cleaner = dict()
            kwargs_for_cleaner['raw_data'] = raw_data
            cleaned_data = self.cleaner.clean(**kwargs_for_cleaner)
            
            # Step 2b: Import in correct order with transaction
            with transaction.atomic():
                # Step 2bi: Import airports first
                kwargs_for_airports = dict()
                kwargs_for_airports['cleaned_data'] = cleaned_data
                airport_count = self._import_airports(**kwargs_for_airports)
                
                # Step 2bii: Import aircraft
                kwargs_for_aircraft = dict()
                kwargs_for_aircraft['cleaned_data'] = cleaned_data
                meta_count, aircraft_count = self._import_aircraft_records(**kwargs_for_aircraft)
                
                # Step 2biii: Import flights
                kwargs_for_flights = dict()
                kwargs_for_flights['cleaned_data'] = cleaned_data
                flight_count = self._import_flights(**kwargs_for_flights)
            
        except Exception as e:
            logger.error(f"Import coordination failed: {e}")
            return {'success': False, 'error': str(e)}
        
        # Step 3: Return
        return {
            'success': True,
            'stats': {
                'airports_created': airport_count,
                'meta_created': meta_count,
                'aircraft_created': aircraft_count,
                'flights_created': flight_count
            }
        }
    
    def _import_airports(self, **kwargs) -> int:
        """
        Import airport records.
        
        Args:
            **kwargs: cleaned_data
        """
        # Step 1: Declaration of variables
        cleaned_data = kwargs.get('cleaned_data', [])
        airport_records = list()
        mapped_airports = list()
        result = dict()
        
        # Step 2: Processing
        # Step 2a: Filter airport records
        airport_records = [r for r in cleaned_data if r.get('table') in ['Airfield', 'airfield']]
        
        if not airport_records:
            return 0
        
        # Step 2b: Map airport records
        for record in airport_records:
            kwargs_for_mapper = dict()
            kwargs_for_mapper['source_record'] = record
            mapped_data = self.airport_mapper.map(**kwargs_for_mapper)
            mapped_airports.append(mapped_data['airport_data'])
        
        # Step 2c: Import airports
        kwargs_for_importer = dict()
        kwargs_for_importer['model_class'] = Airport
        kwargs_for_importer['records'] = mapped_airports
        result = self.importer.import_records(**kwargs_for_importer)
        
        # Step 3: Return
        return result['created']
    
    def _import_aircraft_records(self, **kwargs) -> tuple:
        """
        Handle two-step aircraft import process.
        
        Args:
            **kwargs: cleaned_data
        """
        # Step 1: Declaration of variables
        cleaned_data = kwargs.get('cleaned_data', [])
        aircraft_records = list()
        meta_records = list()
        created_meta = list()
        aircraft_data_list = list()
        meta_result = dict()
        aircraft_result = dict()
        
        # Step 2: Processing
        # Step 2a: Filter aircraft records
        aircraft_records = [r for r in cleaned_data if r.get('table') == 'Aircraft']
        
        if not aircraft_records:
            return 0, 0
        
        # Step 2b: Create AircraftMeta records first
        for record in aircraft_records:
            kwargs_for_mapper = dict()
            kwargs_for_mapper['source_record'] = record
            mapped_data = self.aircraft_mapper.map(**kwargs_for_mapper)
            meta_records.append(mapped_data['meta_data'])
        
        # Step 2c: Import meta records
        kwargs_for_importer = dict()
        kwargs_for_importer['model_class'] = AircraftMeta
        kwargs_for_importer['records'] = meta_records
        meta_result = self.importer.import_records(**kwargs_for_importer)
        
        # Step 2d: Get created meta objects
        created_meta = AircraftMeta.objects.order_by('-id')[:len(meta_records)]
        
        # Step 2e: Create Aircraft records linking to meta
        for i, record in enumerate(aircraft_records):
            kwargs_for_mapper = dict()
            kwargs_for_mapper['source_record'] = record
            mapped_data = self.aircraft_mapper.map(**kwargs_for_mapper)
            aircraft_data = mapped_data['aircraft_data']
            aircraft_data['meta'] = created_meta[len(meta_records) - 1 - i]  # Reverse order
            aircraft_data_list.append(aircraft_data)
        
        # Step 2f: Import aircraft records
        kwargs_for_importer = dict()
        kwargs_for_importer['model_class'] = Aircraft
        kwargs_for_importer['records'] = aircraft_data_list
        aircraft_result = self.importer.import_records(**kwargs_for_importer)
        
        # Step 3: Return
        return meta_result['created'], aircraft_result['created']
    
    def _import_flights(self, **kwargs) -> int:
        """
        Import flight records.
        
        Args:
            **kwargs: cleaned_data
        """
        # Step 1: Declaration of variables
        cleaned_data = kwargs.get('cleaned_data', [])
        flight_records = list()
        mapped_flights = list()
        guid_to_aircraft = dict()
        guid_to_airport = dict()
        result = dict()
        default_airport = None
        
        # Step 2: Processing
        # Step 2a: Filter flight records
        flight_records = [r for r in cleaned_data if r.get('table') in ['Flight', 'flight']]
        
        if not flight_records:
            return 0
        
        # Step 2b: Create default airport for missing references
        default_airport, created = Airport.objects.get_or_create(
            icao_code='UNKN',
            defaults={
                'name': 'Unknown Airport',
                'city': '',
                'country': '',
                'iata_code': '',
                'latitude': None,
                'longitude': None,
                'source_guid': 'DEFAULT'
            }
        )
        if created:
            logger.info("Created default airport for missing references")
        
        # Step 2c: Build GUID lookup tables
        # Step 2ci: Aircraft lookup
        for aircraft in Aircraft.objects.select_related('meta').all():
            guid_to_aircraft[aircraft.guid] = aircraft
        
        # Step 2cii: Airport lookup by source GUID
        for airport in Airport.objects.all():
            if airport.source_guid:
                guid_to_airport[airport.source_guid] = airport
        
        # Step 2d: Map flight records with relationships
        successful_flights = int()
        missing_aircraft = int()
        missing_airports = int()
        
        for record in flight_records:
            kwargs_for_mapper = dict()
            kwargs_for_mapper['source_record'] = record
            mapped_data = self.flight_mapper.map(**kwargs_for_mapper)
            
            flight_data = mapped_data['flight_data']
            aircraft_code = mapped_data['aircraft_code']
            departure_code = mapped_data['departure_code']
            arrival_code = mapped_data['arrival_code']
            
            # Step 2di: Link aircraft
            aircraft = guid_to_aircraft.get(aircraft_code)
            if not aircraft:
                missing_aircraft += 1
                continue
            
            # Step 2dii: Link departure airport (use default if not found)
            departure_airport = guid_to_airport.get(departure_code, default_airport)
            
            # Step 2diii: Link arrival airport (use default if not found)
            arrival_airport = guid_to_airport.get(arrival_code, default_airport)
            
            # Step 2div: Complete flight data
            flight_data['aircraft'] = aircraft
            flight_data['departure'] = departure_airport
            flight_data['arrival'] = arrival_airport
            mapped_flights.append(flight_data)
            successful_flights += 1
            
            # Track missing airports for logging
            if departure_airport == default_airport:
                missing_airports += 1
            if arrival_airport == default_airport:
                missing_airports += 1
        
        # Step 2e: Import flights
        if mapped_flights:
            kwargs_for_importer = dict()
            kwargs_for_importer['model_class'] = Flight
            kwargs_for_importer['records'] = mapped_flights
            result = self.importer.import_records(**kwargs_for_importer)
            
            logger.info(f"Flight import results:")
            logger.info(f"  Total flight records: {len(flight_records)}")
            logger.info(f"  Successfully mapped: {successful_flights}")
            logger.info(f"  Missing aircraft: {missing_aircraft}")
            logger.info(f"  Missing airport references: {missing_airports}")
            logger.info(f"  Successfully imported: {result['created']}")
            
            return result['created']
        
        # Step 3: Return
        logger.warning(f"No flights imported - {missing_aircraft} missing aircraft references")
        return 0


def get():
    """Runner function to get ImportMaster class."""
    return ImportMaster 