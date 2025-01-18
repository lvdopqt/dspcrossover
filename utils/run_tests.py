# run_tests.py

import os

def run_tests(test_folder='tests'):
    """
    Run all test functions in the test folder and print PASS/FAIL status.
    """
    print("Running tests...")

    # List all test files in the test folder
    test_files = [f for f in os.listdir(test_folder) if f.startswith("test_") and f.endswith(".py")]

    if not test_files:
        print("No tests found.")
        return

    # Track the number of passed and failed tests
    passed = 0
    failed = 0

    # Run each test file
    for test_file in test_files:
        print(f"\nRunning tests in {test_file}...")
        try:
            # Open and execute the test file
            with open(f"{test_folder}/{test_file}", "r") as f:
                code = f.read()
                # Execute the test file
                exec(code, globals(), locals())
            print(f"[PASS] {test_file}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test_file}: {e}")
            failed += 1

    # Print summary
    print("\nTest summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("All tests completed.")

if __name__ == "__main__":
    # Run tests in the 'tests' folder
    run_tests("tests")