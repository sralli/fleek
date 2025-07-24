import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from .services.validators.export_validator import get as get_validator
from .services.core.export_master import get as get_export_master
from .services.core.import_master import get as get_import_master


# Individual Functionality Views
@method_decorator(csrf_exempt, name='dispatch')
class ExportFunctionalityView(View):
    """Focused view for export functionality only."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ValidatorClass = get_validator()
        ExportMasterClass = get_export_master()
        
        self.validator = ValidatorClass()
        self.export_master = ExportMasterClass()
    
    def post(self, request, **kwargs):
        """
        Handle export requests.
        
        Args:
            **kwargs: request - Django request object, additional parameters
        """
        # Step 1: Declaration of variables
        data = dict()
        validation_result = dict()
        validated = dict()
        result = dict()
        status_code = int()
        
        try:
            # Step 2: Processing
            # Step 2a: Parse request data
            data = json.loads(request.body.decode('utf-8')) if request.body else dict()
            
            # Step 2b: Validate export request
            validation_result = self.validator.validate_export_request(data)
            if not validation_result['valid']:
                return JsonResponse({
                    'success': False,
                    'errors': validation_result['errors']
                }, status=400)
            
            # Step 2c: Process export
            validated = validation_result['validated_data']
            kwargs_for_export = dict()
            kwargs_for_export['output_path'] = validated['output_path']
            result = self.export_master.export_logbook(**kwargs_for_export)
            
            # Step 2d: Determine status code
            status_code = 200 if result['success'] else 500
            
            # Step 3: Return
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, status=500)
    
    def get(self, request, **kwargs):
        """
        Export API documentation.
        
        Args:
            **kwargs: request - Django request object, additional parameters
        """
        # Step 1: Declaration of variables
        default_export_path = str()
        
        # Step 2: Processing
        # Step 2a: Get default export path from settings
        default_export_path = os.path.join(settings.PILOTLOG_EXPORT_DIR, 'logbook.csv')
        
        # Step 3: Return
        return JsonResponse({
            'functionality': 'export',
            'method': 'POST',
            'description': 'Export complete logbook in ForeFlight template format',
            'parameters': {
                'output_path': 'string (required) - Full path where CSV file will be saved'
            },
            'example_request': {
                'output_path': default_export_path
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class ImportFunctionalityView(View):
    """Focused view for import functionality only."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ValidatorClass = get_validator()
        ImportMasterClass = get_import_master()
        
        self.validator = ValidatorClass()
        self.import_master = ImportMasterClass()
    
    def post(self, request, **kwargs):
        """
        Handle import requests.
        
        Args:
            **kwargs: request - Django request object, additional parameters
        """
        # Step 1: Declaration of variables
        data = dict()
        validation_result = dict()
        validated = dict()
        kwargs_for_import = dict()
        result = dict()
        status_code = int()
        
        try:
            # Step 2: Processing
            # Step 2a: Parse request data
            data = json.loads(request.body.decode('utf-8')) if request.body else dict()
            
            # Step 2b: Validate import request
            validation_result = self.validator.validate_import_request(data)
            if not validation_result['valid']:
                return JsonResponse({
                    'success': False,
                    'errors': validation_result['errors']
                }, status=400)
            
            # Step 2c: Process import
            validated = validation_result['validated_data']
            kwargs_for_import = dict()
            kwargs_for_import['file_path'] = validated['file_path']
            result = self.import_master.import_aircraft(**kwargs_for_import)
            
            # Step 2d: Determine status code
            status_code = 200 if result['success'] else 500
            
            # Step 3: Return
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, status=500)
    
    def get(self, request, **kwargs):
        """
        Import API documentation.
        
        Args:
            **kwargs: request - Django request object, additional parameters
        """
        # Step 1: Declaration of variables
        default_import_file = str()
        
        # Step 2: Processing
        # Step 2a: Get default import file from settings
        default_import_file = settings.PILOTLOG_IMPORT_FILE
        
        # Step 3: Return
        return JsonResponse({
            'functionality': 'import',
            'method': 'POST',
            'description': 'Import aircraft data from JSON file',
            'parameters': {
                'file_path': 'string (required) - Full path to JSON file to import',
                'table': 'string (optional) - Table type: aircraft (default)'
            },
            'example_request': {
                'file_path': default_import_file,
                'table': 'aircraft'
            }
        })


class HealthFunctionalityView(View):
    """Focused view for health check functionality only."""
    
    def get(self, request, **kwargs):
        """
        Health check functionality.
        
        Args:
            **kwargs: request - Django request object, additional parameters
        """
        # Step 1: Declaration of variables
        health_data = dict()
        
        # Step 2: Processing
        # Step 2a: Build health response
        health_data = {
            'functionality': 'health',
            'status': 'healthy',
            'version': '1.0',
            'services': {
                'export_master': 'available',
                'import_master': 'available',
                'validation': 'available'
            },
            'configuration': {
                'data_dir': settings.PILOTLOG_DATA_DIR,
                'export_dir': settings.PILOTLOG_EXPORT_DIR,
                'import_file': settings.PILOTLOG_IMPORT_FILE
            }
        }
        
        # Step 3: Return
        return JsonResponse(health_data)


def get():
    """Runner function to get all views."""
    views_dict = dict()
    views_dict['ExportFunctionalityView'] = ExportFunctionalityView
    views_dict['ImportFunctionalityView'] = ImportFunctionalityView  
    views_dict['HealthFunctionalityView'] = HealthFunctionalityView
    return views_dict
