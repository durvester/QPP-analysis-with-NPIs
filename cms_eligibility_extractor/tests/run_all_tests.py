"""
Test runner for comprehensive test suite.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests(test_type="all", verbose=False, coverage=False):
    """
    Run tests based on type.
    
    Args:
        test_type: Type of tests to run (all, unit, integration, e2e, web, cli)
        verbose: Whether to run in verbose mode
        coverage: Whether to generate coverage report
    """
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov=web", "--cov-report=html", "--cov-report=term"])
    
    # Test file patterns based on type
    test_patterns = {
        "unit": [
            "tests/test_api_client_comprehensive.py",
            "tests/test_rate_limiter.py",
            "tests/test_models.py",
            "tests/test_web_forms.py"
        ],
        "integration": [
            "tests/test_api_client_enhanced.py",
            "tests/test_web_routes.py"
        ],
        "e2e": [
            "tests/test_e2e_cli.py",
            "tests/test_e2e_web.py"
        ],
        "web": [
            "tests/test_web_*.py",
            "tests/test_e2e_web.py"
        ],
        "cli": [
            "tests/test_e2e_cli.py"
        ],
        "all": [
            "tests/"
        ]
    }
    
    if test_type in test_patterns:
        cmd.extend(test_patterns[test_type])
    else:
        print(f"Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_patterns.keys())}")
        return 1
    
    # Add additional pytest options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "-x"  # Stop on first failure
    ])
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {test_type.title()} tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_type.title()} tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest:")
        print("   pip install pytest pytest-cov")
        return 1


def check_dependencies():
    """Check if required test dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-cov",
        "flask",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required test dependencies are installed")
    return True


def run_test_suite():
    """Run the complete test suite in order."""
    test_order = [
        ("unit", "Unit tests"),
        ("integration", "Integration tests"),
        ("e2e", "End-to-end tests")
    ]
    
    results = {}
    
    for test_type, description in test_order:
        print(f"\n{'='*60}")
        print(f"Running {description}")
        print(f"{'='*60}")
        
        result = run_tests(test_type, verbose=True)
        results[test_type] = result
        
        if result != 0:
            print(f"\n❌ {description} failed. Stopping test suite.")
            break
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*60}")
    
    for test_type, description in test_order:
        if test_type in results:
            status = "✅ PASSED" if results[test_type] == 0 else "❌ FAILED"
            print(f"{description:20} {status}")
        else:
            print(f"{description:20} ⏸️ SKIPPED")
    
    total_failed = sum(1 for result in results.values() if result != 0)
    
    if total_failed == 0:
        print(f"\n🎉 All test suites passed!")
        return 0
    else:
        print(f"\n💥 {total_failed} test suite(s) failed")
        return 1


def generate_test_report():
    """Generate comprehensive test report with coverage."""
    print("Generating comprehensive test report...")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov=web", 
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage.xml",
        "--junitxml=test-results.xml",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Test report generated successfully!")
        print("📁 HTML coverage report: htmlcov/index.html")
        print("📄 XML coverage report: coverage.xml")
        print("📄 JUnit test results: test-results.xml")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test report generation failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run CMS QPP Eligibility Extractor tests")
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "e2e", "web", "cli", "suite", "report"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check test dependencies"
    )
    
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        return 0 if check_dependencies() else 1
    
    # Check dependencies before running tests
    if not check_dependencies():
        return 1
    
    # Handle special test types
    if args.test_type == "suite":
        return run_test_suite()
    elif args.test_type == "report":
        return generate_test_report()
    else:
        return run_tests(args.test_type, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())