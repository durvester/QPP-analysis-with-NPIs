#!/usr/bin/env python3
"""
Simple test runner for the CMS Eligibility Extractor.
Run this to execute all tests and validate the system.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests and return exit code."""
    print("=" * 60)
    print("CMS QPP Eligibility Extractor - Test Suite")
    print("=" * 60)
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Try to import pytest
        import pytest
        
        # Run tests
        test_args = [
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "tests/",  # Test directory
        ]
        
        print("Running tests with pytest...")
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED!")
            print("=" * 60)
        
        return exit_code
        
    except ImportError:
        print("pytest not found. Installing pytest...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
            import pytest
            return pytest.main(["-v", "tests/"])
        except Exception as e:
            print(f"Error installing or running pytest: {e}")
            print("\nFalling back to basic test runner...")
            return run_basic_tests()


def run_basic_tests():
    """Basic test runner without pytest."""
    print("Running basic validation tests...")
    
    try:
        # Test imports
        print("Testing imports...")
        from src.processors.npi_reader import NPIReader
        from src.models.flexible_schema import EligibilityResponse
        from src.api.cms_client import CMSEligibilityClient
        from src.exporters.csv_exporter import CSVExporter
        print("✅ All imports successful")
        
        # Test NPI validation
        print("Testing NPI validation...")
        reader = NPIReader("dummy.csv")
        assert reader.validate_npi("1234567890") == True
        assert reader.validate_npi("123456789") == False
        assert reader.validate_npi("12345678901") == False
        assert reader.validate_npi("123456789a") == False
        print("✅ NPI validation tests passed")
        
        # Test schema validation
        print("Testing schema validation...")
        sample_data = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        response = EligibilityResponse(**sample_data)
        assert response.data.npi == "1234567890"
        print("✅ Schema validation tests passed")
        
        # Test API client creation
        print("Testing API client creation...")
        client = CMSEligibilityClient()
        assert client is not None
        client.close()
        print("✅ API client creation test passed")
        
        print("\n" + "=" * 60)
        print("✅ ALL BASIC TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)