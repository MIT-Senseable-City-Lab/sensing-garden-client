#!/usr/bin/env python3
"""
Pytest-compatible tests for the new environment and location functionality in classification calls.

This file demonstrates how to use the new test functions in a pytest framework.
Run with: pytest tests/test_classifications_pytest.py -v
"""
import pytest
from datetime import datetime

from .test_classifications import (
    test_add_classification_with_location_only,
    test_add_classification_with_location_no_altitude,
    test_add_classification_with_environment_only,
    test_add_classification_with_partial_environment,
    test_add_classification_with_location_and_environment,
    test_add_classification_with_all_optional_fields,
    test_add_classification_with_edge_case_location,
    test_add_classification_with_extreme_environment_values,
    test_add_classification_with_minimal_environment_data,
    test_add_classification_data_type_validation,
    test_backward_compatibility_existing_classification
)


class TestClassificationLocationFunctionality:
    """Test class for classification location functionality."""

    def test_location_with_altitude(self, device_id, model_id):
        """Test classification with location data including altitude."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_location_only(device_id, model_id, timestamp)

    def test_location_without_altitude(self, device_id, model_id):
        """Test classification with location data without altitude."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_location_no_altitude(device_id, model_id, timestamp)

    def test_edge_case_coordinates(self, device_id, model_id):
        """Test classification with extreme but valid coordinates."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_edge_case_location(device_id, model_id, timestamp)


class TestClassificationEnvironmentFunctionality:
    """Test class for classification environment functionality."""

    def test_complete_environment_data(self, device_id, model_id):
        """Test classification with complete environment data."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_environment_only(device_id, model_id, timestamp)

    def test_partial_environment_data(self, device_id, model_id):
        """Test classification with partial environment data."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_partial_environment(device_id, model_id, timestamp)

    def test_minimal_environment_data(self, device_id, model_id):
        """Test classification with minimal environment data."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_minimal_environment_data(device_id, model_id, timestamp)

    def test_extreme_environment_values(self, device_id, model_id):
        """Test classification with extreme but valid environment values."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_extreme_environment_values(device_id, model_id, timestamp)


class TestClassificationCombinedFunctionality:
    """Test class for combined location and environment functionality."""

    def test_location_and_environment_combined(self, device_id, model_id):
        """Test classification with both location and environment data."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_location_and_environment(device_id, model_id, timestamp)

    def test_all_optional_fields(self, device_id, model_id):
        """Test classification with all possible optional fields."""
        timestamp = datetime.now().isoformat()
        test_add_classification_with_all_optional_fields(device_id, model_id, timestamp)


class TestClassificationValidation:
    """Test class for validation and edge cases."""

    def test_data_type_validation(self, device_id, model_id):
        """Test classification with mixed data types."""
        timestamp = datetime.now().isoformat()
        test_add_classification_data_type_validation(device_id, model_id, timestamp)

    def test_backward_compatibility(self, device_id, model_id):
        """Test that existing functionality still works."""
        timestamp = datetime.now().isoformat()
        test_backward_compatibility_existing_classification(device_id, model_id, timestamp)


# Individual test functions for direct pytest execution
def test_location_only_functionality(device_id, model_id):
    """Pytest wrapper for location-only functionality."""
    timestamp = datetime.now().isoformat()
    test_add_classification_with_location_only(device_id, model_id, timestamp)


def test_environment_only_functionality(device_id, model_id):
    """Pytest wrapper for environment-only functionality."""  
    timestamp = datetime.now().isoformat()
    test_add_classification_with_environment_only(device_id, model_id, timestamp)


def test_combined_location_environment(device_id, model_id):
    """Pytest wrapper for combined location and environment functionality."""
    timestamp = datetime.now().isoformat()
    test_add_classification_with_location_and_environment(device_id, model_id, timestamp)


def test_comprehensive_optional_fields(device_id, model_id):
    """Pytest wrapper for comprehensive test with all optional fields."""
    timestamp = datetime.now().isoformat()
    test_add_classification_with_all_optional_fields(device_id, model_id, timestamp)


if __name__ == "__main__":
    # Run tests directly if called as a script
    import sys
    from .conftest import test_vars
    
    device_id = test_vars["device_id"]
    model_id = test_vars["model_id"]
    
    print("Running comprehensive classification tests...")
    
    try:
        test_location_only_functionality(device_id, model_id)
        test_environment_only_functionality(device_id, model_id)
        test_combined_location_environment(device_id, model_id)
        test_comprehensive_optional_fields(device_id, model_id)
        print("✅ All pytest tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)