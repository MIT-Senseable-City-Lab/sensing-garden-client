#!/usr/bin/env python3
"""
README Classification Examples Validation Tests

This module validates that ALL classification examples shown in the README.md file
work exactly as documented. It tests every parameter combination shown in lines 102-160
of the README.

Test Coverage:
- Basic classification example (lines 102-112)
- Classification with bounding box (lines 114-115) 
- Classification with location (lines 117-122)
- Classification with environment data (lines 124-134)
- Classification with classification_data arrays (lines 136-150)
- Classification with all optional fields (lines 152-155)

Each test function executes the exact code examples from the README to ensure
they work as documented.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List, Optional

from tests.test_utils import get_client, create_test_image, print_response


class TestReadmeClassificationExamples:
    """Test class for validating all README classification examples."""

    def setup_method(self):
        """Setup for each test method."""
        self.client = get_client()
        self.image_data = create_test_image()
        self.test_timestamp = datetime.now().isoformat()

    def test_readme_basic_classification_example(self):
        """
        Test the basic classification example from README lines 102-112.
        
        This validates the core classification functionality shown in the README.
        """
        print("\n[README VALIDATION] Testing basic classification example (lines 102-112)")
        
        # Execute the exact example from README lines 102-112
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1", 
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
        )
        
        print_response(classification)
        
        # Validate response contains expected data
        assert classification is not None, "Classification response should not be None"
        
        # Check that basic classification data is returned
        data = classification.get('data', classification)
        assert data.get('device_id') == "pi-greenhouse-01", "Device ID should be returned"
        assert data.get('model_id') == "yolov8-insects-v1", "Model ID should be returned" 
        assert data.get('family') == "Nymphalidae", "Family should be returned"
        assert data.get('genus') == "Danaus", "Genus should be returned"
        assert data.get('species') == "Danaus plexippus", "Species should be returned"
        
        print("✅ Basic classification example validation passed!")

    def test_readme_classification_with_bounding_box(self):
        """
        Test classification with bounding box from README lines 114-115.
        
        This validates the bounding box parameter functionality.
        """
        print("\n[README VALIDATION] Testing classification with bounding box (lines 114-115)")
        
        # Execute the exact example from README with bounding box
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae", 
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
            # Optional: Bounding box coordinates as floats
            bounding_box=[0.1, 0.2, 0.8, 0.9],  # [x1, y1, x2, y2] normalized (0.0-1.0)
        )
        
        print_response(classification)
        
        # Validate bounding box is returned
        data = classification.get('data', classification)
        returned_bbox = data.get('bounding_box')
        expected_bbox = [0.1, 0.2, 0.8, 0.9]
        
        assert returned_bbox is not None, "Bounding box should be returned in response"
        assert returned_bbox == expected_bbox, f"Bounding box should match: expected {expected_bbox}, got {returned_bbox}"
        
        print("✅ Classification with bounding box validation passed!")

    def test_readme_classification_with_location(self):
        """
        Test classification with location from README lines 117-122.
        
        This validates the location parameter functionality.
        """
        print("\n[README VALIDATION] Testing classification with location (lines 117-122)")
        
        # Execute the exact example from README with location
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus", 
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
            # Optional: Location data
            location={
                "lat": 40.7128,
                "long": -74.0060,
                "alt": 10.5  # altitude in meters
            },
        )
        
        print_response(classification)
        
        # Validate location data is returned
        data = classification.get('data', classification)
        returned_location = data.get('location')
        expected_location = {
            "lat": 40.7128,
            "long": -74.0060,
            "alt": 10.5
        }
        
        assert returned_location is not None, "Location should be returned in response"
        assert returned_location['lat'] == expected_location['lat'], f"Latitude should match: expected {expected_location['lat']}, got {returned_location.get('lat')}"
        assert returned_location['long'] == expected_location['long'], f"Longitude should match: expected {expected_location['long']}, got {returned_location.get('long')}"
        assert returned_location['alt'] == expected_location['alt'], f"Altitude should match: expected {expected_location['alt']}, got {returned_location.get('alt')}"
        
        print("✅ Classification with location validation passed!")

    def test_readme_classification_with_environment_data(self):
        """
        Test classification with environment data from README lines 124-134.
        
        This validates the environment parameter functionality.
        """
        print("\n[README VALIDATION] Testing classification with environment data (lines 124-134)")
        
        # Execute the exact example from README with environment data
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus", 
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
            # Optional: Environmental sensor data
            environment={
                "pm1p0": 12.5,              # PM1.0 particulate matter (μg/m³)
                "pm2p5": 25.3,              # PM2.5 particulate matter (μg/m³)
                "pm4p0": 35.8,              # PM4.0 particulate matter (μg/m³)
                "pm10p0": 45.2,             # PM10.0 particulate matter (μg/m³)
                "ambient_temperature": 22.3, # Temperature (°C)
                "ambient_humidity": 65.5,    # Relative humidity (%)
                "voc_index": 150,           # Volatile Organic Compounds index
                "nox_index": 75             # Nitrogen Oxides index
            },
        )
        
        print_response(classification)
        
        # Validate environment data is returned
        data = classification.get('data', classification)
        returned_environment = data.get('environment')
        expected_environment = {
            "pm1p0": 12.5,
            "pm2p5": 25.3,
            "pm4p0": 35.8,
            "pm10p0": 45.2,
            "ambient_temperature": 22.3,
            "ambient_humidity": 65.5,
            "voc_index": 150,
            "nox_index": 75
        }
        
        assert returned_environment is not None, "Environment data should be returned in response"
        
        # Validate each environment field
        for field, expected_value in expected_environment.items():
            actual_value = returned_environment.get(field)
            assert actual_value is not None, f"Environment field '{field}' should be present in response"
            assert actual_value == expected_value, f"Environment field '{field}' should match: expected {expected_value}, got {actual_value}"
        
        print("✅ Classification with environment data validation passed!")

    def test_readme_classification_with_classification_data(self):
        """
        Test classification with classification_data from README lines 136-150.
        
        This validates the classification_data parameter with confidence arrays.
        This is a critical test as classification_data is highlighted as a key feature.
        """
        print("\n[README VALIDATION] Testing classification with classification_data (lines 136-150)")
        
        # Execute the exact example from README with classification_data
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
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
        )
        
        print_response(classification)
        
        # Validate classification_data is returned
        data = classification.get('data', classification)
        returned_classification_data = data.get('classification_data')
        expected_classification_data = {
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
        
        assert returned_classification_data is not None, "Classification data should be returned in response"
        
        # Validate each taxonomic level
        for level in ["family", "genus", "species"]:
            assert level in returned_classification_data, f"Classification data should contain '{level}' level"
            returned_level_data = returned_classification_data[level]
            expected_level_data = expected_classification_data[level]
            
            assert len(returned_level_data) == len(expected_level_data), f"Classification data '{level}' should have {len(expected_level_data)} entries"
            
            # Validate each candidate in the level
            for i, expected_candidate in enumerate(expected_level_data):
                returned_candidate = returned_level_data[i]
                assert returned_candidate['name'] == expected_candidate['name'], f"Classification data '{level}' candidate {i} name should match"
                assert returned_candidate['confidence'] == expected_candidate['confidence'], f"Classification data '{level}' candidate {i} confidence should match"
        
        print("✅ Classification with classification_data validation passed!")

    def test_readme_classification_with_all_optional_fields(self):
        """
        Test classification with all optional fields from README lines 152-155.
        
        This validates the complete example with tracking and metadata.
        """
        print("\n[README VALIDATION] Testing classification with all optional fields (lines 152-155)")
        
        # Execute the exact example from README with all optional fields
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
            # Optional: Bounding box coordinates as floats
            bounding_box=[0.1, 0.2, 0.8, 0.9],  # [x1, y1, x2, y2] normalized (0.0-1.0)
            
            # Optional: Location data
            location={
                "lat": 40.7128,
                "long": -74.0060,
                "alt": 10.5  # altitude in meters
            },
            
            # Optional: Environmental sensor data
            environment={
                "pm1p0": 12.5,              # PM1.0 particulate matter (μg/m³)
                "pm2p5": 25.3,              # PM2.5 particulate matter (μg/m³)
                "pm4p0": 35.8,              # PM4.0 particulate matter (μg/m³)
                "pm10p0": 45.2,             # PM10.0 particulate matter (μg/m³)
                "ambient_temperature": 22.3, # Temperature (°C)
                "ambient_humidity": 65.5,    # Relative humidity (%)
                "voc_index": 150,           # Volatile Organic Compounds index
                "nox_index": 75             # Nitrogen Oxides index
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
        
        print_response(classification)
        
        # Validate all optional fields are returned
        data = classification.get('data', classification)
        
        # Validate bounding box
        assert data.get('bounding_box') == [0.1, 0.2, 0.8, 0.9], "Bounding box should be returned"
        
        # Validate location
        location = data.get('location')
        assert location is not None, "Location should be returned"
        assert location['lat'] == 40.7128, "Location latitude should match"
        assert location['long'] == -74.0060, "Location longitude should match" 
        assert location['alt'] == 10.5, "Location altitude should match"
        
        # Validate environment
        environment = data.get('environment')
        assert environment is not None, "Environment data should be returned"
        assert environment['pm1p0'] == 12.5, "Environment PM1.0 should match"
        assert environment['ambient_temperature'] == 22.3, "Environment temperature should match"
        
        # Validate classification_data
        classification_data = data.get('classification_data')
        assert classification_data is not None, "Classification data should be returned"
        assert len(classification_data['family']) == 2, "Classification data family should have 2 entries"
        
        # Validate track_id and metadata
        assert data.get('track_id') == "butterfly-track-001", "Track ID should be returned"
        metadata = data.get('metadata')
        assert metadata is not None, "Metadata should be returned"
        assert metadata.get('camera') == "top", "Metadata camera should match"
        assert metadata.get('weather') == "sunny", "Metadata weather should match"
        
        print("✅ Classification with all optional fields validation passed!")

    def test_readme_complete_example_execution(self):
        """
        Test executing the complete README example exactly as shown.
        
        This test runs the exact code block from the README to ensure it works
        without any modifications.
        """
        print("\n[README VALIDATION] Testing complete README example execution (lines 102-155)")
        
        # This is the EXACT code from the README (with our test image_data)
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,  # Using our test image data
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,  # Using our test timestamp
            
            # Optional: Bounding box coordinates as floats
            bounding_box=[0.1, 0.2, 0.8, 0.9],  # [x1, y1, x2, y2] normalized (0.0-1.0)
            
            # Optional: Location data
            location={
                "lat": 40.7128,
                "long": -74.0060,
                "alt": 10.5  # altitude in meters
            },
            
            # Optional: Environmental sensor data
            environment={
                "pm1p0": 12.5,              # PM1.0 particulate matter (μg/m³)
                "pm2p5": 25.3,              # PM2.5 particulate matter (μg/m³)
                "pm4p0": 35.8,              # PM4.0 particulate matter (μg/m³)
                "pm10p0": 45.2,             # PM10.0 particulate matter (μg/m³)
                "ambient_temperature": 22.3, # Temperature (°C)
                "ambient_humidity": 65.5,    # Relative humidity (%)
                "voc_index": 150,           # Volatile Organic Compounds index
                "nox_index": 75             # Nitrogen Oxides index
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
        
        print_response(classification)
        
        # Basic validation that the request succeeded
        assert classification is not None, "Complete README example should execute successfully"
        
        print("✅ Complete README example execution validation passed!")

    def test_classification_data_parameter_specifically(self):
        """
        Focused test on the classification_data parameter feature.
        
        This test specifically validates the classification_data parameter that was
        added in v0.0.13 as mentioned in the README comments (lines 157-159).
        """
        print("\n[README VALIDATION] Testing classification_data parameter specifically")
        
        # Test with ONLY classification_data parameter (minimal example)
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1", 
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=0.95,
            genus_confidence=0.87,
            species_confidence=0.82,
            timestamp=self.test_timestamp,
            
            # Focus on classification_data only
            classification_data={
                "family": [
                    {"name": "Nymphalidae", "confidence": 0.95},
                    {"name": "Pieridae", "confidence": 0.78},
                    {"name": "Lycaenidae", "confidence": 0.45}
                ],
                "genus": [
                    {"name": "Danaus", "confidence": 0.87},
                    {"name": "Heliconius", "confidence": 0.65},
                    {"name": "Morpho", "confidence": 0.32}
                ],
                "species": [
                    {"name": "Danaus plexippus", "confidence": 0.82},
                    {"name": "Danaus gilippus", "confidence": 0.71},
                    {"name": "Danaus chrysippus", "confidence": 0.28}
                ]
            }
        )
        
        print_response(classification)
        
        # Detailed validation of classification_data structure
        data = classification.get('data', classification)
        classification_data = data.get('classification_data')
        
        assert classification_data is not None, "classification_data should be returned"
        assert isinstance(classification_data, dict), "classification_data should be a dictionary"
        
        # Validate structure for each taxonomic level
        for level in ['family', 'genus', 'species']:
            assert level in classification_data, f"classification_data should contain {level} level"
            level_data = classification_data[level]
            assert isinstance(level_data, list), f"{level} should be a list of candidates"
            assert len(level_data) == 3, f"{level} should have 3 candidates"
            
            # Validate each candidate structure
            for i, candidate in enumerate(level_data):
                assert isinstance(candidate, dict), f"{level} candidate {i} should be a dictionary"
                assert 'name' in candidate, f"{level} candidate {i} should have 'name' field"
                assert 'confidence' in candidate, f"{level} candidate {i} should have 'confidence' field"
                assert isinstance(candidate['name'], str), f"{level} candidate {i} name should be string"
                assert isinstance(candidate['confidence'], (int, float)), f"{level} candidate {i} confidence should be numeric"
                assert 0 <= candidate['confidence'] <= 1, f"{level} candidate {i} confidence should be between 0 and 1"
        
        print("✅ classification_data parameter specific validation passed!")


def generate_validation_report() -> str:
    """
    Generate a comprehensive validation report for README examples.
    
    Returns:
        str: Formatted validation report
    """
    report = []
    report.append("=" * 80)
    report.append("README CLASSIFICATION EXAMPLES VALIDATION REPORT")
    report.append("=" * 80)
    report.append("")
    report.append("This report summarizes the validation of all classification examples")
    report.append("shown in the README.md file (lines 102-160).")
    report.append("")
    report.append("EXAMPLES VALIDATED:")
    report.append("• Basic classification (lines 102-112)")
    report.append("• Classification with bounding box (lines 114-115)")
    report.append("• Classification with location (lines 117-122)")  
    report.append("• Classification with environment data (lines 124-134)")
    report.append("• Classification with classification_data (lines 136-150)")
    report.append("• Classification with all optional fields (lines 152-155)")
    report.append("• Complete README example execution")
    report.append("• classification_data parameter specific testing")
    report.append("")
    report.append("Run with: pytest tests/test_readme_classification_validation.py -v")
    report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    print(generate_validation_report())