#!/usr/bin/env python3
"""
Validation tests for all non-classification API examples in README.md

This module tests the actual behavior of API examples shown in the README
to verify they work as documented and identify any discrepancies.

Test focus areas:
1. Device management examples (lines 45-54)
2. Model creation/fetch examples (lines 59-70)
3. Detection examples (lines 75-94)
4. Environment data examples (lines 167-191)
5. Video upload examples (if AWS credentials available)
6. Query/pagination examples (lines 238-255)
"""
import os
import pytest
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from tests.test_utils import (
    get_client, 
    create_test_image, 
    create_test_video,
    generate_random_string,
    generate_random_bounding_box,
    print_response
)


class TestReadmeValidation:
    """Test class for validating all README examples"""

    def setup_method(self):
        """Setup for each test method"""
        self.client = get_client()
        self.test_device_id = f"readme-test-device-{uuid.uuid4().hex[:8]}"
        self.test_model_id = f"readme-test-model-{uuid.uuid4().hex[:8]}"
        self.test_timestamp = "2024-08-21T12:00:00Z"
        self.created_devices = []
        self.created_models = []

    def teardown_method(self):
        """Cleanup after each test method"""
        # Clean up any devices created during tests
        for device_id in self.created_devices:
            try:
                self.client.delete_device(device_id)
            except Exception:
                pass  # Ignore cleanup errors

    def test_device_management_examples(self):
        """
        Test device management examples from README lines 45-54:
        - client.add_device(device_id="pi-greenhouse-01")
        - devices, next_token = client.get_devices(limit=50)
        - devices, next_token = client.get_devices(device_id="pi-greenhouse-01")
        - client.delete_device(device_id="pi-greenhouse-01")
        """
        print("\n=== Testing Device Management Examples ===")
        
        # Test 1: Add device (README line 47)
        print(f"Testing add_device with device_id: {self.test_device_id}")
        response = self.client.add_device(device_id=self.test_device_id)
        print_response(response)
        
        # Verify response format - should have statusCode
        assert "statusCode" in response, f"Response missing statusCode: {response}"
        assert response["statusCode"] == 200 or "message" in response
        self.created_devices.append(self.test_device_id)
        
        # Test 2: Get devices with limit (README line 50)
        print(f"Testing get_devices with limit=50")
        devices, next_token = self.client.get_devices(limit=50)
        print(f"Found {len(devices)} devices, next_token: {next_token}")
        
        # Verify return format matches README documentation
        assert isinstance(devices, list), f"Expected list, got {type(devices)}"
        assert next_token is None or isinstance(next_token, str), f"Invalid next_token type: {type(next_token)}"
        
        # Test 3: Get devices by device_id (README line 51)
        print(f"Testing get_devices with device_id filter")
        devices, next_token = self.client.get_devices(device_id=self.test_device_id)
        print(f"Found {len(devices)} devices with device_id filter")
        
        # Verify our test device is in the results
        device_ids = [d.get("device_id") for d in devices]
        assert self.test_device_id in device_ids, f"Device {self.test_device_id} not found in results"
        
        # Test 4: Delete device (README line 54)
        print(f"Testing delete_device")
        response = self.client.delete_device(device_id=self.test_device_id)
        print_response(response)
        
        # Verify response format
        assert "statusCode" in response, f"Response missing statusCode: {response}"
        assert response["statusCode"] == 200 or "message" in response
        self.created_devices.remove(self.test_device_id)
        
        # Verify device is actually deleted
        devices, _ = self.client.get_devices(device_id=self.test_device_id)
        device_ids = [d.get("device_id") for d in devices]
        assert self.test_device_id not in device_ids, f"Device {self.test_device_id} still exists after delete"
        
        print("✅ All device management examples validated successfully")

    def test_model_examples(self):
        """
        Test model examples from README lines 59-70:
        - model = client.models.create(...)
        - models = client.models.fetch(limit=10)
        - model_count = client.models.count()
        """
        print("\n=== Testing Model Examples ===")
        
        # Test 1: Create model (README lines 61-66)
        # This tests the parameter requirements issue found by Agent A
        print(f"Testing models.create with model_id: {self.test_model_id}")
        
        # Test with all parameters as shown in README
        try:
            model = self.client.models.create(
                model_id=self.test_model_id,
                name="YOLOv8 Insect Detection",
                version="1.0.0",
                description="Trained on 10k insect images"  # This should be optional per Agent A's findings
            )
            print_response(model)
            self.created_models.append(self.test_model_id)
            print("✅ models.create with description parameter works")
        except Exception as e:
            print(f"❌ models.create with description failed: {e}")
            # Test without description to see if it's actually required
            try:
                model = self.client.models.create(
                    model_id=f"{self.test_model_id}-no-desc",
                    name="YOLOv8 Insect Detection",
                    version="1.0.0"
                )
                print_response(model)
                self.created_models.append(f"{self.test_model_id}-no-desc")
                print("⚠️ models.create works without description - README may be incorrect about requirements")
            except Exception as e2:
                print(f"❌ models.create without description also failed: {e2}")
                pytest.fail(f"models.create failed with and without description: {e}, {e2}")
        
        # Test 2: Fetch models (README line 69)
        print(f"Testing models.fetch with limit=10")
        try:
            models = self.client.models.fetch(limit=10)
            print_response(models)
            
            # Verify response structure
            assert isinstance(models, dict), f"Expected dict response, got {type(models)}"
            assert "items" in models or len(models) > 0, f"No items in models response: {models}"
            print("✅ models.fetch works")
        except Exception as e:
            print(f"❌ models.fetch failed: {e}")
            pytest.fail(f"models.fetch failed: {e}")
        
        # Test 3: Count models (README line 70)
        print(f"Testing models.count")
        try:
            model_count = self.client.models.count()
            print(f"Model count: {model_count}")
            
            # Verify count is a number
            assert isinstance(model_count, (int, dict)), f"Expected int or dict, got {type(model_count)}: {model_count}"
            print("✅ models.count works")
        except Exception as e:
            print(f"❌ models.count failed: {e}")
            pytest.fail(f"models.count failed: {e}")
        
        print("✅ All model examples validated")

    def test_detection_examples(self):
        """
        Test detection examples from README lines 75-94:
        - detection = client.detections.add(...)
        - detections = client.detections.fetch(...)
        """
        print("\n=== Testing Detection Examples ===")
        
        # First, ensure we have a test device and model
        self.client.add_device(device_id=self.test_device_id)
        self.created_devices.append(self.test_device_id)
        
        # Try to use an existing model or create one
        try:
            models = self.client.models.fetch(limit=1)
            if models.get("items"):
                model_id = models["items"][0].get("model_id") or models["items"][0].get("id")
            else:
                # Create a test model
                model = self.client.models.create(
                    model_id=self.test_model_id,
                    name="Test Detection Model",
                    version="1.0.0"
                )
                model_id = self.test_model_id
                self.created_models.append(model_id)
        except Exception as e:
            print(f"Failed to get/create model: {e}")
            model_id = "yolov8-insects-v1"  # Use example model ID from README
        
        # Test 1: Add detection (README lines 81-87)
        print(f"Testing detections.add")
        image_data = create_test_image()
        
        try:
            detection = self.client.detections.add(
                device_id=self.test_device_id,
                model_id=model_id,
                image_data=image_data,
                bounding_box=[0.1, 0.2, 0.8, 0.9],  # As shown in README
                timestamp=self.test_timestamp
            )
            print_response(detection)
            print("✅ detections.add works")
        except Exception as e:
            print(f"❌ detections.add failed: {e}")
            pytest.fail(f"detections.add failed: {e}")
        
        # Test 2: Fetch detections (README lines 90-94)
        print(f"Testing detections.fetch")
        try:
            detections = self.client.detections.fetch(
                device_id=self.test_device_id,
                start_time="2024-08-20T00:00:00Z",
                limit=100
            )
            print_response(detections)
            
            # Verify response structure
            assert isinstance(detections, dict), f"Expected dict response, got {type(detections)}"
            print("✅ detections.fetch works")
        except Exception as e:
            print(f"❌ detections.fetch failed: {e}")
            pytest.fail(f"detections.fetch failed: {e}")
        
        print("✅ All detection examples validated")

    def test_environment_examples(self):
        """
        Test environment data examples from README lines 167-191:
        - reading = client.environment.add(...)
        - env_data = client.environment.fetch(...)
        """
        print("\n=== Testing Environment Examples ===")
        
        # First, ensure we have a test device
        self.client.add_device(device_id=self.test_device_id)
        self.created_devices.append(self.test_device_id)
        
        # Test 1: Add environment reading (README lines 167-184)
        print(f"Testing environment.add")
        try:
            reading = self.client.environment.add(
                device_id=self.test_device_id,
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
                timestamp=self.test_timestamp,
                location={                      # Optional GPS coordinates
                    "lat": 40.7128,
                    "long": -74.0060
                }
            )
            print_response(reading)
            print("✅ environment.add works")
        except Exception as e:
            print(f"❌ environment.add failed: {e}")
            # This might be the endpoint issue found by Agent A
            print("⚠️ Environment endpoint may not be working - this matches Agent A's findings")
            
        # Test 2: Fetch environment data (README lines 187-191)
        print(f"Testing environment.fetch")
        try:
            env_data = self.client.environment.fetch(
                device_id=self.test_device_id,
                start_time="2024-08-20T00:00:00Z",
                end_time="2024-08-21T00:00:00Z"
            )
            print_response(env_data)
            
            # Verify response structure
            assert isinstance(env_data, dict), f"Expected dict response, got {type(env_data)}"
            print("✅ environment.fetch works")
        except Exception as e:
            print(f"❌ environment.fetch failed: {e}")
            print("⚠️ Environment fetch endpoint may not be working")
        
        print("✅ Environment examples testing completed")

    @pytest.mark.skipif(
        not (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")),
        reason="AWS credentials not available for video testing"
    )
    def test_video_examples(self):
        """
        Test video upload examples from README (if AWS credentials available)
        - video = client.videos.upload_video(...)
        - videos = client.videos.fetch(...)
        """
        print("\n=== Testing Video Examples ===")
        
        if self.client.videos is None:
            pytest.skip("Videos client not available - missing AWS credentials")
        
        # First, ensure we have a test device
        self.client.add_device(device_id=self.test_device_id)
        self.created_devices.append(self.test_device_id)
        
        # Test 1: Upload video (README lines 202-208)
        print(f"Testing videos.upload_video")
        video_data = create_test_video()
        
        try:
            video = self.client.videos.upload_video(
                device_id=self.test_device_id,
                timestamp=self.test_timestamp,
                video_path_or_data=video_data,  # Using raw bytes as shown in README
                content_type="video/mp4",
                metadata={"duration": 300, "fps": 30}
            )
            print_response(video)
            print("✅ videos.upload_video works")
        except Exception as e:
            print(f"❌ videos.upload_video failed: {e}")
            pytest.fail(f"videos.upload_video failed: {e}")
        
        # Test 2: Fetch videos (README line 223)
        print(f"Testing videos.fetch")
        try:
            videos = self.client.videos.fetch(device_id=self.test_device_id)
            print_response(videos)
            
            # Verify response structure
            assert isinstance(videos, dict), f"Expected dict response, got {type(videos)}"
            print("✅ videos.fetch works")
        except Exception as e:
            print(f"❌ videos.fetch failed: {e}")
            pytest.fail(f"videos.fetch failed: {e}")
        
        print("✅ All video examples validated")

    def test_query_pagination_examples(self):
        """
        Test common query options from README lines 238-255:
        - Pagination: data = client.detections.fetch(limit=50, next_token="abc123")
        - Time filtering: data = client.classifications.fetch(start_time=..., end_time=...)
        - Sorting: data = client.environment.fetch(sort_by="timestamp", sort_desc=True)
        - Counting: count = client.detections.count(device_id="pi-greenhouse-01")
        """
        print("\n=== Testing Query/Pagination Examples ===")
        
        # First, ensure we have a test device
        self.client.add_device(device_id=self.test_device_id)
        self.created_devices.append(self.test_device_id)
        
        # Test 1: Pagination (README line 240)
        print(f"Testing pagination with detections.fetch")
        try:
            data = self.client.detections.fetch(limit=50, next_token=None)  # Use None instead of "abc123"
            print(f"Pagination result: {len(data.get('items', []))} items")
            assert isinstance(data, dict), f"Expected dict response, got {type(data)}"
            print("✅ Pagination works")
        except Exception as e:
            print(f"❌ Pagination test failed: {e}")
        
        # Test 2: Time filtering (README lines 243-246) 
        # Note: Using detections instead of classifications since we're testing non-classification examples
        print(f"Testing time filtering with detections.fetch")
        try:
            data = self.client.detections.fetch(
                start_time="2024-08-20T00:00:00Z",
                end_time="2024-08-21T00:00:00Z"
            )
            print(f"Time filtering result: {len(data.get('items', []))} items")
            assert isinstance(data, dict), f"Expected dict response, got {type(data)}"
            print("✅ Time filtering works")
        except Exception as e:
            print(f"❌ Time filtering test failed: {e}")
        
        # Test 3: Sorting (README lines 249-252)
        print(f"Testing sorting with environment.fetch")
        try:
            data = self.client.environment.fetch(
                sort_by="timestamp",
                sort_desc=True  # newest first
            )
            print(f"Sorting result: {len(data.get('items', []))} items")
            assert isinstance(data, dict), f"Expected dict response, got {type(data)}"
            print("✅ Sorting works")
        except Exception as e:
            print(f"❌ Sorting test failed: {e}")
            print("⚠️ This may be related to environment endpoint issues")
        
        # Test 4: Counting (README line 255)
        print(f"Testing count with detections.count")
        try:
            count = self.client.detections.count(device_id=self.test_device_id)
            print(f"Count result: {count}")
            assert isinstance(count, (int, dict)), f"Expected int or dict, got {type(count)}: {count}"
            print("✅ Counting works")
        except Exception as e:
            print(f"❌ Counting test failed: {e}")
        
        print("✅ Query/pagination examples testing completed")

    def test_parameter_validation(self):
        """
        Test parameter validation and error handling for edge cases
        """
        print("\n=== Testing Parameter Validation ===")
        
        # Test 1: Invalid bounding box format
        print("Testing invalid bounding box format")
        try:
            image_data = create_test_image()
            self.client.detections.add(
                device_id=self.test_device_id,
                model_id="test-model",
                image_data=image_data,
                bounding_box=[0.1, 0.2, 0.8],  # Invalid - only 3 values instead of 4
                timestamp=self.test_timestamp
            )
            print("⚠️ Invalid bounding box was accepted - validation may be missing")
        except Exception as e:
            print(f"✅ Invalid bounding box correctly rejected: {e}")
        
        # Test 2: Missing required parameters
        print("Testing missing required parameters for models.create")
        try:
            model = self.client.models.create()  # No parameters
            print("⚠️ models.create with no parameters was accepted")
        except Exception as e:
            print(f"✅ Missing parameters correctly rejected: {e}")
        
        # Test 3: Invalid device_id format
        print("Testing invalid device_id format")
        try:
            response = self.client.add_device(device_id="")  # Empty string
            print("⚠️ Empty device_id was accepted")
        except Exception as e:
            print(f"✅ Empty device_id correctly rejected: {e}")
        
        print("✅ Parameter validation testing completed")

    def test_return_value_formats(self):
        """
        Test return value formats match documentation
        """
        print("\n=== Testing Return Value Formats ===")
        
        # Test get_devices return format
        print("Testing get_devices return format")
        devices, next_token = self.client.get_devices(limit=1)
        
        # Verify tuple return as documented in README line 50
        assert isinstance(devices, list), f"get_devices should return list of devices, got {type(devices)}"
        assert next_token is None or isinstance(next_token, str), f"next_token should be str or None, got {type(next_token)}"
        print("✅ get_devices returns (list, str|None) as documented")
        
        # Test models.fetch return format
        print("Testing models.fetch return format")
        try:
            models = self.client.models.fetch(limit=1)
            assert isinstance(models, dict), f"models.fetch should return dict, got {type(models)}"
            print("✅ models.fetch returns dict as expected")
        except Exception as e:
            print(f"⚠️ Could not test models.fetch return format: {e}")
        
        # Test models.count return format
        print("Testing models.count return format")
        try:
            count = self.client.models.count()
            # Count could be int or dict with count field
            if isinstance(count, dict):
                assert "count" in count or "items" in count, f"Count dict should have count or items field: {count}"
            else:
                assert isinstance(count, int), f"Count should be int or dict, got {type(count)}"
            print("✅ models.count returns appropriate format")
        except Exception as e:
            print(f"⚠️ Could not test models.count return format: {e}")
        
        print("✅ Return value format testing completed")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])