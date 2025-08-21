# Sensing Garden Client

A Python client for interacting with the Sensing Garden API - a biodiversity monitoring system for automated insect detection and environmental monitoring.

## Installation

Install from PyPI:

```bash
pip install sensing_garden_client
```

## Quick Start

```python
from sensing_garden_client import SensingGardenClient

# Initialize the client
client = SensingGardenClient(
    base_url="https://your-api-endpoint.com",
    api_key="your-api-key",  # Required for POST operations
    # AWS credentials required only for video uploads:
    aws_access_key_id="your-aws-key",        # Optional
    aws_secret_access_key="your-aws-secret", # Optional
    aws_region="us-east-1"                   # Optional, defaults to us-east-1
)
```

## Features

- **Device Management**: Add, remove, and list IoT devices
- **Model Management**: Create and manage machine learning models
- **Insect Detection**: Submit and retrieve detection results with bounding boxes
- **Classification**: Submit taxonomic classifications with confidence scores and environmental context
- **Environmental Monitoring**: Record sensor data (PM levels, temperature, humidity, air quality)
- **Video Management**: Upload and manage time-lapse videos with S3 integration
- **Location Support**: GPS coordinates for spatial analysis
- **Count Operations**: Efficient counting without data retrieval
- **Pagination**: Handle large datasets with built-in pagination

## API Reference

### Device Management

```python
# Add a new device
client.add_device(device_id="pi-greenhouse-01")

# List devices with optional filtering
devices, next_token = client.get_devices(limit=50)
devices, next_token = client.get_devices(device_id="pi-greenhouse-01")

# Remove a device
client.delete_device(device_id="pi-greenhouse-01")
```

### Models

```python
# Create a model
model = client.models.create(
    model_id="yolov8-insects-v1",
    name="YOLOv8 Insect Detection",
    version="1.0.0",
    description="Trained on 10k insect images"
)

# List models
models = client.models.fetch(limit=10)
model_count = client.models.count()
```

### Detections

Submit detected insects with bounding box coordinates:

```python
with open("insect_photo.jpg", "rb") as f:
    image_data = f.read()

detection = client.detections.add(
    device_id="pi-greenhouse-01",
    model_id="yolov8-insects-v1",
    image_data=image_data,
    bounding_box=[0.15, 0.25, 0.75, 0.85],  # [x1, y1, x2, y2] as floats (0.0-1.0)
    timestamp="2024-08-21T14:30:15Z"
)

# Retrieve detections
detections = client.detections.fetch(
    device_id="pi-greenhouse-01",
    start_time="2024-08-20T06:00:00Z",
    limit=100
)
```

### Classifications

Submit taxonomic classifications with optional environmental context:

```python
classification = client.classifications.add(
    device_id="pi-greenhouse-01",
    model_id="yolov8-insects-v1",
    image_data=image_data,
    family="Nymphalidae",
    genus="Danaus",
    species="Danaus plexippus",
    family_confidence=0.95,    # Float values (0.0-1.0)
    genus_confidence=0.87,     
    species_confidence=0.82,
    timestamp="2024-08-21T16:45:30Z",
    
    # Optional: Bounding box coordinates as floats
    bounding_box=[0.2, 0.3, 0.9, 0.8],  # [x1, y1, x2, y2] normalized (0.0-1.0)
    
    # Optional: Location data
    location={
        "lat": 37.7749,
        "long": -122.4194,
        "alt": 15.2  # altitude in meters
    },
    
    # Optional: Environmental sensor data
    environment={
        "pm1p0": 12.5,              # PM1.0 particulate matter (μg/m³)
        "pm2p5": 25.3,              # PM2.5 particulate matter (μg/m³)
        "pm4p0": 35.8,              # PM4.0 particulate matter (μg/m³)
        "pm10p0": 45.2,             # PM10.0 particulate matter (μg/m³)
        "ambient_temperature": 22.3, # Temperature (°C)
        "ambient_humidity": 65.5,    # Relative humidity (%)
        "voc_index": 150,           # Volatile Organic Compounds index (integer)
        "nox_index": 75             # Nitrogen Oxides index (integer)
    },
    
    # Optional: Multiple classification candidates with confidence arrays
    classification_data={
        "family": [
            {"name": "Nymphalidae", "confidence": 0.95},
            {"name": "Pieridae", "confidence": 0.78}
        ],
        "genus": [
            {"name": "Danaus", "confidence": 0.87},
            {"name": "Heliconius", "confidence": 0.65}
        ],
        "species": [
            {"name": "Danaus plexippus", "confidence": 0.82},
            {"name": "Danaus gilippus", "confidence": 0.71}
        ]
    },
    
    # Optional: Tracking and metadata
    track_id="butterfly-track-001",
    metadata={"camera": "top", "weather": "sunny"}
)

# The classification_data parameter (added in v0.0.13) provides confidence arrays
# for multiple candidates at each taxonomic level, replacing the need for 
# individual confidence_array parameters
```

