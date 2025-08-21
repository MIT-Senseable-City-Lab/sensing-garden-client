#!/usr/bin/env python3
"""
README Classification Edge Cases and Parameter Validation Tests

This module tests edge cases and parameter combinations for the classification
examples to ensure robust behavior beyond the basic README examples.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from tests.test_utils import get_client, create_test_image, print_response


class TestReadmeEdgeCases:
    """Test edge cases for README classification examples."""

    def setup_method(self):
        """Setup for each test method."""
        self.client = get_client()
        self.image_data = create_test_image()
        self.test_timestamp = datetime.now().isoformat()

    def test_classification_data_with_single_candidate(self):
        """Test classification_data with only one candidate per level."""
        print("\n[EDGE CASE] Testing classification_data with single candidates")
        
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
            
            # Single candidate per taxonomic level
            classification_data={
                "family": [{"name": "Nymphalidae", "confidence": 0.95}],
                "genus": [{"name": "Danaus", "confidence": 0.87}],
                "species": [{"name": "Danaus plexippus", "confidence": 0.82}]
            }
        )
        
        data = classification.get('data', classification)
        classification_data = data.get('classification_data')
        
        assert classification_data is not None, "classification_data should be returned"
        assert len(classification_data['family']) == 1, "Family should have 1 candidate"
        assert len(classification_data['genus']) == 1, "Genus should have 1 candidate"
        assert len(classification_data['species']) == 1, "Species should have 1 candidate"
        
        print("✅ Single candidate classification_data test passed!")

    def test_classification_data_with_many_candidates(self):
        """Test classification_data with many candidates per level."""
        print("\n[EDGE CASE] Testing classification_data with many candidates")
        
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
            
            # Many candidates per taxonomic level
            classification_data={
                "family": [
                    {"name": "Nymphalidae", "confidence": 0.95},
                    {"name": "Pieridae", "confidence": 0.78},
                    {"name": "Lycaenidae", "confidence": 0.65},
                    {"name": "Hesperiidae", "confidence": 0.45},
                    {"name": "Riodinidae", "confidence": 0.32}
                ],
                "genus": [
                    {"name": "Danaus", "confidence": 0.87},
                    {"name": "Heliconius", "confidence": 0.75},
                    {"name": "Morpho", "confidence": 0.62},
                    {"name": "Papilio", "confidence": 0.48}
                ],
                "species": [
                    {"name": "Danaus plexippus", "confidence": 0.82},
                    {"name": "Danaus gilippus", "confidence": 0.71},
                    {"name": "Danaus chrysippus", "confidence": 0.58},
                    {"name": "Danaus erippus", "confidence": 0.43}
                ]
            }
        )
        
        data = classification.get('data', classification)
        classification_data = data.get('classification_data')
        
        assert classification_data is not None, "classification_data should be returned"
        assert len(classification_data['family']) == 5, "Family should have 5 candidates"
        assert len(classification_data['genus']) == 4, "Genus should have 4 candidates"
        assert len(classification_data['species']) == 4, "Species should have 4 candidates"
        
        print("✅ Many candidates classification_data test passed!")

    def test_environment_data_with_partial_fields(self):
        """Test environment data with only some fields present."""
        print("\n[EDGE CASE] Testing environment data with partial fields")
        
        # Test with only temperature and humidity
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
            
            environment={
                "ambient_temperature": 22.3,
                "ambient_humidity": 65.5
            }
        )
        
        data = classification.get('data', classification)
        environment = data.get('environment')
        
        assert environment is not None, "Environment data should be returned"
        assert environment.get('ambient_temperature') == 22.3, "Temperature should be returned"
        assert environment.get('ambient_humidity') == 65.5, "Humidity should be returned"
        assert 'pm1p0' not in environment, "PM1.0 should not be present when not provided"
        
        print("✅ Partial environment data test passed!")

    def test_environment_data_with_extreme_values(self):
        """Test environment data with extreme but valid values."""
        print("\n[EDGE CASE] Testing environment data with extreme values")
        
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
            
            environment={
                "pm1p0": 0.1,           # Very low PM
                "pm2p5": 500.0,         # Very high PM2.5
                "ambient_temperature": -20.0,  # Very cold
                "ambient_humidity": 99.9,       # Very humid
                "voc_index": 1,         # Minimum VOC
                "nox_index": 1000       # Maximum NOx
            }
        )
        
        data = classification.get('data', classification)
        environment = data.get('environment')
        
        assert environment is not None, "Environment data should be returned"
        assert environment.get('pm1p0') == 0.1, "Low PM1.0 should be handled"
        assert environment.get('pm2p5') == 500.0, "High PM2.5 should be handled"
        assert environment.get('ambient_temperature') == -20.0, "Negative temperature should be handled"
        assert environment.get('ambient_humidity') == 99.9, "High humidity should be handled"
        
        print("✅ Extreme environment values test passed!")

    def test_location_data_edge_coordinates(self):
        """Test location data with edge case coordinates."""
        print("\n[EDGE CASE] Testing location data with edge coordinates")
        
        # Test with extreme but valid coordinates
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
            
            location={
                "lat": -89.99,   # Near south pole
                "long": 179.99,  # Near date line
                "alt": 8848.0    # Mount Everest height
            }
        )
        
        data = classification.get('data', classification)
        location = data.get('location')
        
        assert location is not None, "Location data should be returned"
        assert location.get('lat') == -89.99, "Extreme latitude should be handled"
        assert location.get('long') == 179.99, "Extreme longitude should be handled"
        assert location.get('alt') == 8848.0, "High altitude should be handled"
        
        print("✅ Edge coordinates location test passed!")

    def test_bounding_box_edge_values(self):
        """Test bounding box with edge values."""
        print("\n[EDGE CASE] Testing bounding box with edge values")
        
        # Test with minimal bounding box
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
            
            bounding_box=[0.0, 0.0, 1.0, 1.0]  # Full image bounding box
        )
        
        data = classification.get('data', classification)
        bounding_box = data.get('bounding_box')
        
        assert bounding_box is not None, "Bounding box should be returned"
        assert bounding_box == [0.0, 0.0, 1.0, 1.0], "Full image bounding box should be handled"
        
        print("✅ Edge values bounding box test passed!")

    def test_confidence_values_edge_cases(self):
        """Test confidence values at edges (0.0 and 1.0)."""
        print("\n[EDGE CASE] Testing confidence values at edges")
        
        classification = self.client.classifications.add(
            device_id="pi-greenhouse-01",
            model_id="yolov8-insects-v1",
            image_data=self.image_data,
            family="Nymphalidae",
            genus="Danaus",
            species="Danaus plexippus",
            family_confidence=1.0,  # Perfect confidence
            genus_confidence=0.0,   # Zero confidence
            species_confidence=0.5,  # Middle confidence
            timestamp=self.test_timestamp,
            
            classification_data={
                "family": [
                    {"name": "Nymphalidae", "confidence": 1.0},   # Perfect confidence
                    {"name": "Pieridae", "confidence": 0.0}       # Zero confidence
                ],
                "genus": [{"name": "Danaus", "confidence": 0.01}],  # Very low confidence
                "species": [{"name": "Danaus plexippus", "confidence": 0.99}]  # Very high confidence
            }
        )
        
        data = classification.get('data', classification)
        
        assert data.get('family_confidence') == 1.0, "Perfect confidence should be handled"
        assert data.get('genus_confidence') == 0.0, "Zero confidence should be handled"
        assert data.get('species_confidence') == 0.5, "Middle confidence should be handled"
        
        classification_data = data.get('classification_data')
        assert classification_data['family'][0]['confidence'] == 1.0, "Perfect confidence in classification_data"
        assert classification_data['family'][1]['confidence'] == 0.0, "Zero confidence in classification_data"
        
        print("✅ Edge confidence values test passed!")

    def test_nested_metadata_object(self):
        """Test with nested metadata object."""
        print("\n[EDGE CASE] Testing nested metadata object")
        
        nested_metadata = {
            "camera": "top",
            "weather": "sunny", 
            "conditions": {
                "lighting": "natural",
                "background": "garden"
            },
            "equipment": {
                "camera_model": "RaspberryPi HQ Camera",
                "settings": {
                    "iso": 100,
                    "aperture": "f/8"
                }
            }
        }
        
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
            
            metadata=nested_metadata
        )
        
        data = classification.get('data', classification)
        returned_metadata = data.get('metadata')
        
        assert returned_metadata is not None, "Nested metadata should be returned"
        assert returned_metadata.get('camera') == "top", "Metadata camera should be returned"
        assert returned_metadata.get('conditions', {}).get('lighting') == "natural", "Nested metadata should be returned"
        assert returned_metadata.get('equipment', {}).get('settings', {}).get('iso') == 100, "Deep nested metadata should be returned"
        
        print("✅ Nested metadata object test passed!")


if __name__ == "__main__":
    print("Edge case tests for README classification examples")
    print("Run with: pytest tests/test_readme_edge_cases.py -v")