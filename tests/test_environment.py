#!/usr/bin/env python3
"""
Tests for the Sensing Garden API environment endpoints.
This module tests both uploading and retrieving environmental readings.
"""
import argparse
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List

import requests

from .test_utils import (
    get_client,
    print_response,
    DEFAULT_TEST_DEVICE_ID
)

def test_add_environment(device_id, timestamp=None):
    """Test basic environmental reading submission."""
    success, request_timestamp = _add_environment(device_id, timestamp)
    assert success, f"Environment test failed at {request_timestamp}"

def test_add_environment_with_altitude(device_id, timestamp=None):
    """Test environmental reading submission with optional altitude in location."""
    success, request_timestamp = _add_environment(device_id, timestamp, include_altitude=True)
    assert success, f"Environment with altitude test failed at {request_timestamp}"

def test_add_environment_without_location(device_id, timestamp=None):
    """Test environmental reading submission without location data."""
    success, request_timestamp = _add_environment(device_id, timestamp, include_location=False)
    assert success, f"Environment without location test failed at {request_timestamp}"

def test_fetch_environment(device_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None, sort_by: Optional[str] = None, sort_desc: bool = False):
    """Test fetching environmental readings with filters."""
    success, data = _fetch_environment(device_id, start_time, end_time, sort_by, sort_desc)
    assert success, f"No environmental readings found for device {device_id} in the specified time range. Data: {data}"

def _add_environment(device_id, timestamp=None, include_altitude=False, include_location=True):
    """
    Helper function to upload an environmental reading to the Sensing Garden API.
    
    Args:
        device_id: Device ID to use for testing
        timestamp: Optional timestamp to use (defaults to current time)
        include_altitude: Whether to include altitude in location data
        include_location: Whether to include location data at all
        
    Returns:
        Tuple of (success, timestamp)
    """
    # Create a unique timestamp for this request to avoid DynamoDB key conflicts
    request_timestamp = timestamp or datetime.now().isoformat()
    
    # Get the client
    client = get_client()
    
    print(f"\n\nTesting ENVIRONMENT UPLOAD with device_id: {device_id}")
    if not include_location:
        print("Testing without location data")
    elif include_altitude:
        print("Including altitude in location data")
    
    try:
        # Generate location data if needed
        location_data = None
        if include_location:
            location_data = {
                "lat": round(random.uniform(35.0, 45.0), 6),  # Realistic latitude range
                "long": round(random.uniform(-125.0, -75.0), 6)  # Realistic longitude range for US
            }
            
            if include_altitude:
                location_data["alt"] = round(random.uniform(0, 3000), 1)  # Altitude in meters
        
        # Generate realistic PM values (PM1.0 < PM2.5 < PM4.0 < PM10.0)
        pm1p0 = round(random.uniform(5.0, 25.0), 1)
        pm2p5 = round(pm1p0 + random.uniform(5.0, 20.0), 1)
        pm4p0 = round(pm2p5 + random.uniform(5.0, 15.0), 1)
        pm10p0 = round(pm4p0 + random.uniform(5.0, 25.0), 1)
        
        environmental_data = {
            "pm1p0": pm1p0,
            "pm2p5": pm2p5,
            "pm4p0": pm4p0,
            "pm10p0": pm10p0,
            "ambient_humidity": round(random.uniform(20.0, 90.0), 1),  # 20-90% humidity
            "ambient_temperature": round(random.uniform(-10.0, 40.0), 1),  # -10 to 40°C
            "voc_index": random.randint(50, 500),  # VOC index 50-500
            "nox_index": random.randint(50, 300)   # NOx index 50-300
        }
        
        if location_data:
            print(f"Location: {location_data}")
        else:
            print("Location: Not provided")
        print(f"Environmental data: {environmental_data}")
        
        # Add the environmental reading
        if location_data:
            response_data = client.environment.add(
                device_id=device_id,
                data=environmental_data,
                timestamp=request_timestamp,
                location=location_data
            )
        else:
            response_data = client.environment.add(
                device_id=device_id,
                data=environmental_data,
                timestamp=request_timestamp
            )
        
        print_response(response_data)
        print(f"\n✅ Environment upload successful!")
        return True, request_timestamp
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Environment upload failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        return False, request_timestamp
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        return False, request_timestamp

