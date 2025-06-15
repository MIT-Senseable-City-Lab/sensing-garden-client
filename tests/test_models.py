#!/usr/bin/env python3
"""
Tests for the Sensing Garden API model endpoints.
This module tests both uploading and retrieving ML models.
"""
import argparse
import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

import requests

from .test_utils import (
    get_client,
    generate_random_string,
    print_response
)

import pytest
from tests.conftest import test_vars

@pytest.mark.usefixtures('model_id', 'timestamp')
def test_create_model(model_id=None, timestamp=None) -> None:
    """
    Test uploading a model to the Sensing Garden API.
    
    Args:
        model_id: Optional model ID to use (generates a new one if not provided)
        timestamp: Optional timestamp to use (defaults to current time)
        
    Returns:
        Tuple of (success, model_id, timestamp)
    """
    # Use the shared static model_id and timestamp
    model_id = model_id or test_vars['model_id']
    request_timestamp = timestamp or test_vars['timestamp']
    client = get_client()
    print(f"\n\nTesting MODEL UPLOAD with model_id: {model_id}")
    try:
        response_data = client.models.create(
            model_id=model_id,
            name=f"Test Model {model_id}",
            version="1.0.0",
            description=f"Test model created at {request_timestamp}",
            timestamp=request_timestamp
        )
        print_response(response_data)
        print(f"\n✅ Model creation successful!")
        success = True
    except requests.exceptions.RequestException as e:
        print(f"❌ Model upload failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        success = False
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        success = False
    assert success, f"Model test failed at {request_timestamp}"

def test_fetch_models(model_id: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, sort_by: Optional[str] = None, sort_desc: bool = False):
    success, response_data = _fetch_models(model_id, start_time, end_time, sort_by, sort_desc)
    assert success, f"Model fetch failed. Data: {response_data}"

def _fetch_models(
    model_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test retrieving models from the Sensing Garden API.
    
    Args:
        model_id: Optional model ID to filter by
        start_time: Optional start time for filtering (ISO-8601)
        end_time: Optional end time for filtering (ISO-8601)
        sort_by: Optional field to sort by
        sort_desc: Whether to sort descending
    Returns:
        Tuple of (success, response_data)
    """
    client = get_client()
    
    print(f"\n\nTesting MODEL FETCH")
    try:
        response_data = client.models.fetch(
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        print_response(response_data)
        print(f"\n✅ Model fetch successful!")
        success = True
    except Exception as e:
        print(f"❌ Error in fetching models: {str(e)}")
        response_data = None
        success = False
    return success, response_data


def test_fetch_all_models_and_check_created():
    """
    Fetch all models and assert the test model is present in the results.
    """
    from tests.conftest import test_vars
    client = get_client()
    print("\n\nTesting FETCH ALL MODELS")
    try:
        response_data = client.models.fetch()
        print_response(response_data)
        all_ids = [item.get('id') for item in response_data.get('items', [])]
        print(f"All model IDs: {all_ids}")
        assert test_vars['model_id'] in all_ids, f"Test model_id {test_vars['model_id']} not found in model list!"
        print(f"✅ Newly created model_id {test_vars['model_id']} found in model list!")
    except Exception as e:
        print(f"❌ Error in fetching all models: {str(e)}")
        assert False, f"Exception during fetch all models: {e}"

def test_fetch_models_with_time_range(
    model_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test retrieving models from the Sensing Garden API.
    
    Args:
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
    
    print(f"\n\nTesting MODEL FETCH" + (f" with model_id: {model_id}" if model_id else ""))
    print(f"Searching from {start_time} to {end_time}")
    
    try:
        # Use the models.fetch method to get models
        data = client.models.fetch(
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            limit=10,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        # Check if we got any results
        if data.get('items') and len(data['items']) > 0:
            print(f"✅ Model fetch successful! Found {len(data['items'])} models.")
            
            # Print details of each model
            for i, model in enumerate(data['items']):
                print(f"\nModel {i+1}:")
                print(f"  Model ID: {model.get('model_id')}")
                print(f"  Name: {model.get('name')}")
                print(f"  Version: {model.get('version')}")
                print(f"  Description: {model.get('description')}")
                print(f"  Type: {model.get('model_type')}")
                print(f"  Framework: {model.get('framework')}")
                print(f"  Timestamp: {model.get('timestamp')}")
                
                # Print metadata if available
                if 'metadata' in model:
                    print(f"  Metadata: {model.get('metadata')}")
            
            assert True
        else:
            print(f"❌ No models found in the specified time range.")
            assert False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Model fetch request failed: {str(e)}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
        assert False
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        assert False

def add_test_models(num_models: int = 3) -> List[str]:
    """
    Add test models.
    
    Args:
        num_models: Number of models to add
        
    Returns:
        List of created model IDs
    """
    print(f"\nAdding {num_models} test models")
    
    model_ids = []
    for i in range(num_models):
        success, model_id, _ = test_create_model()
        if success:
            model_ids.append(model_id)
    
    assert len(model_ids) == num_models

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Sensing Garden API model endpoints')
    parser.add_argument('--model-id', type=str, default=None,
                      help='Model ID to use for testing')
    parser.add_argument('--timestamp', type=str, help='Optional timestamp to use for testing')
    parser.add_argument('--upload', action='store_true', help='Test model creation')
    parser.add_argument('--fetch', action='store_true', help='Test model fetch')
    parser.add_argument('--add-test-data', action='store_true', help='Add test models')
    parser.add_argument('--num-models', type=int, default=3, help='Number of test models to add')
    
    args = parser.parse_args()
    
    # Use provided timestamp or generate a new one
    timestamp = args.timestamp or datetime.now().isoformat()
    
    # Run the appropriate tests
    success = True
    
    # Default to running both upload and fetch if neither is specified
    run_upload = args.upload or (not args.upload and not args.fetch)
    run_fetch = args.fetch or (not args.upload and not args.fetch)
    
    # Test model creation
    if run_upload:
        upload_success, model_id, _ = test_create_model(args.model_id, timestamp)
        success &= upload_success
    
    # Add test data if requested
    if args.add_test_data:
        model_ids = add_test_models(args.num_models)
        success &= len(model_ids) == args.num_models
    
    # Test model fetch
    if run_fetch:
        fetch_success, _ = test_fetch_models(args.model_id)
        success &= fetch_success
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
