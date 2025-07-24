import os
from typing import Dict, Optional


class ExportValidator:
    """Validates export requests for logbook export only."""
    
    def __init__(self):
        self.errors = []
    
    def validate_export_request(self, data: Dict) -> Dict:
        """Validate logbook export request."""
        self.errors = []
        
        output_path = self._validate_output_path(data.get('output_path'))
        
        if self.errors:
            return {
                'valid': False,
                'errors': self.errors
            }
        
        return {
            'valid': True,
            'validated_data': {
                'output_path': output_path
            }
        }
    
    def validate_import_request(self, data: Dict) -> Dict:
        """Validate import request."""
        self.errors = []
        
        file_path = self._validate_input_file(data.get('file_path'))
        table_type = self._validate_table_type(data.get('table', 'aircraft'))
        
        if self.errors:
            return {
                'valid': False,
                'errors': self.errors
            }
        
        return {
            'valid': True,
            'validated_data': {
                'file_path': file_path,
                'table': table_type
            }
        }
    
    def _validate_output_path(self, output_path: Optional[str]) -> Optional[str]:
        """Validate output file path."""
        if not output_path:
            self.errors.append("output_path is required")
            return None
        
        if not isinstance(output_path, str):
            self.errors.append("output_path must be a string")
            return None
        
        # Check if directory exists or can be created
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                self.errors.append(f"Cannot create output directory: {str(e)}")
                return None
        
        # Check file extension
        if not output_path.lower().endswith('.csv'):
            self.errors.append("output_path must end with .csv")
            return None
        
        return output_path
    
    def _validate_input_file(self, file_path: Optional[str]) -> Optional[str]:
        """Validate input file path."""
        if not file_path:
            self.errors.append("file_path is required")
            return None
        
        if not isinstance(file_path, str):
            self.errors.append("file_path must be a string")
            return None
        
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return None
        
        if not file_path.lower().endswith('.json'):
            self.errors.append("file_path must be a JSON file")
            return None
        
        return file_path
    
    def _validate_table_type(self, table_type: Optional[str]) -> Optional[str]:
        """Validate table type for import."""
        if not table_type:
            return 'aircraft'  # Default
        
        if table_type not in ['aircraft']:  # Only aircraft supported for now
            self.errors.append("table type 'aircraft' is currently supported")
            return None
        
        return table_type


def get():
    """Runner function to get ExportValidator class."""
    return ExportValidator 