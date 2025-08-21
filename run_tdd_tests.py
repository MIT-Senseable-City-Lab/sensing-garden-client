#!/usr/bin/env python3
"""
Run TDD tests to demonstrate failing environment data tests.

This script runs the new TDD tests that are designed to fail, demonstrating
the current issue with environment data in classifications.

Expected outcome: All TDD tests should FAIL, showing that:
1. Client sends environment data under "data" field (wrong)
2. API doesn't return environment data (because it expects "environment" field)
3. Need to fix client to send "environment" field instead of "data"
"""

import subprocess
import sys

def run_tdd_tests():
    """Run the TDD tests and capture output."""
    
    print("=" * 80)
    print("RUNNING TDD TESTS FOR ENVIRONMENT DATA IN CLASSIFICATIONS")
    print("=" * 80)
    print()
    print("These tests are DESIGNED TO FAIL to demonstrate TDD approach.")
    print("They show the current client implementation issue.")
    print()
    
    # List of TDD test functions
    tdd_tests = [
        "test_add_classification_with_environment_tdd",
        "test_add_classification_with_partial_environment_tdd", 
        "test_add_classification_with_location_and_environment_tdd"
    ]
    
    failed_count = 0
    
    for test_name in tdd_tests:
        print(f"Running {test_name}...")
        print("-" * 60)
        
        try:
            # Run the test
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                f"tests/test_classifications.py::{test_name}",
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=".")
            
            if result.returncode != 0:
                failed_count += 1
                print(f"✗ {test_name} FAILED (as expected)")
                # Extract the key failure message
                lines = result.stdout.split('\n')
                for line in lines:
                    if "TDD FAILURE" in line and "AssertionError:" in line:
                        failure_msg = line.split("AssertionError: ")[-1]
                        print(f"  Failure reason: {failure_msg}")
                        break
            else:
                print(f"✓ {test_name} PASSED (unexpected!)")
                
        except Exception as e:
            print(f"✗ Error running {test_name}: {e}")
            failed_count += 1
            
        print()
    
    print("=" * 80)
    print("TDD TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if failed_count == len(tdd_tests):
        print(f"✓ SUCCESS: All {failed_count} TDD tests failed as expected!")
        print()
        print("This confirms the current issue:")
        print("- Client sends environment data under 'data' field")
        print("- New API schema expects 'environment' field")
        print("- Need to fix classifications.py line 106")
        print()
        print("Next step: Fix the client implementation and these tests should pass.")
        return True
    else:
        passed_count = len(tdd_tests) - failed_count
        print(f"✗ UNEXPECTED: {passed_count} tests passed, {failed_count} tests failed")
        print("TDD tests should all fail initially!")
        return False

if __name__ == "__main__":
    success = run_tdd_tests()
    sys.exit(0 if success else 1)