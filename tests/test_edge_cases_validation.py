"""
Edge case tests for parameter validation and type requirements.

This module tests various edge cases to validate that the client properly
handles different data types, validates parameters, and provides appropriate
error messages for invalid inputs.
"""

import pytest
import io
from unittest.mock import Mock, patch
from sensing_garden_client import SensingGardenClient


@pytest.fixture
def mock_client():
    """Create a mock sensing garden client for testing."""
    return SensingGardenClient(
        base_url="https://test-api.com",
        api_key="test-key"
    )


@pytest.fixture
def sample_image_data():
    """Sample image data for testing."""
    return b"fake_image_data_12345"


class TestBoundingBoxValidation:
    """Test bounding box format validation edge cases."""
    
    def test_bounding_box_float_list_valid(self, mock_client, sample_image_data):
        """Test that float bounding box values work correctly."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with proper float values
            bbox = [0.1, 0.2, 0.8, 0.9]
            result = mock_client.detections.add(
                device_id="test-device",
                model_id="test-model", 
                image_data=sample_image_data,
                bounding_box=bbox,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Verify the call was made correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            # Arguments are (endpoint, payload)
            endpoint = args[0]
            payload = args[1]
            assert endpoint == "detections"
            assert payload["bounding_box"] == bbox
    
    def test_bounding_box_int_list_behavior(self, mock_client, sample_image_data):
        """Test behavior with integer bounding box values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with integer values (should work, may be coerced to float)
            bbox = [0, 0, 1, 1]  # integers instead of floats
            result = mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=bbox,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Verify the call was made (integers are valid)
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["bounding_box"] == bbox
    
    def test_bounding_box_mixed_types(self, mock_client, sample_image_data):
        """Test bounding box with mixed int/float types."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with mixed int/float values
            bbox = [0, 0.2, 1, 0.9]  # mixed types
            result = mock_client.detections.add(
                device_id="test-device", 
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=bbox,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Should work fine with mixed types
            mock_post.assert_called_once()
    
    def test_bounding_box_wrong_length(self, mock_client, sample_image_data):
        """Test that wrong length bounding boxes are rejected."""
        # Test too few values
        with pytest.raises(ValueError, match="bounding_box must be a list of 4 float values"):
            mock_client.detections.add(
                device_id="test-device",
                model_id="test-model", 
                image_data=sample_image_data,
                bounding_box=[0.1, 0.2, 0.8],  # only 3 values
                timestamp="2024-08-21T12:00:00Z"
            )
        
        # Test too many values
        with pytest.raises(ValueError, match="bounding_box must be a list of 4 float values"):
            mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=[0.1, 0.2, 0.8, 0.9, 0.5],  # 5 values
                timestamp="2024-08-21T12:00:00Z"
            )
    
    def test_bounding_box_wrong_type(self, mock_client, sample_image_data):
        """Test that non-list bounding boxes are rejected."""
        # Test tuple (should fail since code checks for list specifically)
        with pytest.raises(ValueError, match="bounding_box must be a list of 4 float values"):
            mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=(0.1, 0.2, 0.8, 0.9),  # tuple instead of list
                timestamp="2024-08-21T12:00:00Z"
            )
        
        # Test string
        with pytest.raises(ValueError, match="bounding_box must be a list of 4 float values"):
            mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box="0.1,0.2,0.8,0.9",  # string
                timestamp="2024-08-21T12:00:00Z"
            )
    
    def test_bounding_box_string_values(self, mock_client, sample_image_data):
        """Test bounding box with string values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with string values that could be converted
            bbox = ["0.1", "0.2", "0.8", "0.9"]
            result = mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=bbox,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Should work (client doesn't validate types, just list and length)
            mock_post.assert_called_once()
    
    def test_bounding_box_out_of_range(self, mock_client, sample_image_data):
        """Test bounding box with out of range values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with values outside 0.0-1.0 range (should still pass client validation)
            bbox = [-0.1, 0.2, 1.2, 0.9]  # negative and > 1.0
            result = mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=bbox,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Client doesn't validate ranges, only format
            mock_post.assert_called_once()
    
    def test_classifications_bounding_box_optional(self, mock_client, sample_image_data):
        """Test that bounding box is optional for classifications."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test without bounding box - should work
            result = mock_client.classifications.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            
            # None values should not be included in the payload
            assert "bounding_box" not in payload


class TestConfidenceScoreTypes:
    """Test confidence score type flexibility."""
    
    def test_confidence_float_values(self, mock_client, sample_image_data):
        """Test confidence scores as float values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.classifications.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus", 
                family_confidence=0.95,  # float
                genus_confidence=0.87,   # float
                species_confidence=0.82, # float
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["family_confidence"] == 0.95
            assert payload["genus_confidence"] == 0.87
            assert payload["species_confidence"] == 0.82
    
    def test_confidence_string_values(self, mock_client, sample_image_data):
        """Test confidence scores as string values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.classifications.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence="0.95",  # string
                genus_confidence="0.87",   # string  
                species_confidence="0.82", # string
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["family_confidence"] == "0.95"
            assert payload["genus_confidence"] == "0.87"
            assert payload["species_confidence"] == "0.82"
    
    def test_confidence_mixed_types(self, mock_client, sample_image_data):
        """Test mixing float and string confidence scores."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.classifications.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,    # float
                genus_confidence="0.87",   # string
                species_confidence=0.82,   # float
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["family_confidence"] == 0.95
            assert payload["genus_confidence"] == "0.87"
            assert payload["species_confidence"] == 0.82
    
    def test_confidence_edge_values(self, mock_client, sample_image_data):
        """Test edge case confidence values."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test boundary values
            test_cases = [
                (0.0, 0.0, 0.0),     # minimum
                (1.0, 1.0, 1.0),     # maximum
                (-0.1, 1.1, 0.5),    # out of range
                (0, 1, 0.5),         # integers
            ]
            
            for family_conf, genus_conf, species_conf in test_cases:
                mock_post.reset_mock()
                result = mock_client.classifications.add(
                    device_id="test-device",
                    model_id="test-model",
                    image_data=sample_image_data,
                    family="Nymphalidae",
                    genus="Danaus",
                    species="Danaus plexippus",
                    family_confidence=family_conf,
                    genus_confidence=genus_conf,
                    species_confidence=species_conf,
                    timestamp="2024-08-21T12:00:00Z"
                )
                
                # Client should accept all values (no validation)
                mock_post.assert_called_once()


class TestEnvironmentDataValidation:
    """Test environment data validation edge cases."""
    
    def test_environment_all_required_fields(self, mock_client):
        """Test environment data with all required fields."""
        complete_data = {
            "pm1p0": 8.2,
            "pm2p5": 15.7,
            "pm4p0": 22.1,
            "pm10p0": 28.5,
            "ambient_temperature": 24.5,
            "ambient_humidity": 68.2,
            "voc_index": 120,
            "nox_index": 85
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.environment.add(
                device_id="test-device",
                data=complete_data,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
    
    def test_environment_missing_required_fields(self, mock_client):
        """Test environment data with missing required fields."""
        incomplete_data = {
            "pm1p0": 8.2,
            "pm2p5": 15.7,
            # missing pm4p0, pm10p0, ambient_temperature, ambient_humidity, voc_index, nox_index
        }
        
        with pytest.raises(ValueError, match="data must contain all required keys"):
            mock_client.environment.add(
                device_id="test-device",
                data=incomplete_data,
                timestamp="2024-08-21T12:00:00Z"
            )
    
    def test_environment_partial_fields_specific_missing(self, mock_client):
        """Test specific missing fields are identified in error."""
        partial_data = {
            "pm1p0": 8.2,
            "pm2p5": 15.7,
            "pm4p0": 22.1,
            "pm10p0": 28.5,
            "ambient_temperature": 24.5,
            # missing: ambient_humidity, voc_index, nox_index
        }
        
        with pytest.raises(ValueError) as exc_info:
            mock_client.environment.add(
                device_id="test-device",
                data=partial_data,
                timestamp="2024-08-21T12:00:00Z"
            )
        
        error_msg = str(exc_info.value)
        assert "Missing:" in error_msg
        assert "ambient_humidity" in error_msg
        assert "voc_index" in error_msg
        assert "nox_index" in error_msg
    
    def test_environment_extra_fields_allowed(self, mock_client):
        """Test that extra fields in environment data are allowed."""
        data_with_extra = {
            "pm1p0": 8.2,
            "pm2p5": 15.7,
            "pm4p0": 22.1,
            "pm10p0": 28.5,
            "ambient_temperature": 24.5,
            "ambient_humidity": 68.2,
            "voc_index": 120,
            "nox_index": 85,
            # Extra fields
            "pressure": 1013.25,
            "wind_speed": 5.2,
            "custom_sensor": 42.0
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.environment.add(
                device_id="test-device",
                data=data_with_extra,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Should accept extra fields
            mock_post.assert_called_once()
    
    def test_environment_wrong_data_type(self, mock_client):
        """Test environment data with wrong data types."""
        # Test non-dict data
        with pytest.raises(ValueError, match="data must be a dictionary"):
            mock_client.environment.add(
                device_id="test-device",
                data="not a dict",
                timestamp="2024-08-21T12:00:00Z"
            )
        
        # Test list instead of dict
        with pytest.raises(ValueError, match="data must be a dictionary"):
            mock_client.environment.add(
                device_id="test-device",
                data=[1, 2, 3, 4],
                timestamp="2024-08-21T12:00:00Z"
            )
    
    def test_environment_string_values(self, mock_client):
        """Test environment data with string values for numbers."""
        string_data = {
            "pm1p0": "8.2",        # string instead of float
            "pm2p5": "15.7", 
            "pm4p0": "22.1",
            "pm10p0": "28.5",
            "ambient_temperature": "24.5",
            "ambient_humidity": "68.2",
            "voc_index": "120",
            "nox_index": "85"
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Should work (client doesn't validate value types, only presence)
            result = mock_client.environment.add(
                device_id="test-device",
                data=string_data,
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()


class TestLocationDataValidation:
    """Test location data validation edge cases."""
    
    def test_location_with_altitude(self, mock_client):
        """Test location data with altitude."""
        complete_env_data = {
            "pm1p0": 8.2, "pm2p5": 15.7, "pm4p0": 22.1, "pm10p0": 28.5,
            "ambient_temperature": 24.5, "ambient_humidity": 68.2,
            "voc_index": 120, "nox_index": 85
        }
        
        location_with_alt = {
            "lat": 40.7128,
            "long": -74.0060,
            "alt": 10.5
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=location_with_alt
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["location"] == location_with_alt
    
    def test_location_without_altitude(self, mock_client):
        """Test location data without altitude."""
        complete_env_data = {
            "pm1p0": 8.2, "pm2p5": 15.7, "pm4p0": 22.1, "pm10p0": 28.5,
            "ambient_temperature": 24.5, "ambient_humidity": 68.2,
            "voc_index": 120, "nox_index": 85
        }
        
        location_no_alt = {
            "lat": 40.7128,
            "long": -74.0060
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=location_no_alt
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["location"] == location_no_alt
    
    def test_location_missing_required_keys(self, mock_client):
        """Test location data missing required lat/long."""
        complete_env_data = {
            "pm1p0": 8.2, "pm2p5": 15.7, "pm4p0": 22.1, "pm10p0": 28.5,
            "ambient_temperature": 24.5, "ambient_humidity": 68.2,
            "voc_index": 120, "nox_index": 85
        }
        
        # Missing longitude
        location_no_long = {
            "lat": 40.7128,
            "alt": 10.5
        }
        
        with pytest.raises(ValueError, match="location must contain 'lat' and 'long' keys"):
            mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=location_no_long
            )
        
        # Missing latitude
        location_no_lat = {
            "long": -74.0060,
            "alt": 10.5
        }
        
        with pytest.raises(ValueError, match="location must contain 'lat' and 'long' keys"):
            mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=location_no_lat
            )
    
    def test_location_wrong_type(self, mock_client):
        """Test location data with wrong type."""
        complete_env_data = {
            "pm1p0": 8.2, "pm2p5": 15.7, "pm4p0": 22.1, "pm10p0": 28.5,
            "ambient_temperature": 24.5, "ambient_humidity": 68.2,
            "voc_index": 120, "nox_index": 85
        }
        
        # Test string location
        with pytest.raises(ValueError, match="location must be a dictionary"):
            mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location="40.7128,-74.0060"
            )
        
        # Test list location
        with pytest.raises(ValueError, match="location must be a dictionary"):
            mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=[40.7128, -74.0060]
            )
    
    def test_location_extra_fields_allowed(self, mock_client):
        """Test location data with extra fields."""
        complete_env_data = {
            "pm1p0": 8.2, "pm2p5": 15.7, "pm4p0": 22.1, "pm10p0": 28.5,
            "ambient_temperature": 24.5, "ambient_humidity": 68.2,
            "voc_index": 120, "nox_index": 85
        }
        
        location_extra = {
            "lat": 40.7128,
            "long": -74.0060,
            "alt": 10.5,
            "accuracy": 5.0,
            "source": "GPS",
            "timestamp": "2024-08-21T12:00:00Z"
        }
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.environment.add(
                device_id="test-device",
                data=complete_env_data,
                timestamp="2024-08-21T12:00:00Z",
                location=location_extra
            )
            
            # Should work with extra fields
            mock_post.assert_called_once()
    
    def test_classifications_location_flexible(self, mock_client, sample_image_data):
        """Test that classifications location parameter is more flexible."""
        location_variations = [
            {"lat": 40.7128, "long": -74.0060},  # standard
            {"lat": 40.7128, "long": -74.0060, "alt": 10.5},  # with altitude
            {"latitude": 40.7128, "longitude": -74.0060},  # different keys
            {"x": 40.7128, "y": -74.0060},  # custom format
        ]
        
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            for location in location_variations:
                mock_post.reset_mock()
                result = mock_client.classifications.add(
                    device_id="test-device",
                    model_id="test-model",
                    image_data=sample_image_data,
                    family="Nymphalidae",
                    genus="Danaus",
                    species="Danaus plexippus",
                    family_confidence=0.95,
                    genus_confidence=0.87,
                    species_confidence=0.82,
                    timestamp="2024-08-21T12:00:00Z",
                    location=location
                )
                
                # Classifications don't validate location format
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                payload = args[1]
                assert payload["location"] == location


class TestClassificationBoundingBoxTypes:
    """Test that classification bounding box accepts diverse types."""
    
    def test_classifications_bounding_box_any_type_validation(self, mock_client, sample_image_data):
        """Test classifications accepts Any type for bounding box - comprehensive test."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test with different bounding box types that would fail in detections
            test_cases = [
                # Standard detection format
                [0.1, 0.2, 0.8, 0.9],  
                
                # Dictionary formats
                {"x1": 0.1, "y1": 0.2, "x2": 0.8, "y2": 0.9},  
                {"left": 0.1, "top": 0.2, "right": 0.8, "bottom": 0.9},
                {"x": 0.1, "y": 0.2, "width": 0.7, "height": 0.7},
                
                # Tuple format (not allowed in detections) 
                (0.1, 0.2, 0.8, 0.9),
                
                # String formats
                "0.1,0.2,0.8,0.9",
                "custom_bbox_format",
                
                # Wrong lengths (not allowed in detections)
                [0.1, 0.2, 0.8],  # too short
                [0.1, 0.2, 0.8, 0.9, 0.5],  # too long
                
                # Complex objects
                {"format": "yolo", "coordinates": [0.5, 0.6, 0.7, 0.8]},
                None,  # explicitly None
            ]
            
            for i, bbox in enumerate(test_cases):
                mock_post.reset_mock()
                result = mock_client.classifications.add(
                    device_id=f"test-device-{i}",
                    model_id="test-model",
                    image_data=sample_image_data,
                    family="Nymphalidae",
                    genus="Danaus", 
                    species="Danaus plexippus",
                    family_confidence=0.95,
                    genus_confidence=0.87,
                    species_confidence=0.82,
                    timestamp="2024-08-21T12:00:00Z",
                    bounding_box=bbox
                )
                
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                payload = args[1]
                
                if bbox is None:
                    assert "bounding_box" not in payload
                else:
                    assert payload["bounding_box"] == bbox


class TestParameterTypesAndCoercion:
    """Test parameter type coercion behavior."""
    
    def test_device_id_type_handling(self, mock_client, sample_image_data):
        """Test device_id parameter with different types."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test integer device ID
            result = mock_client.detections.add(
                device_id=12345,  # integer
                model_id="test-model",
                image_data=sample_image_data,
                bounding_box=[0.1, 0.2, 0.8, 0.9],
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["device_id"] == 12345
    
    def test_model_id_type_handling(self, mock_client, sample_image_data):
        """Test model_id parameter with different types."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            # Test integer model ID
            result = mock_client.detections.add(
                device_id="test-device",
                model_id=42,  # integer
                image_data=sample_image_data,
                bounding_box=[0.1, 0.2, 0.8, 0.9],
                timestamp="2024-08-21T12:00:00Z"
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            assert payload["model_id"] == 42
    
    def test_timestamp_format_flexibility(self, mock_client, sample_image_data):
        """Test timestamp parameter with different formats."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            timestamp_formats = [
                "2024-08-21T12:00:00Z",           # standard ISO
                "2024-08-21T12:00:00.000Z",       # with milliseconds
                "2024-08-21T12:00:00+00:00",      # with timezone
                "2024-08-21T12:00:00",            # without timezone
                "2024-08-21 12:00:00",            # space separator
                1692619200,                       # unix timestamp
                "invalid-timestamp",              # invalid format
            ]
            
            for timestamp in timestamp_formats:
                mock_post.reset_mock()
                result = mock_client.detections.add(
                    device_id="test-device",
                    model_id="test-model",
                    image_data=sample_image_data,
                    bounding_box=[0.1, 0.2, 0.8, 0.9],
                    timestamp=timestamp
                )
                
                # Client doesn't validate timestamp format
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                payload = args[1]
                assert payload["timestamp"] == timestamp


class TestNullAndEmptyValues:
    """Test behavior with null and empty values."""
    
    def test_optional_parameters_none(self, mock_client, sample_image_data):
        """Test optional parameters set to None."""
        with patch.object(mock_client._base_client, 'post') as mock_post:
            mock_post.return_value = {"status": "success"}
            
            result = mock_client.classifications.add(
                device_id="test-device",
                model_id="test-model",
                image_data=sample_image_data,
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                timestamp="2024-08-21T12:00:00Z",
                bounding_box=None,          # explicitly None
                track_id=None,              # explicitly None
                metadata=None,              # explicitly None
                location=None,              # explicitly None
                environment=None            # explicitly None
            )
            
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            payload = args[1]
            # Check that required fields have expected values  
            assert payload["device_id"] == "test-device"
            assert payload["model_id"] == "test-model" 
            assert payload["family"] == "Nymphalidae"
            
            # None values should not be included in the payload
            assert "bounding_box" not in payload
            assert "track_id" not in payload
            assert "metadata" not in payload
            assert "location" not in payload
            assert "environment" not in payload
    
    def test_empty_image_data(self, mock_client):
        """Test behavior with empty image data."""
        # Empty image data should raise ValueError
        with pytest.raises(ValueError, match="image_data cannot be empty"):
            mock_client.detections.add(
                device_id="test-device",
                model_id="test-model",
                image_data=b"",  # empty bytes
                bounding_box=[0.1, 0.2, 0.8, 0.9],
                timestamp="2024-08-21T12:00:00Z"
            )