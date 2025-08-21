#!/usr/bin/env python3
"""
Test to verify models.create() parameter requirements discrepancy found by Agent A.

This test specifically checks if the 'description' parameter is optional as implemented
in the code (line 29: description: str = "") vs potentially required in the README example.
"""
import pytest
import uuid
from tests.test_utils import get_client

class TestModelsCreateParams:
    """Test class for models.create parameter requirements"""

    def setup_method(self):
        """Setup for each test method"""
        self.client = get_client()

    def test_models_create_without_description(self):
        """
        Test that models.create works without the description parameter.
        
        This verifies that the implementation allows description to be optional
        (defaults to empty string) even though the README example always includes it.
        """
        model_id = f"test-no-desc-{uuid.uuid4().hex[:8]}"
        
        # Test without description parameter (relying on default)
        response = self.client.models.create(
            model_id=model_id,
            name="Test Model Without Description",
            version="1.0.0"
            # description is intentionally omitted
        )
        
        # Verify the request succeeded
        assert "data" in response or "message" in response
        print(f"✅ models.create works without description parameter")
        print(f"Response: {response}")

    def test_models_create_with_empty_description(self):
        """
        Test that models.create works with an explicitly empty description.
        """
        model_id = f"test-empty-desc-{uuid.uuid4().hex[:8]}"
        
        # Test with empty description
        response = self.client.models.create(
            model_id=model_id,
            name="Test Model With Empty Description",
            version="1.0.0",
            description=""  # explicitly empty
        )
        
        # Verify the request succeeded
        assert "data" in response or "message" in response
        print(f"✅ models.create works with empty description")
        print(f"Response: {response}")

    def test_models_create_with_description(self):
        """
        Test that models.create works with a description (as shown in README).
        """
        model_id = f"test-with-desc-{uuid.uuid4().hex[:8]}"
        
        # Test with description (as shown in README)
        response = self.client.models.create(
            model_id=model_id,
            name="Test Model With Description",
            version="1.0.0",
            description="A test model with description"
        )
        
        # Verify the request succeeded
        assert "data" in response or "message" in response
        print(f"✅ models.create works with description (as shown in README)")
        print(f"Response: {response}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])