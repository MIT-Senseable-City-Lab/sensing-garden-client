#!/usr/bin/env python3
"""
Debug test for environment endpoint issues found by Agent A and confirmed in validation.

This test investigates the specific error with environment.add() to understand
what's causing the 400 Bad Request error.
"""
import pytest
import uuid
import requests
from tests.test_utils import get_client

class TestEnvironmentEndpointDebug:
    """Debug tests for environment endpoint"""

    def setup_method(self):
        """Setup for each test method"""
        self.client = get_client()
        self.test_device_id = f"env-debug-device-{uuid.uuid4().hex[:8]}"

    def teardown_method(self):
        """Cleanup after each test method"""
        try:
            self.client.delete_device(self.test_device_id)
        except Exception:
            pass

    def test_environment_add_minimal_data(self):
        """
        Test environment.add with minimal required data to isolate the issue.
        """
        # First create a test device
        self.client.add_device(device_id=self.test_device_id)
        
        print(f"Testing environment.add with minimal data for device: {self.test_device_id}")
        
        try:
            # Try with minimal data first
            response = self.client.environment.add(
                device_id=self.test_device_id,
                data={
                    "ambient_temperature": 20.0,
                    "ambient_humidity": 50.0
                },
                timestamp="2024-08-21T12:00:00Z"
            )
            print(f"✅ Minimal environment.add succeeded: {response}")
        except requests.HTTPError as e:
            print(f"❌ Minimal environment.add failed with HTTP {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            try:
                error_json = e.response.json()
                print(f"Error details: {error_json}")
            except:
                print("Could not parse error response as JSON")
        except Exception as e:
            print(f"❌ Minimal environment.add failed with: {type(e).__name__}: {e}")

    def test_environment_add_full_data_as_readme(self):
        """
        Test environment.add with the exact data from README example.
        """
        # First create a test device
        self.client.add_device(device_id=self.test_device_id)
        
        print(f"Testing environment.add with full README data for device: {self.test_device_id}")
        
        try:
            # Use the exact data from README
            response = self.client.environment.add(
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
                timestamp="2024-08-21T12:00:00Z",
                location={                      # Optional GPS coordinates
                    "lat": 40.7128,
                    "long": -74.0060
                }
            )
            print(f"✅ Full README environment.add succeeded: {response}")
        except requests.HTTPError as e:
            print(f"❌ Full README environment.add failed with HTTP {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            try:
                error_json = e.response.json()
                print(f"Error details: {error_json}")
            except:
                print("Could not parse error response as JSON")
        except Exception as e:
            print(f"❌ Full README environment.add failed with: {type(e).__name__}: {e}")

    def test_environment_add_without_location(self):
        """
        Test environment.add without the optional location parameter.
        """
        # First create a test device
        self.client.add_device(device_id=self.test_device_id)
        
        print(f"Testing environment.add without location for device: {self.test_device_id}")
        
        try:
            response = self.client.environment.add(
                device_id=self.test_device_id,
                data={
                    "pm1p0": 8.2,
                    "pm2p5": 15.7,
                    "ambient_temperature": 24.5,
                    "ambient_humidity": 68.2
                },
                timestamp="2024-08-21T12:00:00Z"
                # location parameter omitted
            )
            print(f"✅ Environment.add without location succeeded: {response}")
        except requests.HTTPError as e:
            print(f"❌ Environment.add without location failed with HTTP {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        except Exception as e:
            print(f"❌ Environment.add without location failed with: {type(e).__name__}: {e}")

    def test_environment_fetch_works(self):
        """
        Verify that environment.fetch works (as seen in validation tests).
        """
        print("Testing that environment.fetch works")
        
        try:
            response = self.client.environment.fetch(
                device_id=self.test_device_id,
                start_time="2024-08-20T00:00:00Z",
                end_time="2024-08-21T00:00:00Z"
            )
            print(f"✅ Environment.fetch works: {response}")
        except Exception as e:
            print(f"❌ Environment.fetch failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])