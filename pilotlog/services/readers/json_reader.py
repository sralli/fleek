import json
import logging
from .base import BaseReader

logger = logging.getLogger(__name__)


class JSONReader(BaseReader):
    """JSON file reader with error handling."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def read(self, **kwargs):
        """
        Read JSON file and return data.
        
        Args:
            **kwargs: file_path
        """
        # Step 1: Declaration of variables
        file_path = kwargs.get('file_path')
        data = None
        
        try:
            # Step 2: Processing
            # Step 2a: Read and parse JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Malformed JSON, returning raw content for cleaning")
            # Step 2b: Return raw content if JSON parsing fails
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
        
        # Step 3: Return
        return data
    
    def get_format(self) -> str:
        return "JSON"


def get():
    """Runner function to get JSONReader class."""
    return JSONReader 