def _fetch_environment(
    device_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Helper function to retrieve environmental readings from the Sensing Garden API.
    
    Args:
        device_id: Device ID to filter by
        start_time: Optional start time for filtering (ISO-8601)
        end_time: Optional end time for filtering (ISO-8601)
        sort_by: Optional attribute to sort by
        sort_desc: Whether to sort in descending order
        
    Returns:
        Tuple of (success, response data)
    """
    if not start_time:
        # If no specific start_time provided, use a time range from beginning of 2023
        start_time = datetime(2023, 1, 1).isoformat()
    
    if not end_time:
        # If no specific end_time provided, use current time
        end_time = datetime.now().isoformat()
    
    # Get the client
    client = get_client()
    
    print(f"\n\nTesting ENVIRONMENT FETCH with device_id: {device_id}")
    print(f"Searching from {start_time} to {end_time}")
    
    try:
        # Use the environment.fetch method to get environmental readings
        data = client.environment.fetch(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            limit=10,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        # Check if we got any results
        if data.get('items') and len(data['items']) > 0:
            print(f"✅ Environment fetch successful! Found {len(data['items'])} environmental readings.")
            
            # Print details of each environmental reading
            for i, reading in enumerate(data['items']):
                print(f"\nEnvironmental Reading {i+1}:")
                print(f"  Device ID: {reading.get('device_id')}")
                print(f"  Timestamp: {reading.get('timestamp')}")
                
                # Print location data
                if 'location' in reading:
                    location = reading['location']
                    print(f"  Location:")
                    print(f"    Latitude: {location.get('lat')}")
                    print(f"    Longitude: {location.get('long')}")
                    if 'alt' in location:
                        print(f"    Altitude: {location.get('alt')} m")
                
                # Print environmental data
                if 'data' in reading:
                    env_data = reading['data']
                    print(f"  Environmental Data:")
                    print(f"    PM1.0: {env_data.get('pm1p0')} µg/m³")
                    print(f"    PM2.5: {env_data.get('pm2p5')} µg/m³")
                    print(f"    PM4.0: {env_data.get('pm4p0')} µg/m³")
                    print(f"    PM10.0: {env_data.get('pm10p0')} µg/m³")
                    print(f"    Temperature: {env_data.get('ambient_temperature')}°C")
                    print(f"    Humidity: {env_data.get('ambient_humidity')}%")
                    print(f"    VOC Index: {env_data.get('voc_index')}")
                    print(f"    NOx Index: {env_data.get('nox_index')}")
                
                # Print metadata if available
                if 'metadata' in reading:
                    print(f"  Metadata: {reading.get('metadata')}")
            
            return True, data
        else:
            print(f"❌ No environmental readings found for device {device_id} in the specified time range.")
            return False, data
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Environment fetch request failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        return False, None
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        return False, None

def add_test_environmental_readings(
    device_id: str,
    num_readings: int = 3
) -> bool:
    """
    Add test environmental readings for a device.
    
    Args:
        device_id: Device ID to use
        num_readings: Number of environmental readings to add
        
    Returns:
        bool: Whether all readings were added successfully
    """
    print(f"\nAdding {num_readings} test environmental readings for device {device_id}")
    
    success = True
    for i in range(num_readings):
        # Vary timestamps slightly to avoid conflicts
        timestamp = (datetime.now() + timedelta(seconds=i)).isoformat()
        upload_success, _ = _add_environment(
            device_id=device_id,
            timestamp=timestamp,
            include_altitude=(i % 2 == 0)  # Include altitude for every other reading
        )
        success = success and upload_success
    
    return success

if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Sensing Garden API environment endpoints')
    parser.add_argument('--device-id', type=str, default=DEFAULT_TEST_DEVICE_ID,
                      help=f'Device ID to use for testing (default: {DEFAULT_TEST_DEVICE_ID})')
    parser.add_argument('--timestamp', type=str, help='Optional timestamp to use for testing')
    parser.add_argument('--upload', action='store_true', help='Test environment upload')
    parser.add_argument('--fetch', action='store_true', help='Test environment fetch')
    parser.add_argument('--with-altitude', action='store_true', help='Test with altitude in location')
    parser.add_argument('--add-test-data', action='store_true', help='Add test environmental readings')
    parser.add_argument('--num-readings', type=int, default=3, help='Number of test readings to add')
    
    args = parser.parse_args()
    
    # Use provided timestamp or generate a new one
    timestamp = args.timestamp or datetime.now().isoformat()
    
    # Run the appropriate tests
    success = True
    
    # Default to running both upload and fetch if neither is specified
    run_upload = args.upload or (not args.upload and not args.fetch and not args.add_test_data)
    run_fetch = args.fetch or (not args.upload and not args.fetch and not args.add_test_data)
    
    # Test environment upload
    if run_upload:
        upload_success, _ = test_add_environment(args.device_id, timestamp)
        success &= upload_success
    
    # Test with altitude if requested
    if args.with_altitude:
        altitude_success, _ = test_add_environment_with_altitude(args.device_id, timestamp)
        success &= altitude_success
    
    # Add test data if requested
    if args.add_test_data:
        add_success = add_test_environmental_readings(args.device_id, args.num_readings)
        success &= add_success
    
    # Test environment fetch
    if run_fetch:
        fetch_success, _ = test_fetch_environment(args.device_id)
        success &= fetch_success
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)