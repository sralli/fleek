# PilotLog Import/Export System

## Architecture Overview

**Clean, modular system following SOLID principles with `get()` runner functions:**

```
pilotlog/services/
├── readers/         # File format readers (JSON, CSV, XML)
│   ├── base.py      # Abstract BaseReader + get()
│   └── json_reader.py # JSONReader + get()
├── cleaners/        # Data validation & preprocessing  
│   ├── base.py      # Abstract BaseCleaner + get()
│   └── pilotlog_cleaner.py # PilotLogCleaner + get()
├── mappers/         # Source → Django model mapping
│   ├── base.py      # Abstract BaseMapper + get()
│   └── aircraft_mapper.py # AircraftMapper + get()
├── importers/       # Database operations
│   ├── base.py      # Abstract BaseImporter + get()
│   └── database_importer.py # DatabaseImporter + get()
└── orchestrators/   # Main workflow coordination
    └── pilotlog_importer.py # PilotLogImporter + get()
```

## Usage

### **Import Aircraft Data**
```bash
python manage.py import_pilotlog --file Data/import-pilotlog_mcc.json --table aircraft
```

### **Programmatic Usage with get() Pattern**
```python
# Import using get() runner functions
from pilotlog.services.orchestrators.pilotlog_importer import get as get_importer

ImporterClass = get_importer()
importer = ImporterClass()
result = importer.import_aircraft('/path/to/data.json')
print(f"Created {result['stats']['aircraft_created']} aircraft records")

# Individual service components
from pilotlog.services.readers.json_reader import get as get_reader
from pilotlog.services.cleaners.pilotlog_cleaner import get as get_cleaner
from pilotlog.services.mappers.aircraft_mapper import get as get_mapper

ReaderClass = get_reader()
CleanerClass = get_cleaner()
MapperClass = get_mapper()

reader = ReaderClass()
cleaner = CleanerClass()
mapper = MapperClass()
```

## Design Decisions

### **1. Single Responsibility + get() Pattern**
- Each service class has one job
- Every class accessible through `get()` runner function
- Easy to test and maintain
- Clear separation of concerns

### **2. Strategy Pattern with get() Access**
- Pluggable readers for different formats
- Easy to add CSV, XML, etc. readers
- Consistent interface across formats
- All accessible via `get()` functions

### **3. Two-Step Import for Related Models**
- Create `AircraftMeta` first, then `Aircraft`
- Handles foreign key dependencies
- Uses Django's `bulk_create()` for performance

### **4. Concise Code with get() Standard**
- Removed excessive step comments
- Added required `get()` functions to all classes
- Focused on readability over verbosity
- Pythonic patterns throughout

## Adding New Formats

### **New Reader (e.g., CSV)**
```python
# pilotlog/services/readers/csv_reader.py
from .base import BaseReader

class CSVReader(BaseReader):
    def read(self, file_path: str):
        # CSV parsing logic
        pass
    
    def get_format(self) -> str:
        return "CSV"

def get():
    """Runner function to get CSVReader class."""
    return CSVReader
```

### **New Table Type (e.g., Pilot)**
```python
# pilotlog/services/mappers/pilot_mapper.py
from .base import BaseMapper
from ...models import Pilot

class PilotMapper(BaseMapper):
    def map(self, source_record: Dict) -> Dict:
        # Mapping logic
        pass
    
    def get_model(self):
        return Pilot

def get():
    """Runner function to get PilotMapper class."""
    return PilotMapper
```

## Service Components

### **Readers** 📖
- **Purpose**: Handle different file formats
- **Interface**: `read(file_path)`, `get_format()`
- **Implementation**: JSONReader with malformed JSON handling
- **Access**: Via `get()` function

### **Cleaners** 🧹
- **Purpose**: Validate and preprocess raw data
- **Interface**: `clean(raw_data)`, `validate(data)`
- **Implementation**: PilotLogCleaner fixes JSON issues
- **Access**: Via `get()` function

### **Mappers** 🗺️
- **Purpose**: Transform source data to Django model format
- **Interface**: `map(source_record)`, `get_model()`
- **Implementation**: AircraftMapper handles PascalCase → snake_case
- **Access**: Via `get()` function

### **Importers** 💾
- **Purpose**: Perform database operations
- **Interface**: `import_records(model_class, records)`
- **Implementation**: DatabaseImporter with bulk operations
- **Access**: Via `get()` function

### **Orchestrators** 🎯
- **Purpose**: Coordinate complete workflows
- **Interface**: `import_aircraft(file_path)`
- **Implementation**: PilotLogImporter manages full pipeline
- **Access**: Via `get()` function

## Error Handling

- **Fail Fast**: Stop on critical errors
- **Detailed Logging**: Track what failed and why
- **Partial Success**: Continue processing other records
- **Graceful Degradation**: Handle malformed JSON

## Performance Considerations

- **Bulk Operations**: Use Django's `bulk_create()`
- **Batching**: Process in configurable batch sizes
- **Memory Efficient**: Stream large files when needed
- **Transaction Safety**: Atomic operations

## Testing Strategy

Each component can be tested independently using `get()`:

```python
def test_aircraft_mapper():
    MapperClass = get_mapper()
    mapper = MapperClass()
    source = {'user_id': 123, 'table': 'Aircraft', 'meta': {...}}
    result = mapper.map(source)
    assert 'aircraft_data' in result
    assert 'meta_data' in result

def test_json_reader():
    ReaderClass = get_reader()
    reader = ReaderClass()
    data = reader.read('/path/to/test.json')
    assert data is not None
```

## Interview Highlights

### **Architecture Strengths** 🏗️
- **SOLID Principles**: Single responsibility per class
- **Strategy Pattern**: Pluggable components
- **get() Pattern**: Consistent access method
- **Extensibility**: Easy to add new formats/tables

### **Technical Excellence** ⚡
- **Performance**: Bulk operations, batching
- **Error Handling**: Comprehensive logging
- **Code Quality**: Concise, readable, maintainable
- **Django Integration**: Proper ORM usage

### **Senior Developer Approach** 👨‍💼
- **Planning**: Clear architecture before coding
- **Modularity**: Independent, testable components
- **Standards**: Consistent get() pattern throughout
- **Documentation**: Clear interfaces and examples 