### Environmental Data

Record environmental sensor readings:

⚠️ **Known Issue:** The environment endpoint currently has an API payload mismatch. The client sends `{"data": {...}}` but the server expects `{"environment": {...}}`. This causes a `400 Bad Request: Missing required fields: environment` error. This issue is under investigation.

```python
reading = client.environment.add(
    device_id="pi-greenhouse-01",
    data={
        "pm1p0": 8.2,               # Air quality measurements
        "pm2p5": 15.7,
        "pm4p0": 22.1,
        "pm10p0": 28.5,
        "ambient_temperature": 24.5, # Climate measurements  
        "ambient_humidity": 68.2,
        "voc_index": 120,           # Chemical measurements
        "nox_index": 85
    },
    timestamp="2024-08-21T09:15:45Z",
    location={                      # Optional GPS coordinates
        "lat": 34.0522,
        "long": -118.2437
    }
)

# Retrieve environmental data
env_data = client.environment.fetch(
    device_id="pi-greenhouse-01",
    start_time="2024-08-20T08:00:00Z",
    end_time="2024-08-21T18:00:00Z"
)
```

### Videos

Upload and manage time-lapse videos (requires AWS credentials):

**Note:** The videos client is only available if AWS credentials are provided during client initialization. If credentials are missing, `client.videos` will be `None`.

```python
# Upload video file
video = client.videos.upload_video(
    device_id="pi-greenhouse-01",
    timestamp="2024-08-21T11:20:00Z",
    video_path_or_data="/path/to/timelapse.mp4",  # or raw bytes
    content_type="video/mp4",
    metadata={"duration": 300, "fps": 30}
)

# Upload with progress tracking
def progress_callback(uploaded, total, chunk):
    percent = (uploaded / total) * 100
    print(f"Upload progress: {percent:.1f}%")

video = client.videos.upload_video(
    device_id="pi-greenhouse-01",
    timestamp="2024-08-21T13:45:30Z",
    video_path_or_data=video_bytes,
    progress_callback=progress_callback
)

# List videos
videos = client.videos.fetch(device_id="pi-greenhouse-01")
```

### Data Formats

#### Bounding Boxes

**For Detections (Required):**
- Must be **lists of 4 numeric values** (int or float)
- Format: `[x1, y1, x2, y2]` where coordinates range from 0.0 to 1.0
- Example: `[0.15, 0.25, 0.75, 0.85]` represents a box from (15%, 25%) top-left to (75%, 85%) bottom-right
- Strict validation: tuples, strings, or wrong-length arrays will be rejected

**For Classifications (Optional):**
- Flexible format support for different detection systems
- Standard: `[0.1, 0.2, 0.8, 0.9]`
- Dictionary: `{"x1": 0.1, "y1": 0.2, "x2": 0.8, "y2": 0.9}`
- String: `"0.1,0.2,0.8,0.9"`
- Tuple: `(0.1, 0.2, 0.8, 0.9)`
- Custom formats accepted for integration flexibility

### Common Query Options

All fetch methods support common filtering and pagination:

```python
# Pagination
data = client.detections.fetch(limit=50, next_token="abc123")

# Time filtering
data = client.classifications.fetch(
    start_time="2024-08-20T07:30:00Z",
    end_time="2024-08-21T19:30:00Z"
)

# Sorting
data = client.environment.fetch(
    sort_by="timestamp",
    sort_desc=True  # newest first
)

# Counting without data retrieval
count = client.detections.count(device_id="pi-greenhouse-01")
```

## Configuration

### Environment Variables

```bash
export API_BASE_URL="https://your-api-endpoint.com"
export SENSING_GARDEN_API_KEY="your-api-key"
export AWS_ACCESS_KEY_ID="your-aws-key"      # For video uploads
export AWS_SECRET_ACCESS_KEY="your-aws-secret"  # For video uploads
```

```python
import os
from sensing_garden_client import SensingGardenClient

client = SensingGardenClient(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["SENSING_GARDEN_API_KEY"],
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
)
```

## Requirements

- Python 3.8+
- `requests` for HTTP communication
- `boto3` for AWS S3 video uploads (only required for video functionality)

## Troubleshooting

**ModuleNotFoundError with boto3**: Update your boto3 installation:
```bash
pip install --upgrade boto3 botocore
```

**API Key Issues**: Ensure your API key has the necessary permissions for the operations you're performing.

**AWS Credential Issues**: Video uploads require valid AWS credentials. Ensure your credentials have S3 access permissions.

## License

This project is part of the Sensing Garden biodiversity monitoring ecosystem.