#!/usr/bin/env python3
"""
End-to-End Test Runner for Phase 8 Features

This script runs all end-to-end tests for the Phase 8 polish and cross-cutting concerns:
- T097: Comprehensive error handling
- T098: Security headers
- T099: API documentation
- T100: Comprehensive logging
- T101: Accessibility (frontend)
- T102: Performance optimization
- T103: Deployment configurations (tested via validation)
- T104: User documentation (validated via structure)
- T105: End-to-end testing (this script)
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all end-to-end tests"""
    print("Starting Phase 8 End-to-End Tests...")
    print("=" * 50)

    # Change to the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    test_files = [
        "e2e/test_phase8_features.py",
        "e2e/test_security_features.py",
        "e2e/test_error_handling.py",
        "e2e/test_logging_features.py",
        "e2e/test_performance_features.py"
    ]

    all_passed = True
    results = []

    for test_file in test_files:
        print(f"\nRunning {test_file}...")
        print("-" * 30)

        try:
            # Run the test with pytest
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                str(Path(test_file)),
                "-v",  # verbose
                "--tb=short"  # short traceback
            ], capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                status = "✅ PASSED"
                print(f"{status}")
                results.append((test_file, True, result.stdout))
            else:
                status = "❌ FAILED"
                print(f"{status}")
                print("STDOUT:")
                print(result.stdout)
                print("STDERR:")
                print(result.stderr)
                results.append((test_file, False, result.stderr))
                all_passed = False

        except subprocess.TimeoutExpired:
            status = " TIMEOUT"
            print(f"❌ {status}")
            results.append((test_file, False, "Test timed out"))
            all_passed = False
        except Exception as e:
            status = " ERROR"
            print(f"❌ {status}")
            print(f"Error: {str(e)}")
            results.append((test_file, False, str(e)))
            all_passed = False

    # Print summary
    print("\n" + "=" * 50)
    print("END-TO-END TEST SUMMARY")
    print("=" * 50)

    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)

    for test_file, passed, _ in results:
        status = "✅" if passed else "❌"
        print(f"{status} {test_file}")

    print(f"\nTotal: {passed_count}/{total_count} test suites passed")

    if all_passed:
        print("\n🎉 All end-to-end tests passed!")
        print("Phase 8 features are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test suite(s) failed.")
        print("Please check the output above for details.")
        return 1


def validate_deployment_configs():
    """Validate deployment configuration files exist and are properly structured"""
    print("\nValidating deployment configurations...")
    print("-" * 35)

    deploy_dir = Path(__file__).parent.parent.parent / "deploy"
    required_files = [
        "docker/Dockerfile.backend",
        "docker/Dockerfile.frontend",
        "docker/docker-compose.prod.yml",
        "docker/docker-compose.dev.yml",
        "kubernetes/production.yaml",
        "README.md",
        "production_config.py",
        "start_production.sh",
        "ai-textbook.service",
        ".env.production.example"
    ]

    all_present = True
    for file_path in required_files:
        full_path = deploy_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False

    if all_present:
        print("✅ All deployment configuration files are present")
    else:
        print("⚠️  Some deployment configuration files are missing")

    return all_present


def validate_user_documentation():
    """Validate user documentation exists and is properly structured"""
    print("\nValidating user documentation...")
    print("-" * 32)

    docs_dir = Path(__file__).parent.parent.parent / "docs" / "user-guide"
    required_docs = [
        "index.md",
        "onboarding.md",
        "getting-started.md",
        "translation-features.md",
        "personalization.md",
        "accessibility.md",
        "troubleshooting.md",
        "faq.md",
        "_category_.json"
    ]

    all_present = True
    for doc_file in required_docs:
        full_path = docs_dir / doc_file
        if full_path.exists():
            print(f"✅ {doc_file}")
        else:
            print(f"❌ {doc_file} - MISSING")
            all_present = False

    if all_present:
        print("✅ All user documentation files are present")
    else:
        print("⚠️  Some user documentation files are missing")

    return all_present


def main():
    """Main function to run all validations and tests"""
    print("AI-Native Textbook - Phase 8 Validation Suite")
    print("Testing: Polish & Cross-Cutting Concerns")
    print()

    # Validate deployment configurations
    deploy_ok = validate_deployment_configs()

    # Validate user documentation
    docs_ok = validate_user_documentation()

    # Run end-to-end tests
    tests_result = run_tests()

    # Overall result
    print("\n" + "=" * 50)
    print("OVERALL VALIDATION RESULT")
    print("=" * 50)

    results = [
        ("Deployment Configs", deploy_ok),
        ("User Documentation", docs_ok),
        ("End-to-End Tests", tests_result == 0)
    ]

    all_good = True
    for name, status in results:
        status_text = "✅ PASS" if status else "❌ FAIL"
        print(f"{name}: {status_text}")
        if not status:
            all_good = False

    if all_good:
        print(f"\n🎉 All Phase 8 validation checks passed!")
        print("The polish and cross-cutting concerns implementation is complete and validated.")
        return 0
    else:
        print(f"\n⚠️  Some validation checks failed.")
        print("Please address the issues before considering Phase 8 complete.")
        return 1


if __name__ == "__main__":
    sys.exit(main())