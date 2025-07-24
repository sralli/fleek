import logging
from typing import Dict
from datetime import datetime
from .base import BaseMapper
from ...models import Flight

logger = logging.getLogger(__name__)


class FlightMapper(BaseMapper):
    """Maps PilotLog Flight records to Django models."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # Field mapping from PilotLog to our models
    FLIGHT_FIELD_MAP = {
        'DateLOCAL': 'flight_date',
        'minTOTAL': 'flight_time',
        'minPIC': 'pic_time', 
        'minSIC': 'sic_time',
        'minDUAL': 'dual_time',
        'minINSTR': 'instructor_time',
        'minIFR': 'instrument_time',
        'minNIGHT': 'night_time',
        'minXC': 'cross_country_time',
        'LdgDay': 'day_landings',
        'LdgNight': 'night_landings',
        'Remarks': 'remarks',
        'Route': 'route',
        'Record_Modified': 'record_modified'
    }
    
    FLIGHT_DEFAULTS = {
        'flight_time': 0,
        'pic_time': 0,
        'sic_time': 0,
        'dual_time': 0,
        'instructor_time': 0,
        'instrument_time': 0,
        'night_time': 0,
        'cross_country_time': 0,
        'day_landings': 0,
        'night_landings': 0,
        'remarks': '',
        'route': '',
        'record_modified': 0
    }
    
    def map(self, **kwargs) -> Dict:
        """
        Map source record to target model fields.
        
        Args:
            **kwargs: source_record
        """
        # Step 1: Declaration of variables
        source_record = kwargs.get('source_record')
        meta_data = source_record.get('meta', {})
        flight_kwargs = dict()
        
        # Step 2: Processing
        # Step 2a: Map basic flight fields
        flight_kwargs = {
            'user_id': source_record.get('user_id'),
            'guid': source_record.get('guid'),
            'platform': source_record.get('platform', 9),
            'record_modified': source_record.get('_modified', 0)
        }
        
        # Step 2b: Map meta fields
        for source_field, target_field in self.FLIGHT_FIELD_MAP.items():
            value = meta_data.get(source_field)
            if value is not None:
                # Step 2bi: Special handling for date field
                if target_field == 'flight_date':
                    try:
                        # Convert YYYY-MM-DD string to date
                        flight_kwargs[target_field] = datetime.strptime(str(value), '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        # Default to today if date parsing fails
                        flight_kwargs[target_field] = datetime.now().date()
                else:
                    flight_kwargs[target_field] = value
            elif target_field in self.FLIGHT_DEFAULTS:
                flight_kwargs[target_field] = self.FLIGHT_DEFAULTS[target_field]
        
        # Step 2c: Store aircraft and airport codes for later linking
        aircraft_code = meta_data.get('AircraftCode')
        departure_code = meta_data.get('DepCode') 
        arrival_code = meta_data.get('ArrCode')
        
        # Step 3: Return
        return {
            'flight_data': flight_kwargs,
            'aircraft_code': aircraft_code,
            'departure_code': departure_code,
            'arrival_code': arrival_code
        }
    
    def get_model(self):
        return Flight


def get():
    """Runner function to get FlightMapper class."""
    return FlightMapper 