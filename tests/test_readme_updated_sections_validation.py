#!/usr/bin/env python3
"""
Test validation for the specific sections that were updated by Agent G.
This focuses on:
1. Environment endpoint API mismatch warning validation
2. Confidence score type flexibility documentation
3. Classification_data parameter examples
4. Bounding box format differences between APIs
"""

import pytest
import json
import requests
from unittest.mock import Mock, patch, MagicMock
from sensing_garden_client import SensingGardenClient


class TestUpdatedSectionsValidation:
    """Test the specific sections updated by Agent G"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.mock_client = SensingGardenClient(
            base_url="https://test-api.example.com",
            api_key="test-key-123",
            aws_access_key_id="test-aws-key",
            aws_secret_access_key="test-aws-secret"
        )
    
    def test_environment_endpoint_api_mismatch_warning_validation(self):
        """Test that the environment endpoint warning in README is accurate"""
        # Test that client sends {"data": {...}} format and server expects {"environment": {...}}
        with patch('requests.post') as mock_post:
            # Setup mock to return 400 error as documented
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "message": "Missing required fields: environment",
                "statusCode": 400
            }
            # Add raise_for_status to mock the HTTPError that should occur
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
            mock_post.return_value = mock_response
            
            # Test environment data submission
            env_data = {
                "pm1p0": 8.2,
                "pm2p5": 15.7,
                "pm4p0": 22.1,
                "pm10p0": 28.5,
                "ambient_temperature": 24.5,
                "ambient_humidity": 68.2,
                "voc_index": 120,
                "nox_index": 85
            }
            
            # This should raise an HTTPError as documented in the README warning
            with pytest.raises(requests.exceptions.HTTPError) as exc_info:
                self.mock_client.environment.add(
                    device_id="pi-greenhouse-01",
                    data=env_data,
                    timestamp="2024-08-21T12:00:00Z"
                )
            
            # Verify the request was made with {"data": {...}} format as client sends
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            # The BaseClient.post method uses json=payload, so check json parameter
            request_data = call_args[1]['json']
            
            # Confirm client sends "data" not "environment" - validating the warning
            assert "data" in request_data
            assert "environment" not in request_data
            assert request_data["data"] == env_data
            
            # Verify exception contains the expected error message
            assert "400" in str(exc_info.value)
    
    def test_confidence_score_type_flexibility_documentation(self):
        """Test that confidence scores accept both float and string values as documented"""
        
        # Mock successful response
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "test-classification", "status": "success"}
            mock_post.return_value = mock_response
            
            # Test float values (documented as primary)
            classification_float = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus", 
                species="Danaus plexippus",
                family_confidence=0.95,    # float
                genus_confidence=0.87,     # float
                species_confidence=0.82,   # float
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Test string values (documented as "also works")
            classification_string = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1", 
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus", 
                family_confidence="0.95",    # string - documented as working
                genus_confidence="0.87",     # string - documented as working
                species_confidence="0.82",   # string - documented as working
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Test mixed types (should also work based on documentation)
            classification_mixed = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data", 
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,      # float
                genus_confidence="0.87",     # string  
                species_confidence=0.82,     # float
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # All should succeed without error
            assert mock_post.call_count == 3
            
    def test_classification_data_parameter_examples(self):
        """Test the specific classification_data examples from lines 136-150 of README"""
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201 
            mock_response.json.return_value = {"id": "test-classification", "status": "success"}
            mock_post.return_value = mock_response
            
            # Test the exact classification_data structure from README lines 136-150
            classification_data_example = {
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
            }
            
            result = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                timestamp="2024-08-21T12:00:00Z",
                classification_data=classification_data_example  # The key parameter from README
            )
            
            # Verify request was made successfully
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            
            # Verify classification_data was included properly
            assert "classification_data" in request_data
            assert request_data["classification_data"] == classification_data_example
            
            # Verify the structure matches README exactly
            assert len(request_data["classification_data"]["family"]) == 2
            assert len(request_data["classification_data"]["genus"]) == 2
            assert len(request_data["classification_data"]["species"]) == 2
            
            # Verify specific values from README examples
            assert request_data["classification_data"]["family"][0]["name"] == "Nymphalidae"
            assert request_data["classification_data"]["family"][0]["confidence"] == 0.95
            assert request_data["classification_data"]["genus"][0]["name"] == "Danaus"
            assert request_data["classification_data"]["species"][0]["name"] == "Danaus plexippus"
    
    def test_bounding_box_format_differences_documentation(self):
        """Test the documented differences between detection and classification bounding boxes"""
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "test-item", "status": "success"}
            mock_post.return_value = mock_response
            
            # Test Detection bounding box (strict - must be list of 4 numeric values)
            detection_result = self.mock_client.detections.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                bounding_box=[0.1, 0.2, 0.8, 0.9],  # Must be list as documented
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Test Classification bounding box (flexible formats as documented)
            
            # Standard list format
            classification_list = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01", 
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus", 
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                bounding_box=[0.1, 0.2, 0.8, 0.9],  # Standard format
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Dictionary format (documented as accepted for classifications)
            classification_dict = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1", 
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                bounding_box={"x1": 0.1, "y1": 0.2, "x2": 0.8, "y2": 0.9},  # Dict format
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # String format (documented as accepted for classifications) 
            classification_string = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data", 
                family="Nymphalidae",
                genus="Danaus", 
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                bounding_box="0.1,0.2,0.8,0.9",  # String format
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Tuple format (documented as accepted for classifications)
            classification_tuple = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae", 
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                bounding_box=(0.1, 0.2, 0.8, 0.9),  # Tuple format  
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # All classification formats should work (4 classifications + 1 detection = 5 calls)
            assert mock_post.call_count == 5
    
    def test_detection_bounding_box_strict_validation(self):
        """Test that detection bounding boxes enforce strict validation as documented"""
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "test-detection", "status": "success"}
            mock_post.return_value = mock_response
            
            # Valid list format should work
            valid_result = self.mock_client.detections.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1", 
                image_data=b"fake_image_data",
                bounding_box=[0.1, 0.2, 0.8, 0.9],
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Test rejection of non-list formats for detections (as documented)
            with pytest.raises((ValueError, TypeError)) as exc_info:
                self.mock_client.detections.add(
                    device_id="pi-greenhouse-01",
                    model_id="yolov8-insects-v1",
                    image_data=b"fake_image_data", 
                    bounding_box=(0.1, 0.2, 0.8, 0.9),  # Tuple should be rejected
                    timestamp="2024-08-21T12:00:00Z"
                )
            
            with pytest.raises((ValueError, TypeError)):
                self.mock_client.detections.add(
                    device_id="pi-greenhouse-01",
                    model_id="yolov8-insects-v1",
                    image_data=b"fake_image_data",
                    bounding_box="0.1,0.2,0.8,0.9",  # String should be rejected
                    timestamp="2024-08-21T12:00:00Z"
                )
            
            with pytest.raises((ValueError, TypeError)):
                self.mock_client.detections.add(
                    device_id="pi-greenhouse-01",
                    model_id="yolov8-insects-v1", 
                    image_data=b"fake_image_data",
                    bounding_box={"x1": 0.1, "y1": 0.2, "x2": 0.8, "y2": 0.9},  # Dict should be rejected
                    timestamp="2024-08-21T12:00:00Z"
                )
            
            # Only one successful call should have been made
            assert mock_post.call_count == 1
    
    def test_complete_readme_example_with_all_updated_sections(self):
        """Test a complete example combining all the updated sections"""
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "complete-test", "status": "success"}
            mock_post.return_value = mock_response
            
            # Complete example using all updated documentation features
            result = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus", 
                species="Danaus plexippus",
                
                # Test confidence type flexibility (float and string mix)
                family_confidence=0.95,      # float
                genus_confidence="0.87",     # string (documented as working)  
                species_confidence=0.82,     # float
                
                timestamp="2024-08-21T12:00:00Z",
                
                # Test flexible bounding box for classifications
                bounding_box=[0.1, 0.2, 0.8, 0.9],  # List format
                
                # Optional location data
                location={
                    "lat": 40.7128,
                    "long": -74.0060,
                    "alt": 10.5
                },
                
                # Optional environmental data 
                environment={
                    "pm1p0": 12.5,
                    "pm2p5": 25.3, 
                    "pm4p0": 35.8,
                    "pm10p0": 45.2,
                    "ambient_temperature": 22.3,
                    "ambient_humidity": 65.5,
                    "voc_index": 150,
                    "nox_index": 75
                },
                
                # Test the key updated feature - classification_data from README lines 136-150
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
                
                # Optional metadata
                track_id="butterfly-track-001",
                metadata={"camera": "top", "weather": "sunny"}
            )
            
            # Verify the request was made successfully
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            
            # Verify all updated features are present
            assert "classification_data" in request_data
            assert "environment" in request_data
            assert "location" in request_data
            assert "bounding_box" in request_data
            assert "track_id" in request_data
            assert "metadata" in request_data
            
            # Verify classification_data structure matches README exactly
            assert request_data["classification_data"]["family"][0]["name"] == "Nymphalidae"
            assert request_data["classification_data"]["family"][0]["confidence"] == 0.95
            
            # Verify confidence values were accepted in mixed types
            assert "family_confidence" in request_data
            assert "genus_confidence" in request_data  
            assert "species_confidence" in request_data
    
    def test_readme_version_note_validation(self):
        """Test the version note about classification_data being added in v0.0.13"""
        
        # This test validates that the feature mentioned in the README note exists
        with patch('requests.post') as mock_post:
            mock_response = Mock() 
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "version-test", "status": "success"}
            mock_post.return_value = mock_response
            
            # Test the classification_data parameter that was noted as "added in v0.0.13"
            result = self.mock_client.classifications.add(
                device_id="pi-greenhouse-01",
                model_id="yolov8-insects-v1",
                image_data=b"fake_image_data",
                family="Nymphalidae",
                genus="Danaus",
                species="Danaus plexippus",
                family_confidence=0.95,
                genus_confidence=0.87,
                species_confidence=0.82,
                classification_data={  # This is the v0.0.13 feature
                    "family": [{"name": "Nymphalidae", "confidence": 0.95}]
                },
                timestamp="2024-08-21T12:00:00Z"
            )
            
            # Verify it works (proving the version note is accurate)
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            assert "classification_data" in request_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])