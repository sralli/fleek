import json
import re
import logging
from typing import Any, List, Dict
from .base import BaseCleaner

logger = logging.getLogger(__name__)


class PilotLogCleaner(BaseCleaner):
    """Robust PilotLog JSON data cleaner with automatic validation and fixing."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def clean(self, **kwargs) -> List[Dict]:
        """
        Clean and validate malformed JSON data from PilotLog exports.
        
        Args:
            **kwargs: raw_data - the data to clean
        """
        # Step 1: Declaration of variables
        raw_data = kwargs.get('raw_data')
        cleaned_data = list()
        json_str = str()
        
        # Step 2: Processing
        logger.info("Starting JSON cleaning and validation")
        
        # Step 2a: Handle different data types
        if isinstance(raw_data, list):
            cleaned_data = raw_data
        elif isinstance(raw_data, str):
            # Step 2b: Clean the JSON string step by step
            json_str = raw_data
            
            # Step 2c: Remove BOM and basic cleanup
            if json_str.startswith('\ufeff'):
                json_str = json_str[1:]
            json_str = json_str.strip()
            
            # Step 2d: Fix double-escaped quotes (main issue)
            if r'\"' in json_str:
                logger.info("Fixing double-escaped quotes")
                json_str = json_str.replace(r'\"', '"')
                json_str = json_str.replace(r'\\', '\\')
            
            # Step 2e: Ensure proper array structure
            if not json_str.startswith('[') and json_str.startswith('{'):
                logger.info("Adding array brackets around JSON objects")
                json_str = '[' + json_str + ']'
            
            # Step 2f: Fix trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Step 2g: Try to parse the cleaned JSON
            try:
                cleaned_data = json.loads(json_str)
                logger.info(f"Successfully parsed {len(cleaned_data)} records")
            except json.JSONDecodeError as e:
                logger.warning(f"Standard parsing failed: {e}, trying emergency parsing")
                cleaned_data = self.emergency_parse(raw_data=json_str)
        else:
            raise ValueError(f"Unexpected data type: {type(raw_data)}")
        
        # Step 3: Return
        return cleaned_data
    
    def validate(self, **kwargs) -> bool:
        """
        Validate cleaned data structure.
        
        Args:
            **kwargs: data - the data to validate
        """
        # Step 1: Declaration of variables
        data = kwargs.get('data')
        is_valid = bool()
        required_fields = ['user_id', 'table', 'guid', 'meta']
        
        # Step 2: Processing
        # Step 2a: Check basic structure
        if not data or not isinstance(data, list):
            is_valid = False
        elif len(data) == 0:
            is_valid = True  # Empty list is valid
        else:
            # Step 2b: Check required fields in first record
            is_valid = all(field in data[0] for field in required_fields)
        
        # Step 3: Return
        return is_valid
    
    def emergency_parse(self, **kwargs) -> List[Dict]:
        """
        Emergency parsing when standard JSON parsing fails.
        
        Args:
            **kwargs: raw_data - the malformed JSON string
        """
        # Step 1: Declaration of variables
        raw_data = kwargs.get('raw_data')
        objects = list()
        current_object = str()
        brace_count = int()
        in_string = bool()
        escape_next = bool()
        
        # Step 2: Processing
        logger.info("Starting emergency parsing")
        
        # Step 2a: Apply basic fixes first
        fixed_data = raw_data.replace(r'\"', '"').replace(r'\\', '\\')
        
        # Step 2b: Try simple JSON parse after basic fixes
        try:
            objects = json.loads(fixed_data)
            logger.info(f"Emergency basic fix successful: {len(objects)} records")
            return objects
        except json.JSONDecodeError:
            pass
        
        # Step 2c: Manual parsing character by character
        for char in fixed_data:
            # Step 2ci: Track string boundaries
            if char == '"' and not escape_next:
                in_string = not in_string
            elif char == '\\' and in_string:
                escape_next = True
                current_object += char
                continue
            
            # Step 2cii: Track object boundaries
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            
            current_object += char
            escape_next = False
            
            # Step 2ciii: Complete object when braces balance
            if brace_count == 0 and current_object.strip().startswith('{'):
                try:
                    obj = json.loads(current_object.strip())
                    objects.append(obj)
                    current_object = ''
                except json.JSONDecodeError:
                    # Step 2civ: Skip malformed objects
                    current_object = ''
        
        logger.info(f"Emergency parsing recovered {len(objects)} objects")
        
        # Step 3: Return
        return objects
    
    def fix_json_structure(self, **kwargs) -> str:
        """
        Fix common JSON structure issues.
        
        Args:
            **kwargs: json_str - the JSON string to fix
        """
        # Step 1: Declaration of variables
        json_str = kwargs.get('json_str', '')
        fixed_str = str()
        
        # Step 2: Processing
        # Step 2a: Basic structure fixes
        json_str = json_str.strip()
        
        # Step 2b: Handle missing array brackets
        if json_str.startswith('{') and not json_str.startswith('['):
            if '},{' in json_str:
                # Step 2bi: Multiple objects, needs array brackets
                fixed_str = '[' + json_str + ']'
            else:
                # Step 2bii: Single object, wrap in array
                fixed_str = '[' + json_str + ']'
        else:
            fixed_str = json_str
        
        # Step 2c: Fix trailing commas
        fixed_str = re.sub(r',(\s*[}\]])', r'\1', fixed_str)
        
        # Step 2d: Balance brackets if needed
        open_braces = fixed_str.count('{') - fixed_str.count('}')
        open_brackets = fixed_str.count('[') - fixed_str.count(']')
        
        if open_braces > 0:
            fixed_str += '}' * open_braces
        if open_brackets > 0:
            fixed_str += ']' * open_brackets
        
        # Step 3: Return
        return fixed_str


def get():
    """Runner function to get PilotLogCleaner class."""
    return PilotLogCleaner 