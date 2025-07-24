import logging
from typing import Dict, List
from django.db import models, transaction
from .base import BaseImporter

logger = logging.getLogger(__name__)


class DatabaseImporter(BaseImporter):
    """Database importer using Django ORM bulk operations."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Step 1: Declaration of variables
        self.batch_size = kwargs.get('batch_size', 1000)
        self.ignore_conflicts = kwargs.get('ignore_conflicts', False)
    
    def import_records(self, **kwargs) -> Dict:
        """
        Import records into database using bulk operations.
        
        Args:
            **kwargs: model_class, records
        """
        # Step 1: Declaration of variables
        model_class = kwargs.get('model_class')
        records = kwargs.get('records', [])
        created_count = int()
        error_count = int()
        instances = list()
        
        # Step 2: Processing
        # Step 2a: Create model instances
        for record in records:
            try:
                # Step 2ai: Create kwargs for model instance
                kwargs_for_model = dict()
                for key, value in record.items():
                    kwargs_for_model[key] = value
                
                # Step 2aii: Create instance using proper **kwargs pattern
                instance = model_class(**kwargs_for_model)
                instances.append(instance)
            except Exception as e:
                logger.error(f"Failed to create {model_class.__name__}: {e}")
                error_count += 1
        
        # Step 2b: Bulk create in batches
        try:
            with transaction.atomic():
                # Step 2bi: Process instances in batches
                for i in range(0, len(instances), self.batch_size):
                    batch = instances[i:i + self.batch_size]
                    # Step 2bii: Bulk create batch
                    created = model_class.objects.bulk_create(
                        batch, 
                        ignore_conflicts=self.ignore_conflicts
                    )
                    created_count += len(created)
                    
        except Exception as e:
            logger.error(f"Bulk import failed: {e}")
            raise
        
        # Step 3: Return
        return {
            'created': created_count,
            'errors': error_count
        }


def get():
    """Runner function to get DatabaseImporter class."""
    return DatabaseImporter 