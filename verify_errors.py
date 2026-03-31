# -*- coding: utf-8 -*-
"""
Simple verification script for error categorization system.
Run this to verify the code works before running full pytest suite.
"""

import sys
import os

# Add CoPaw src to path
sys.path.insert(0, r'D:\github\CoPaw\src')

print("=" * 60)
print("Error Categorization System - Verification")
print("=" * 60)

# Test 1: Import modules
print("\n[Test 1] Importing modules...")
try:
    from copaw.utils.errors import (
        ErrorCategory,
        ErrorSeverity,
        ErrorType,
        get_error_type,
        AutoErrorCatcher,
        auto_catch,
        catch_and_learn
    )
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Error type classification
print("\n[Test 2] Testing error type classification...")
error_type = get_error_type("FileNotFoundError")
assert error_type.category == ErrorCategory.FILE_ERROR
assert "file" in error_type.suggestion.lower()
print(f"✅ FileNotFoundError: {error_type.category.value}")

error_type = get_error_type("KeyError")
assert error_type.category == ErrorCategory.KEY_ERROR
assert ".get()" in error_type.suggestion
print(f"✅ KeyError: {error_type.category.value}")

error_type = get_error_type("ValueError")
assert error_type.category == ErrorCategory.VALUE_ERROR
print(f"✅ ValueError: {error_type.category.value}")

# Test 3: AutoErrorCatcher context manager
print("\n[Test 3] Testing AutoErrorCatcher...")
try:
    with AutoErrorCatcher("test_division") as catcher:
        result = 1 / 0
except ZeroDivisionError:
    assert catcher.has_error is True
    assert catcher.error_record is not None
    print(f"✅ Caught error: {catcher.error_record.error_type}")
    print(f"✅ Category: {catcher.error_record.category}")
    print(f"✅ Suggestion: {catcher.error_record.suggestion[:50]}...")

# Test 4: auto_catch decorator
print("\n[Test 4] Testing auto_catch decorator...")
@auto_catch("decorated_function")
def test_func():
    return int("abc")

try:
    test_func()
except ValueError:
    print("✅ Decorator caught ValueError")

# Test 5: catch_and_learn function
print("\n[Test 5] Testing catch_and_learn...")
try:
    d = {"a": 1}
    value = d["b"]
except Exception as e:
    record = catch_and_learn(e, "dict_access")
    assert record.error_type == "KeyError"
    assert record.category == "key_error"
    print(f"✅ Manual capture: {record.error_type} -> {record.category}")

# Test 6: All error categories
print("\n[Test 6] Testing all error categories...")
categories = [
    "FileNotFoundError",
    "PermissionError",
    "ModuleNotFoundError",
    "KeyError",
    "TypeError",
    "ValueError",
    "TimeoutError",
    "ConnectionError",
    "AttributeError",
    "IndexError",
]

for error_name in categories:
    error_type = get_error_type(error_name)
    assert error_type.category != ErrorCategory.UNKNOWN, f"{error_name} should be categorized"
    print(f"  ✅ {error_name:25} -> {error_type.category.value}")

# Test 7: Unknown error
print("\n[Test 7] Testing unknown error handling...")
unknown = get_error_type("CustomUnknownError")
assert unknown.category == ErrorCategory.UNKNOWN
print(f"✅ Unknown error handled: {unknown.category.value}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe error categorization system is working correctly!")
print("Ready for pytest full test suite and PR submission.")
