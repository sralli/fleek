# Fleek - PilotLog Django API

A Django REST API for importing PilotLog data and exporting to ForeFlight format.

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```
   Just install and run :)
   ```

3. **Run Server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## API Endpoints

- `POST /pilotlog/api/import/` - Import PilotLog JSON data
- `POST /pilotlog/api/export/` - Export to ForeFlight CSV format  
- `GET /pilotlog/api/health/` - Health check

## Features

- Import aircraft, airports, and flight records from PilotLog JSON
- Export complete logbook to ForeFlight-compatible CSV
- Environment-based configuration
- Comprehensive logging and error handling

## Usage Example

```bash
curl -X POST http://localhost:8000/pilotlog/api/export/ \
  -H "Content-Type: application/json" \
  -d '{"output_path": "/path/to/export.csv"}'
``` 