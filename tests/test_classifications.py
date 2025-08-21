#!/usr/bin/env python3
"""
Tests for the Sensing Garden API classification endpoints.
This module tests both uploading and retrieving plant classifications.

## Test Coverage

### Basic Classification Tests:
- test_add_classification: Basic classification upload
- test_add_classification_with_bounding_box: Classification with bounding box
- test_add_classification_with_track_id_and_metadata: Classification with track ID and metadata
- test_add_classification_with_classification_data: Classification with detailed classification data
- test_add_classification_with_invalid_model: Classification with invalid model ID

### Location Data Tests:
- test_add_classification_with_location_only: Classification with complete location data (lat, long, alt)
- test_add_classification_with_location_no_altitude: Classification with location data without altitude
- test_add_classification_with_edge_case_location: Classification with extreme but valid coordinates

### Environment Data Tests (OLD - COMMENTED OUT):  
# - test_add_classification_with_environment_only: Classification with complete environment data
# - test_add_classification_with_partial_environment: Classification with partial environment data (subset of fields)
# - test_add_classification_with_minimal_environment_data: Classification with minimal environment data (single field)
# - test_add_classification_with_extreme_environment_values: Classification with extreme but valid environment values

### TDD Environment Data Tests (NEW - DESIGNED TO FAIL):
- test_add_classification_with_environment_tdd: TDD test for complete environment data using new "environment" schema
- test_add_classification_with_partial_environment_tdd: TDD test for partial environment data using new "environment" schema  
- test_add_classification_with_location_and_environment_tdd: TDD test for both location and environment using new "environment" schema

### Combined Data Tests:
- test_add_classification_with_location_and_environment: Classification with both location and environment data
- test_add_classification_with_all_optional_fields: Classification with all possible optional fields

### Validation Tests:
- test_add_classification_data_type_validation: Test with mixed data types (int/float validation)
- test_backward_compatibility_existing_classification: Ensure existing functionality still works

### Fetch Tests:
- test_fetch_classifications: Retrieve classifications with various filters

### Helper Functions:
- generate_test_location_data: Generate realistic location test data
- generate_test_environment_data: Generate realistic environment test data with option for partial data
"""
import argparse
import base64
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List

import requests

from .test_utils import (
    get_client,
    create_test_image,
    generate_random_confidence,
    get_random_test_name,
    TEST_FAMILIES,
    TEST_GENERA,
    TEST_SPECIES,
    print_response,
    generate_random_bounding_box,
    DEFAULT_TEST_DEVICE_ID,
    DEFAULT_TEST_MODEL_ID
)

# Helper functions for generating test data
def generate_test_location_data(include_altitude=True):
    """Generate realistic location data for testing."""
    location_data = {
        "lat": round(random.uniform(35.0, 45.0), 6),  # Realistic latitude range
        "long": round(random.uniform(-125.0, -75.0), 6)  # Realistic longitude range for US
    }
    
    if include_altitude:
        location_data["alt"] = round(random.uniform(0, 3000), 1)  # Altitude in meters
        
    return location_data

def generate_test_environment_data(partial=False):
    """Generate realistic environmental data for testing.
    
    Args:
        partial: If True, only include some fields for testing partial data scenarios
    """
    # Generate realistic PM values (PM1.0 < PM2.5 < PM4.0 < PM10.0)
    pm1p0 = round(random.uniform(5.0, 25.0), 1)
    pm2p5 = round(pm1p0 + random.uniform(5.0, 20.0), 1)
    pm4p0 = round(pm2p5 + random.uniform(5.0, 15.0), 1)
    pm10p0 = round(pm4p0 + random.uniform(5.0, 25.0), 1)
    
    env_data = {
        "pm1p0": pm1p0,
        "pm2p5": pm2p5,
        "pm4p0": pm4p0,
        "pm10p0": pm10p0,
        "ambient_humidity": round(random.uniform(20.0, 90.0), 1),  # 20-90% humidity
        "ambient_temperature": round(random.uniform(-10.0, 40.0), 1),  # -10 to 40°C
        "voc_index": random.randint(50, 500),  # VOC index 50-500
        "nox_index": random.randint(50, 300)   # NOx index 50-300
    }
    
    if partial:
        # Return only a subset of fields for partial data testing
        keys_to_keep = random.sample(list(env_data.keys()), k=random.randint(2, 5))
        env_data = {k: v for k, v in env_data.items() if k in keys_to_keep}
    
    return env_data

