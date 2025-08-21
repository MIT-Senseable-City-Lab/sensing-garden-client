# New Environment and Location Functionality Tests for Classifications

## Overview

This document describes the comprehensive test suite created for the new environment and location functionality in classification calls for the Sensing Garden API.

## Changes Made

### 1. Fixed classifications.py Client Bug
- **File**: `/Users/deniz/Build/scl/sg/sensing-garden-client/sensing_garden_client/classifications.py`
- **Issue**: The `location` and `environment_data` parameters were defined in the method signature but not being added to the API request payload
- **Fix**: Updated line 106 to correctly set `payload["environment_data"]` instead of `payload["data"]`

### 2. Enhanced test_classifications.py
- **File**: `/Users/deniz/Build/scl/sg/sensing-garden-client/tests/test_classifications.py`
- **Added**: 11 new comprehensive test functions covering location and environment functionality
- **Enhanced**: Updated helper function `_add_classification` to support new parameters

### 3. Created Pytest-Compatible Test Suite
- **File**: `/Users/deniz/Build/scl/sg/sensing-garden-client/tests/test_classifications_pytest.py`
- **Purpose**: Demonstrates how to use the new test functions within a pytest framework
- **Structure**: Organized test classes for different functionality areas

## New Test Functions

### Location Data Tests
1. **test_add_classification_with_location_only**
   - Tests classification with complete location data (lat, long, alt)
   - Validates location data is included in request and response

2. **test_add_classification_with_location_no_altitude**
   - Tests classification with location data without altitude
   - Ensures altitude field is properly omitted when not provided

3. **test_add_classification_with_edge_case_location**
   - Tests with extreme but valid coordinates (near poles, international date line)
   - Validates handling of edge cases in geographic data

### Environment Data Tests
4. **test_add_classification_with_environment_only**
   - Tests classification with complete environment data
   - Validates all 8 environment fields: pm1p0, pm2p5, pm4p0, pm10p0, ambient_temperature, ambient_humidity, voc_index, nox_index

5. **test_add_classification_with_partial_environment**
   - Tests classification with partial environment data (random subset of fields)
   - Ensures partial data is handled correctly

6. **test_add_classification_with_minimal_environment_data**
   - Tests classification with minimal environment data (single field)
   - Validates minimum viable environment data scenarios

7. **test_add_classification_with_extreme_environment_values**
   - Tests with extreme but valid environment values
   - Validates handling of boundary conditions for sensor readings

### Combined Data Tests
8. **test_add_classification_with_location_and_environment**
   - Tests classification with both location and environment data
   - Ensures both data types work together correctly

9. **test_add_classification_with_all_optional_fields**
   - Tests classification with all possible optional fields
   - Comprehensive test including location, environment, bounding_box, track_id, metadata, and classification_data

### Validation Tests
10. **test_add_classification_data_type_validation**
    - Tests with mixed data types (int/float) for location and environment data
    - Validates proper data type handling

11. **test_backward_compatibility_existing_classification**
    - Ensures existing classification functionality still works without new parameters
    - Critical for maintaining backward compatibility

### Helper Functions
- **generate_test_location_data**: Generates realistic location test data with optional altitude
- **generate_test_environment_data**: Generates realistic environment test data with option for partial data

## Test Data Specifications

### Valid Location Data
```python
{
    "lat": 40.7128,      # Latitude (float)
    "long": -74.0060,    # Longitude (float) 
    "alt": 10.5          # Altitude in meters (optional float)
}
```

### Valid Environment Data
```python
{
    "pm1p0": 15.2,                  # PM1.0 µg/m³ (float)
    "pm2p5": 25.1,                  # PM2.5 µg/m³ (float)
    "pm4p0": 35.8,                  # PM4.0 µg/m³ (float)
    "pm10p0": 45.3,                 # PM10.0 µg/m³ (float)
    "ambient_temperature": 22.5,     # Temperature °C (float)
    "ambient_humidity": 65.0,        # Humidity % (float)
    "voc_index": 120,               # VOC Index (int)
    "nox_index": 95                 # NOx Index (int)
}
```

## Usage Examples

### Running Individual Tests (Standalone)
```bash
# Run specific location test
python -c "from tests.test_classifications import test_add_classification_with_location_only, DEFAULT_TEST_DEVICE_ID, DEFAULT_TEST_MODEL_ID; test_add_classification_with_location_only(DEFAULT_TEST_DEVICE_ID, DEFAULT_TEST_MODEL_ID)"

# Run specific environment test
python -c "from tests.test_classifications import test_add_classification_with_environment_only, DEFAULT_TEST_DEVICE_ID, DEFAULT_TEST_MODEL_ID; test_add_classification_with_environment_only(DEFAULT_TEST_DEVICE_ID, DEFAULT_TEST_MODEL_ID)"
```

### Running with Pytest
```bash
# Run all new classification tests
pytest tests/test_classifications_pytest.py -v

# Run specific test class
pytest tests/test_classifications_pytest.py::TestClassificationLocationFunctionality -v

# Run individual test
pytest tests/test_classifications_pytest.py::test_location_only_functionality -v
```

### Running Original Test Script
```bash
# The original test_classifications.py script still works as before
python tests/test_classifications.py --device-id test-device-2025 --model-id test-model-2025
```

## Test Coverage Summary

The new test suite provides comprehensive coverage for:

- ✅ **Location data validation**: Complete location with altitude, location without altitude, edge case coordinates
- ✅ **Environment data validation**: Complete environment data, partial data, minimal data, extreme values  
- ✅ **Combined functionality**: Both location and environment data together
- ✅ **Data type handling**: Mixed int/float values for numeric fields
- ✅ **Integration testing**: All optional fields together (location, environment, bounding_box, track_id, metadata, classification_data)
- ✅ **Backward compatibility**: Existing functionality preserved
- ✅ **Edge cases**: Boundary conditions and extreme but valid values
- ✅ **API contract validation**: Request payload and response structure verification

## Key Benefits

1. **Comprehensive Coverage**: Tests cover all combinations of location and environment data
2. **Realistic Test Data**: Uses realistic ranges for coordinates and sensor readings
3. **Edge Case Testing**: Validates handling of extreme but valid values
4. **Backward Compatibility**: Ensures existing functionality is preserved
5. **Data Type Validation**: Tests mixed int/float handling for numeric fields
6. **Integration Ready**: Works with existing test infrastructure and patterns
7. **Framework Flexible**: Can be run standalone or with pytest
8. **Well Documented**: Clear test descriptions and comprehensive documentation

## Files Modified/Created

1. **Modified**: `/Users/deniz/Build/scl/sg/sensing-garden-client/sensing_garden_client/classifications.py` - Fixed payload bug
2. **Enhanced**: `/Users/deniz/Build/scl/sg/sensing-garden-client/tests/test_classifications.py` - Added 11 new test functions
3. **Created**: `/Users/deniz/Build/scl/sg/sensing-garden-client/tests/test_classifications_pytest.py` - Pytest-compatible test suite
4. **Created**: `/Users/deniz/Build/scl/sg/sensing-garden-client/NEW_CLASSIFICATION_TESTS.md` - This documentation

The implementation follows the existing test patterns, uses the standard test device/model IDs from conftest.py, generates test images using test_utils helpers, verifies API calls succeed, and checks response structure as requested.