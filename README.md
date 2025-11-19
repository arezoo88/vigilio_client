# Vigilio Client - Django REST API

A Django app that provides REST API endpoints for the Vigilio gRPC client. This app can be installed into any Django project to expose Vigilio shareholder data through REST APIs.

## Features

- Django REST Framework ViewSets with Router support
- Clean REST API endpoints for all Vigilio gRPC methods
- Excel export endpoints
- Configurable gRPC connection settings
- Full error handling for gRPC errors

## Installation

### 1. Install the package

```bash
pip install -e /path/to/vigilio_client
```

Or add to your `requirements.txt`:
```
vigilio_client @ file:///path/to/vigilio_client
```

### 2. Add to Django INSTALLED_APPS

In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',  # Required
    'vigilio_client',  # Add this
    ...
]
```

### 3. Configure gRPC Settings

Add to your `settings.py`:

```python
# Vigilio gRPC Client Settings
VIGILIO_GRPC_HOST = '127.0.0.1:50051'  # gRPC server host and port
VIGILIO_GRPC_SECURE = False  # Use secure connection (SSL/TLS)
VIGILIO_GRPC_CREDENTIALS_PATH = None  # Path to SSL credentials if secure=True
```

### 4. Include URLs

In your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('vigilio/', include('vigilio_client.urls')),
    ...
]
```

## API Endpoints

### Fund Types

- **GET** `/vigilio/fund-types/` - Get all fund types

### Shareholders

- **GET** `/vigilio/shareholders/` - List all shareholders
  - Query params: `fund_type` (optional)

- **GET** `/vigilio/shareholders/{id}/` - Get shareholder detail with chart data
  - Query params: `fund` (optional)

- **GET** `/vigilio/shareholders/summary/` - Get shareholders summary
  - Query params: `date`, `fund_type`, `search`, `ordering` (all optional)

- **GET** `/vigilio/shareholders/summary_excel/` - Export summary to Excel
  - Query params: `fund_type` (required), `date` (optional)

- **GET** `/vigilio/shareholders/{id}/for_date/` - Get shareholder for specific date
  - Query params: `date`, `fund_type` (both optional)

- **GET** `/vigilio/shareholders/{id}/excel/` - Export shareholder to Excel
  - Query params: `fund` (optional)

## Example Usage

### Using Python requests

```python
import requests

# Get fund types
response = requests.get('http://localhost:8000/vigilio/fund-types/')
fund_types = response.json()

# List shareholders
response = requests.get('http://localhost:8000/vigilio/shareholders/?fund_type=1')
shareholders = response.json()

# Get shareholder detail
response = requests.get('http://localhost:8000/vigilio/shareholders/5040/?fund=ضمان')
detail = response.json()

# Download Excel
response = requests.get('http://localhost:8000/vigilio/shareholders/5040/excel/?fund=ضمان')
with open('shareholder.xlsx', 'wb') as f:
    f.write(response.content)
```

### Using cURL

```bash
# Get fund types
curl http://localhost:8000/vigilio/fund-types/

# List shareholders with fund type filter
curl "http://localhost:8000/vigilio/shareholders/?fund_type=1"

# Get shareholder detail
curl "http://localhost:8000/vigilio/shareholders/5040/?fund=ضمان"

# Download Excel
curl "http://localhost:8000/vigilio/shareholders/5040/excel/?fund=ضمان" -o shareholder.xlsx
```

### Using Django's browsable API

Navigate to any endpoint in your browser (e.g., `http://localhost:8000/vigilio/fund-types/`) to use DRF's browsable API interface.

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (missing required parameters)
- `500` - Internal Server Error
- `503` - Service Unavailable (gRPC connection error)

Error responses include a JSON object with an `error` key:

```json
{
  "error": "gRPC Error: UNAVAILABLE - failed to connect to all addresses"
}
```

## Development

### Running Tests

```bash
python manage.py test vigilio_client
```

### Checking Available Routes

```bash
python manage.py show_urls | grep vigilio
```

## Requirements

- Python >= 3.10
- Django >= 3.2
- Django REST Framework >= 3.14
- grpcio >= 1.50.0
- protobuf >= 4.0.0

## License

Proprietary