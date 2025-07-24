import logging
from typing import Dict
from .base import BaseMapper
from ...models import Aircraft, AircraftMeta

logger = logging.getLogger(__name__)


class AircraftMapper(BaseMapper):
    """Maps PilotLog Aircraft records to Django models."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # Field mapping from PilotLog to our models
    META_FIELD_MAP = {
        'Fin': 'fin', 'Sea': 'sea', 'TMG': 'tmg', 'Efis': 'efis', 'FNPT': 'fnpt',
        'Make': 'make', 'Run2': 'run2', 'Class': 'aircraft_class', 'Model': 'model',
        'Power': 'power', 'Seats': 'seats', 'Active': 'active', 'Kg5700': 'kg5700',
        'Rating': 'rating', 'Company': 'company', 'Complex': 'complex',
        'CondLog': 'cond_log', 'FavList': 'fav_list', 'Category': 'category',
        'HighPerf': 'high_perf', 'SubModel': 'sub_model', 'Aerobatic': 'aerobatic',
        'RefSearch': 'ref_search', 'Reference': 'reference', 'Tailwheel': 'tailwheel',
        'DefaultApp': 'default_app', 'DefaultLog': 'default_log', 'DefaultOps': 'default_ops',
        'DeviceCode': 'device_code', 'AircraftCode': 'aircraft_code',
        'DefaultLaunch': 'default_launch', 'Record_Modified': 'record_modified'
    }
    
    META_DEFAULTS = {
        'make': '', 'model': '', 'reference': '', 'company': '',
        'aircraft_class': 1, 'category': 1, 'power': 1, 'seats': 0,
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
        meta_kwargs = dict()
        aircraft_kwargs = dict()
        
        # Step 2: Processing
        # Step 2a: Map meta fields
        for source_field, target_field in self.META_FIELD_MAP.items():
            value = meta_data.get(source_field)
            if value is not None:
                meta_kwargs[target_field] = value
            elif target_field in self.META_DEFAULTS:
                meta_kwargs[target_field] = self.META_DEFAULTS[target_field]
        
        # Step 2b: Map aircraft fields
        aircraft_kwargs = {
            'user_id': source_record.get('user_id'),
            'table': source_record.get('table', 'Aircraft'),
            'guid': source_record.get('guid'),
            'platform': source_record.get('platform', 9),
            'modified': source_record.get('_modified', 0)
        }
        
        # Step 3: Return
        return {
            'aircraft_data': aircraft_kwargs,
            'meta_data': meta_kwargs
        }
    
    def get_model(self):
        return Aircraft


def get():
    """Runner function to get AircraftMapper class."""
    return AircraftMapper 