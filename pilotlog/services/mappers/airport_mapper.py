import logging
from typing import Dict
from .base import BaseMapper
from ...models import Airport

logger = logging.getLogger(__name__)


class AirportMapper(BaseMapper):
    """Maps PilotLog Airfield records to Django models."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # Field mapping from PilotLog to our models
    AIRPORT_FIELD_MAP = {
        'AFICAO': 'icao_code',
        'AFIATA': 'iata_code',
        'AFName': 'name',
        'Latitude': 'latitude',
        'Longitude': 'longitude'
    }
    
    AIRPORT_DEFAULTS = {
        'icao_code': 'UNKN',
        'iata_code': '',
        'name': 'Unknown Airport',
        'city': '',
        'country': '',
        'latitude': None,
        'longitude': None,
        'source_guid': ''
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
        airport_kwargs = dict()
        
        # Step 2: Processing
        # Step 2a: Initialize with defaults
        airport_kwargs = self.AIRPORT_DEFAULTS.copy()
        
        # Step 2b: Store source GUID for linking
        source_guid = source_record.get('guid', '')
        airport_kwargs['source_guid'] = source_guid
        
        # Step 2c: Map meta fields
        for source_field, target_field in self.AIRPORT_FIELD_MAP.items():
            value = meta_data.get(source_field)
            if value is not None:
                # Step 2ci: Special handling for coordinate fields
                if target_field in ['latitude', 'longitude']:
                    try:
                        # Convert from integer (degrees * 1000) to decimal degrees
                        decimal_value = float(value) / 1000.0
                        airport_kwargs[target_field] = decimal_value
                    except (ValueError, TypeError):
                        airport_kwargs[target_field] = None
                elif target_field == 'icao_code':
                    # Ensure ICAO code is valid (4 characters)
                    icao = str(value).strip().upper()
                    airport_kwargs[target_field] = icao if len(icao) == 4 else f"AP{len(Airport.objects.all()):02d}"
                elif target_field == 'iata_code':
                    # Ensure IATA code is valid (3 characters or empty)
                    iata = str(value).strip().upper()
                    airport_kwargs[target_field] = iata if len(iata) == 3 else ''
                else:
                    airport_kwargs[target_field] = value
        
        # Step 2d: Set country based on country code if available
        country_code = meta_data.get('AFCountry')
        if country_code:
            airport_kwargs['country'] = self._map_country_code(country_code)
        
        # Step 3: Return
        return {
            'airport_data': airport_kwargs
        }
    
    def _map_country_code(self, country_code: int) -> str:
        """
        Map country code to country name.
        
        Args:
            country_code: Integer country code from PilotLog
        """
        # Basic country code mapping (can be extended)
        country_map = {
            223: 'Turkey',
            840: 'United States',
            124: 'Canada',
            826: 'United Kingdom',
            276: 'Germany',
            250: 'France',
            724: 'Spain',
            380: 'Italy',
            528: 'Netherlands',
            56: 'Belgium'
        }
        return country_map.get(country_code, f'Country_{country_code}')
    
    def get_model(self):
        return Airport


def get():
    """Runner function to get AirportMapper class."""
    return AirportMapper 