def test_add_classification(device_id, model_id, timestamp=None):
    success, request_timestamp = _add_classification(device_id, model_id, timestamp)
    assert success, f"Classification test failed at {request_timestamp}"

def test_add_classification_with_bounding_box(device_id, model_id, timestamp=None):
    bounding_box = generate_random_bounding_box()
    success, request_timestamp = _add_classification(device_id, model_id, timestamp, bounding_box=bounding_box)
    assert success, f"Classification with bounding_box test failed at {request_timestamp}"

def test_add_classification_with_track_id_and_metadata(device_id, model_id, timestamp=None):
    track_id = f"track-{uuid.uuid4()}"
    metadata = {"foo": "bar", "num": 123}
    print(f"\n[TEST] Sending classification with track_id: {track_id} and metadata: {metadata}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(device_id, model_id, timestamp, track_id=track_id, metadata=metadata, return_response=True, return_sent_kwargs=True)
    print(f"[TEST] Payload sent to server:\n{sent_kwargs}")
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with track_id/metadata test failed at {request_timestamp}"
    # Check response contains track_id and metadata
    assert (response_data.get("track_id") == track_id or ("data" in response_data and response_data["data"].get("track_id") == track_id)), "track_id not returned in response"
    assert (response_data.get("metadata") == metadata or ("data" in response_data and response_data["data"].get("metadata") == metadata)), f"metadata not returned or mismatched: {response_data.get('metadata')} != {metadata}"

def test_add_classification_with_classification_data(device_id, model_id, timestamp=None):
    classification_data = {
        "family": [
            {"name": "Rosaceae", "confidence": 0.95},
            {"name": "Asteraceae", "confidence": 0.78}
        ],
        "genus": [
            {"name": "Rosa", "confidence": 0.92},
            {"name": "Rubus", "confidence": 0.65}
        ],
        "species": [
            {"name": "Rosa canina", "confidence": 0.88},
            {"name": "Rosa rugosa", "confidence": 0.76}
        ]
    }
    print(f"\n[TEST] Sending classification with classification_data: {classification_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp, 
        classification_data=classification_data, 
        return_response=True, 
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with classification_data test failed at {request_timestamp}"
    # Verify classification_data is returned in response
    returned_data = response_data.get("classification_data") or response_data.get("data", {}).get("classification_data")
    assert returned_data is not None, "classification_data not returned in response"

def test_add_classification_with_location_only(device_id, model_id, timestamp=None):
    """Test classification with location data only."""
    location_data = generate_test_location_data(include_altitude=True)
    print(f"\n[TEST] Sending classification with location data: {location_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Payload sent to server:\n{sent_kwargs}")
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with location test failed at {request_timestamp}"
    # Verify location is included in the request
    assert sent_kwargs.get("location") == location_data, "location not included in request payload"
    # Verify location is returned in response
    returned_location = response_data.get("location") or response_data.get("data", {}).get("location")
    assert returned_location is not None, "location not returned in response"

def test_add_classification_with_location_no_altitude(device_id, model_id, timestamp=None):
    """Test classification with location data without altitude."""
    location_data = generate_test_location_data(include_altitude=False)
    print(f"\n[TEST] Sending classification with location data (no altitude): {location_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with location (no altitude) test failed at {request_timestamp}"
    # Verify location is included in the request without altitude
    sent_location = sent_kwargs.get("location")
    assert sent_location == location_data, "location not included correctly in request payload"
    assert "alt" not in sent_location, "altitude should not be present when not provided"

# OLD: Comment out old environment tests that use "data" structure
# def test_add_classification_with_environment_only(device_id, model_id, timestamp=None):
#     """Test classification with environment data only."""
#     environment_data = generate_test_environment_data(partial=False)
#     print(f"\n[TEST] Sending classification with environment data: {environment_data}")
#     success, request_timestamp, response_data, sent_kwargs = _add_classification(
#         device_id, model_id, timestamp,
#         environment=environment_data,
#         return_response=True,
#         return_sent_kwargs=True
#     )
#     print(f"[TEST] Payload sent to server:\n{sent_kwargs}")
#     print(f"[TEST] Full response received from server:\n{response_data}")
#     assert success, f"Classification with environment data test failed at {request_timestamp}"
#     # Verify environment_data is included in the request
#     assert sent_kwargs.get("environment") == environment_data, "environment_data not included in request payload"
#     # Verify environment_data is returned in response
#     returned_env_data = response_data.get("environment_data") or response_data.get("data", {}).get("environment_data")
#     assert returned_env_data is not None, "environment_data not returned in response"

# OLD: Comment out old environment tests that use "data" structure
# def test_add_classification_with_partial_environment(device_id, model_id, timestamp=None):
#     """Test classification with partial environment data (not all fields)."""
#     environment_data = generate_test_environment_data(partial=True)
#     print(f"\n[TEST] Sending classification with partial environment data: {environment_data}")
#     success, request_timestamp, response_data, sent_kwargs = _add_classification(
#         device_id, model_id, timestamp,
#         environment=environment_data,
#         return_response=True,
#         return_sent_kwargs=True
#     )
#     print(f"[TEST] Full response received from server:\n{response_data}")
#     assert success, f"Classification with partial environment data test failed at {request_timestamp}"
#     # Verify partial environment_data is included in the request
#     assert sent_kwargs.get("environment") == environment_data, "partial environment_data not included correctly in request payload"
#     # Verify only the sent fields are returned
#     returned_env_data = response_data.get("environment_data") or response_data.get("data", {}).get("environment_data")
#     assert returned_env_data is not None, "partial environment_data not returned in response"

# OLD: Comment out old environment tests that use "data" structure
# def test_add_classification_with_location_and_environment(device_id, model_id, timestamp=None):
#     """Test classification with both location and environment data."""
#     location_data = generate_test_location_data(include_altitude=True)
#     environment_data = generate_test_environment_data(partial=False)
#     print(f"\n[TEST] Sending classification with both location and environment data")
#     print(f"Location: {location_data}")
#     print(f"Environment: {environment_data}")
#     success, request_timestamp, response_data, sent_kwargs = _add_classification(
#         device_id, model_id, timestamp,
#         location=location_data,
#         environment=environment_data,
#         return_response=True,
#         return_sent_kwargs=True
#     )
#     print(f"[TEST] Full response received from server:\n{response_data}")
#     assert success, f"Classification with both location and environment test failed at {request_timestamp}"
#     # Verify both are included in the request
#     assert sent_kwargs.get("location") == location_data, "location not included in request payload"
#     assert sent_kwargs.get("environment") == environment_data, "environment_data not included in request payload"
#     # Verify both are returned in response
#     returned_location = response_data.get("location") or response_data.get("data", {}).get("location")
#     returned_env_data = response_data.get("environment_data") or response_data.get("data", {}).get("environment_data")
#     assert returned_location is not None, "location not returned in response"
#     assert returned_env_data is not None, "environment_data not returned in response"

def test_add_classification_with_all_optional_fields(device_id, model_id, timestamp=None):
    """Test classification with all optional fields including location, environment, bounding_box, track_id, metadata, and classification_data."""
    location_data = generate_test_location_data(include_altitude=True)
    environment_data = generate_test_environment_data(partial=False)
    bounding_box = generate_random_bounding_box()
    track_id = f"track-{uuid.uuid4()}"
    metadata = {"test_type": "comprehensive", "version": "1.0"}
    classification_data = {
        "family": [{"name": "Rosaceae", "confidence": 0.95}],
        "genus": [{"name": "Rosa", "confidence": 0.92}],
        "species": [{"name": "Rosa canina", "confidence": 0.88}]
    }
    
    print(f"\n[TEST] Sending classification with all optional fields")
    print(f"Location: {location_data}")
    print(f"Environment: {environment_data}")
    print(f"Bounding box: {bounding_box}")
    print(f"Track ID: {track_id}")
    print(f"Metadata: {metadata}")
    print(f"Classification data: {classification_data}")
    
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        environment=environment_data,
        bounding_box=bounding_box,
        track_id=track_id,
        metadata=metadata,
        classification_data=classification_data,
        return_response=True,
        return_sent_kwargs=True
    )
    
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with all optional fields test failed at {request_timestamp}"
    
    # Verify all fields are included in the request
    assert sent_kwargs.get("location") == location_data, "location not included in request payload"
    assert sent_kwargs.get("environment") == environment_data, "environment_data not included in request payload"
    assert sent_kwargs.get("bounding_box") == bounding_box, "bounding_box not included in request payload"
    assert sent_kwargs.get("track_id") == track_id, "track_id not included in request payload"
    assert sent_kwargs.get("metadata") == metadata, "metadata not included in request payload"
    assert sent_kwargs.get("classification_data") == classification_data, "classification_data not included in request payload"

def test_add_classification_with_edge_case_location(device_id, model_id, timestamp=None):
    """Test classification with edge case location data (extreme coordinates)."""
    # Test with extreme but valid coordinates
    location_data = {
        "lat": 85.0,  # Near north pole
        "long": -179.9,  # Near international date line
        "alt": 0.0  # Sea level
    }
    print(f"\n[TEST] Sending classification with edge case location data: {location_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with edge case location test failed at {request_timestamp}"
    assert sent_kwargs.get("location") == location_data, "edge case location not included correctly in request payload"

def test_add_classification_with_extreme_environment_values(device_id, model_id, timestamp=None):
    """Test classification with extreme but valid environment values."""
    # Test with extreme but realistic values
    environment_data = {
        "pm1p0": 0.1,  # Very low PM value
        "pm2p5": 500.0,  # Very high PM2.5
        "pm4p0": 600.0,  # Very high PM4.0
        "pm10p0": 1000.0,  # Very high PM10.0
        "ambient_humidity": 5.0,  # Very low humidity
        "ambient_temperature": 50.0,  # Very high temperature
        "voc_index": 1,  # Minimum VOC index
        "nox_index": 500   # High NOx index
    }
    print(f"\n[TEST] Sending classification with extreme environment values: {environment_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with extreme environment values test failed at {request_timestamp}"
    assert sent_kwargs.get("environment") == environment_data, "extreme environment values not included correctly in request payload"

def test_add_classification_with_minimal_environment_data(device_id, model_id, timestamp=None):
    """Test classification with minimal environment data (only one field)."""
    environment_data = {
        "ambient_temperature": 20.5
    }
    print(f"\n[TEST] Sending classification with minimal environment data: {environment_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with minimal environment data test failed at {request_timestamp}"
    assert sent_kwargs.get("environment") == environment_data, "minimal environment data not included correctly in request payload"

def test_add_classification_data_type_validation(device_id, model_id, timestamp=None):
    """Test classification with various data types to ensure proper handling."""
    # Test with different numeric types
    location_data = {
        "lat": 40.7128,  # float
        "long": -74,  # int (should be acceptable)
        "alt": 10.5  # float
    }
    
    environment_data = {
        "pm1p0": 15,  # int
        "pm2p5": 20.5,  # float
        "ambient_temperature": 25,  # int
        "ambient_humidity": 65.0,  # float
        "voc_index": 100,  # int (should be int type for indices)
        "nox_index": 150   # int
    }
    
    print(f"\n[TEST] Sending classification with mixed data types")
    print(f"Location (mixed int/float): {location_data}")
    print(f"Environment (mixed int/float): {environment_data}")
    
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Classification with mixed data types test failed at {request_timestamp}"
    assert sent_kwargs.get("location") == location_data, "location with mixed data types not handled correctly"
    assert sent_kwargs.get("environment") == environment_data, "environment data with mixed data types not handled correctly"

def test_backward_compatibility_existing_classification(device_id, model_id, timestamp=None):
    """Test that existing classification functionality still works without location/environment data."""
    print(f"\n[TEST] Testing backward compatibility - classification without location/environment data")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TEST] Full response received from server:\n{response_data}")
    assert success, f"Backward compatibility test failed at {request_timestamp}"
    # Verify that location and environment_data are not in the payload when not provided
    assert "location" not in sent_kwargs or sent_kwargs["location"] is None, "location should not be present when not provided"
    assert "environment_data" not in sent_kwargs or sent_kwargs["environment_data"] is None, "environment_data should not be present when not provided"

"""
=== TDD TESTS FOR ENVIRONMENT DATA ===

These tests are designed to FAIL initially to demonstrate the TDD (Test-Driven Development) approach.
They test the EXPECTED behavior after fixing the client to use the new API schema.

CURRENT ISSUE IDENTIFIED:
- Client code in classifications.py line 106 sends: payload["data"] = environment_data
- New API schema expects: payload["environment"] = environment_data

FAILING TESTS CONFIRM:
1. Environment data is not being returned by the API (even with current "data" field)
2. Location data works correctly and is returned
3. Client needs to be fixed to send "environment" field instead of "data" field

TO FIX: Change classifications.py line 106 from:
    payload["data"] = environment_data
TO:
    payload["environment"] = environment_data

After this fix, these tests should pass (assuming the backend API also supports the new schema).
"""

# NEW TDD TESTS: These tests expect the updated API schema with "environment" field
def test_add_classification_with_environment_tdd(device_id, model_id, timestamp=None):
    """TDD Test: Classification with environment data using new 'environment' schema structure.
    
    This test validates that environment data is properly sent and returned using the 'environment' parameter.
    """
    environment_data = generate_test_environment_data(partial=False)
    print(f"\n[TDD TEST] Sending classification with environment data (new schema): {environment_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TDD TEST] Payload sent to server:\n{sent_kwargs}")
    print(f"[TDD TEST] Full response received from server:\n{response_data}")
    assert success, f"TDD Classification with environment data test failed at {request_timestamp}"
    
    # Verify the client method received environment data correctly
    client_method_received_env_data = sent_kwargs.get("environment")
    assert client_method_received_env_data == environment_data, "Client method should receive environment parameter correctly"
    
    # Verify that the API returns environment data under "environment" field  
    returned_env_data = response_data.get("data", {}).get("environment")
    assert returned_env_data is not None, "environment data should be returned under 'environment' field in response"
    
    # Verify the structure matches expected field names
    expected_fields = {"ambient_temperature", "ambient_humidity", "pm1p0", "pm2p5", "pm4p0", "pm10p0", "voc_index", "nox_index"}
    actual_fields = set(returned_env_data.keys())
    assert expected_fields.issubset(actual_fields), f"Response should contain expected environment fields. Missing: {expected_fields - actual_fields}"
    
    # Verify that the sent environment data values match what was returned
    for field in environment_data:
        assert field in returned_env_data, f"Environment field '{field}' not found in response"
        assert returned_env_data[field] == environment_data[field], f"Environment field '{field}' value mismatch: expected {environment_data[field]}, got {returned_env_data[field]}"

def test_add_classification_with_partial_environment_tdd(device_id, model_id, timestamp=None):
    """TDD Test: Classification with partial environment data using new 'environment' schema.
    
    This test verifies that partial environment data is properly handled under the new schema.
    """
    environment_data = generate_test_environment_data(partial=True)
    print(f"\n[TDD TEST] Sending classification with partial environment data (new schema): {environment_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TDD TEST] Full response received from server:\n{response_data}")
    assert success, f"TDD Classification with partial environment data test failed at {request_timestamp}"
    
    # Verify client method received partial environment data correctly
    client_method_received_env_data = sent_kwargs.get("environment")
    assert client_method_received_env_data == environment_data, "Client method should receive partial environment parameter correctly"
    
    # Verify response contains partial environment data under "environment" field
    returned_env_data = response_data.get("data", {}).get("environment")
    assert returned_env_data is not None, "partial environment data should be returned under 'environment' field"
    
    # Verify only the sent fields are returned and match expected values
    sent_keys = set(environment_data.keys())
    returned_keys = set(returned_env_data.keys())
    assert sent_keys.issubset(returned_keys), f"Response should contain all sent environment fields. Missing: {sent_keys - returned_keys}"
    
    # Verify that the sent environment data values match what was returned
    for field in environment_data:
        assert field in returned_env_data, f"Partial environment field '{field}' not found in response"
        assert returned_env_data[field] == environment_data[field], f"Partial environment field '{field}' value mismatch: expected {environment_data[field]}, got {returned_env_data[field]}"

def test_add_classification_with_location_and_environment_tdd(device_id, model_id, timestamp=None):
    """TDD Test: Classification with both location and environment using new 'environment' schema.
    
    This test verifies that both location and environment data work together under the new schema.
    """
    location_data = generate_test_location_data(include_altitude=True)
    environment_data = generate_test_environment_data(partial=False)
    print(f"\n[TDD TEST] Sending classification with both location and environment (new schema)")
    print(f"Location: {location_data}")
    print(f"Environment: {environment_data}")
    success, request_timestamp, response_data, sent_kwargs = _add_classification(
        device_id, model_id, timestamp,
        location=location_data,
        environment=environment_data,
        return_response=True,
        return_sent_kwargs=True
    )
    print(f"[TDD TEST] Full response received from server:\n{response_data}")
    assert success, f"TDD Classification with location and environment test failed at {request_timestamp}"
    
    # Verify client method received both location and environment data correctly
    client_method_received_location = sent_kwargs.get("location")
    client_method_received_env_data = sent_kwargs.get("environment")
    assert client_method_received_location == location_data, "Client method should receive location parameter correctly"
    assert client_method_received_env_data == environment_data, "Client method should receive environment parameter correctly"
    
    # Verify response contains both location and environment in correct structure
    returned_location = response_data.get("data", {}).get("location")
    returned_env_data = response_data.get("data", {}).get("environment")
    assert returned_location is not None, "location should be returned in response"
    assert returned_env_data is not None, "environment data should be returned under 'environment' field"
    
    # Verify location structure and values match
    assert "lat" in returned_location and "long" in returned_location, "returned location should contain lat/long"
    for field in location_data:
        assert field in returned_location, f"Location field '{field}' not found in response"
        assert returned_location[field] == location_data[field], f"Location field '{field}' value mismatch: expected {location_data[field]}, got {returned_location[field]}"
    
    # Verify environment structure with correct field names and values
    expected_env_fields = {"ambient_temperature", "ambient_humidity", "pm1p0", "pm2p5", "pm4p0", "pm10p0", "voc_index", "nox_index"}
    actual_env_fields = set(returned_env_data.keys())
    assert expected_env_fields.issubset(actual_env_fields), f"Response environment should contain expected fields. Missing: {expected_env_fields - actual_env_fields}"
    
    # Verify that the sent environment data values match what was returned
    for field in environment_data:
        assert field in returned_env_data, f"Environment field '{field}' not found in response"
        assert returned_env_data[field] == environment_data[field], f"Environment field '{field}' value mismatch: expected {environment_data[field]}, got {returned_env_data[field]}"

def _add_classification(device_id, model_id, timestamp=None, bounding_box=None, track_id=None, metadata=None, classification_data=None, location=None, environment=None, return_response=False, return_sent_kwargs=False):
    """
    Helper function to upload a classification to the Sensing Garden API.
    
    Args:
        device_id: Device ID to use for testing
        model_id: Model ID to use for testing
        timestamp: Optional timestamp to use (defaults to current time)
        bounding_box: Optional bounding box to include
        track_id: Optional track ID to include
        metadata: Optional metadata to include
        classification_data: Optional classification data to include
        location: Optional location data to include
        environment: Optional environment data to include
        return_response: Whether to return the response data
        return_sent_kwargs: Whether to return the sent kwargs
        
    Returns:
        Tuple of (success, timestamp[, response_data][, sent_kwargs])
    """
    # Create a unique timestamp for this request to avoid DynamoDB key conflicts
    request_timestamp = timestamp or datetime.now().isoformat()
    
    # Get the client
    client = get_client()
    
    print(f"\n\nTesting CLASSIFICATION UPLOAD with device_id: {device_id}, model_id: {model_id}")
    
    try:
        # Create test image
        image_data = create_test_image()
        
        # Generate random classification data
        family = get_random_test_name(TEST_FAMILIES)
        genus = get_random_test_name(TEST_GENERA)
        species = get_random_test_name(TEST_SPECIES)
        family_confidence = generate_random_confidence()
        genus_confidence = generate_random_confidence()
        species_confidence = generate_random_confidence()
        
        # Add the classification
        kwargs = dict(
            device_id=device_id,
            model_id=model_id,
            image_data=image_data,
            family=family,
            genus=genus,
            species=species,
            family_confidence=family_confidence,
            genus_confidence=genus_confidence,
            species_confidence=species_confidence,
            timestamp=request_timestamp,
        )
        if bounding_box is not None:
            kwargs["bounding_box"] = bounding_box
        if track_id is not None:
            kwargs["track_id"] = track_id
        if metadata is not None:
            kwargs["metadata"] = metadata
        if classification_data is not None:
            kwargs["classification_data"] = classification_data
        if location is not None:
            kwargs["location"] = location
        if environment is not None:
            kwargs["environment"] = environment
        
        # Send the request
        try:
            response = client.classifications.add(**kwargs)
        except Exception as e:
            print(f"[ERROR] Exception during classification upload: {e}")
            if return_response and return_sent_kwargs:
                return (False, request_timestamp, None, kwargs)
            elif return_response:
                return (False, request_timestamp, None)
            elif return_sent_kwargs:
                return (False, request_timestamp, kwargs)
            return (False, request_timestamp)
        
        # Optionally return the response data and/or sent kwargs
        if return_response and return_sent_kwargs:
            return True, request_timestamp, response, kwargs
        elif return_response:
            return True, request_timestamp, response
        elif return_sent_kwargs:
            return True, request_timestamp, kwargs
        return True, request_timestamp
        
        print_response(response)
        print(f"\n✅ Classification upload successful!")
        success = True
        # For bounding_box test, verify it is returned (check both response_data['bounding_box'] and response_data['data']['bounding_box'])
        if bounding_box is not None:
            returned_box = None
            if "bounding_box" in response:
                returned_box = response["bounding_box"]
            elif isinstance(response, dict) and "data" in response and isinstance(response["data"], dict) and "bounding_box" in response["data"]:
                returned_box = response["data"]["bounding_box"]
            assert returned_box == bounding_box, f"bounding_box not returned or mismatched: {returned_box} != {bounding_box}"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Classification upload failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        success = False
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        success = False
    
    if return_response:
        return success, request_timestamp, response_data
    return success, request_timestamp

def test_add_classification_with_invalid_model(device_id, nonexistent_model_id, timestamp=None):
    success, request_timestamp = _add_classification_with_invalid_model(device_id, nonexistent_model_id, timestamp)
    assert success, f"Classification with random/nonexistent model_id failed at {request_timestamp}"

def _add_classification_with_invalid_model(device_id, nonexistent_model_id, timestamp=None):
    """
    Helper function to test uploading a classification with an invalid model ID.
    This should fail with an appropriate error message.
    
    Args:
        device_id: Device ID to use for testing
        nonexistent_model_id: Non-existent model ID to use for testing
        timestamp: Optional timestamp to use (defaults to current time)
        
    Returns:
        Tuple of (success, timestamp)
    """
    # Create a unique timestamp for this request
    request_timestamp = timestamp or datetime.now().isoformat()
    
    # Generate a random invalid model ID
    invalid_model_id = str(uuid.uuid4())
    
    # Get the client
    client = get_client()
    
    print(f"\n\nTesting CLASSIFICATION with invalid model_id: {invalid_model_id}")
    
    try:
        # Create test image
        image_data = create_test_image()
        
        # Generate random classification data
        family = get_random_test_name(TEST_FAMILIES)
        genus = get_random_test_name(TEST_GENERA)
        species = get_random_test_name(TEST_SPECIES)
        family_confidence = generate_random_confidence()
        genus_confidence = generate_random_confidence()
        species_confidence = generate_random_confidence()
        
        # Add the classification with invalid model ID
        response_data = client.classifications.add(
            device_id=device_id,
            model_id=invalid_model_id,
            image_data=image_data,
            family=family,
            genus=genus,
            species=species,
            family_confidence=family_confidence,
            genus_confidence=genus_confidence,
            species_confidence=species_confidence,
            timestamp=request_timestamp
        )
        print(f"✅ Classification with random/nonexistent model_id succeeded as expected!")
        print_response(response_data)
        return True, request_timestamp
    except Exception as e:
        print(f"❌ Classification upload failed: {str(e)}")
        return False, request_timestamp

def test_fetch_classifications(device_id: str, model_id: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, sort_by: Optional[str] = None, sort_desc: bool = False):
    success, data = _fetch_classifications(device_id, model_id, start_time, end_time, sort_by, sort_desc)
    assert success, f"No classifications found for device {device_id} in the specified time range. Data: {data}"

def _fetch_classifications(device_id: str, model_id: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, sort_by: Optional[str] = None, sort_desc: bool = False):
    """
    Helper function to retrieve classifications from the Sensing Garden API.
    
    Args:
        device_id: Device ID to filter by
        model_id: Optional model ID to filter by
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
    
    print(f"\n\nTesting CLASSIFICATION FETCH with device_id: {device_id}, model_id: {model_id}")
    print(f"Searching from {start_time} to {end_time}")
    
    try:
        # Use the classifications.fetch method to get classifications
        data = client.classifications.fetch(
            device_id=device_id,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            limit=10,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        # Check if we got any results
        if data.get('items') and len(data['items']) > 0:
            print(f"✅ Classification fetch successful! Found {len(data['items'])} classifications.")
            
            # Print details of each classification
            for i, classification in enumerate(data['items']):
                print(f"\nClassification {i+1}:")
                print(f"  Device ID: {classification.get('device_id')}")
                print(f"  Model ID: {classification.get('model_id')}")
                print(f"  Timestamp: {classification.get('timestamp')}")
                print(f"  Family: {classification.get('family')}")
                print(f"  Genus: {classification.get('genus')}")
                print(f"  Species: {classification.get('species')}")
                print(f"  Confidence: {classification.get('confidence')}")
                
                # Print image URL if available
                if 'image_url' in classification:
                    print(f"  Image URL: {classification.get('image_url')}")
                
                # Print metadata if available
                if 'metadata' in classification:
                    print(f"  Metadata: {classification.get('metadata')}")
            
            return True, data
        else:
            print(f"❌ No classifications found for device {device_id} in the specified time range.")
            return False, data
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Classification fetch request failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        return False, None
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        return False, None

def _add_test_classifications(
    device_id: str,
    model_id: str,
    num_classifications: int = 3
) -> bool:
    """
    Add test classifications for a device.
    
    Args:
        device_id: Device ID to use
        model_id: Model ID to use
        num_classifications: Number of classifications to add
        
    Returns:
        bool: Whether all classifications were added successfully
    """
    print(f"\nAdding {num_classifications} test classifications for device {device_id}")
    
    success = True
    for i in range(num_classifications):
        upload_success, _ = test_add_classification(
            device_id=device_id,
            model_id=model_id,
            timestamp=datetime.now().isoformat()
        )
        success = success and upload_success
    
    return success

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Sensing Garden API classification endpoints')
    parser.add_argument('--device-id', type=str, default=DEFAULT_TEST_DEVICE_ID,
                      help=f'Device ID to use for testing (default: {DEFAULT_TEST_DEVICE_ID})')
    parser.add_argument('--model-id', type=str, default=DEFAULT_TEST_MODEL_ID,
                      help=f'Model ID to use for testing (default: {DEFAULT_TEST_MODEL_ID})')
    parser.add_argument('--timestamp', type=str, help='Optional timestamp to use for testing')
    parser.add_argument('--upload', action='store_true', help='Test classification upload')
    parser.add_argument('--fetch', action='store_true', help='Test classification fetch')
    parser.add_argument('--test-invalid', action='store_true', help='Test with invalid model ID')
    parser.add_argument('--add-test-data', action='store_true', help='Add test classifications')
    parser.add_argument('--num-classifications', type=int, default=3, help='Number of test classifications to add')
    
    args = parser.parse_args()
    
    # Use provided timestamp or generate a new one
    timestamp = args.timestamp or datetime.now().isoformat()
    
    # Run the appropriate tests
    success = True
    
    # Default to running both upload and fetch if neither is specified
    run_upload = args.upload or (not args.upload and not args.fetch)
    run_fetch = args.fetch or (not args.upload and not args.fetch)
    
    # Test classification upload
    if run_upload:
        upload_success, _ = test_add_classification(args.device_id, args.model_id, timestamp)
        success &= upload_success
    
    # Test with invalid model ID if requested
    if args.test_invalid:
        invalid_success, _ = test_add_classification_with_invalid_model(args.device_id, timestamp)
        success &= invalid_success
    
    # Add test data if requested
    if args.add_test_data:
        add_success = add_test_classifications(args.device_id, args.model_id, args.num_classifications)
        success &= add_success
    
    # Test classification fetch
    if run_fetch:
        fetch_success, _ = test_fetch_classifications(args.device_id, args.model_id)
        success &= fetch_success
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
