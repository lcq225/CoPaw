# -*- coding: utf-8 -*-
"""
Tests for error categorization system.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime

from copaw.utils.errors import (
    ErrorType,
    ErrorCategory,
    ErrorSeverity,
    get_error_type,
    get_category_errors,
    ErrorRecord,
    AutoErrorCatcher,
    auto_catch,
    catch_and_learn
)


class TestErrorTypes:
    """Test error type classification"""
    
    def test_get_known_error_type(self):
        """Test getting known error type"""
        error_type = get_error_type("FileNotFoundError")
        
        assert error_type.error_type == "FileNotFoundError"
        assert error_type.category == ErrorCategory.FILE_ERROR
        assert error_type.severity == ErrorSeverity.ERROR
        assert "file path" in error_type.suggestion.lower()
    
    def test_get_unknown_error_type(self):
        """Test getting unknown error type"""
        error_type = get_error_type("CustomUnknownError")
        
        assert error_type.error_type == "CustomUnknownError"
        assert error_type.category == ErrorCategory.UNKNOWN
        assert "Unknown error" in error_type.suggestion
    
    def test_get_category_errors(self):
        """Test getting errors by category"""
        file_errors = get_category_errors(ErrorCategory.FILE_ERROR)
        
        assert "FileNotFoundError" in file_errors
        assert isinstance(file_errors, list)
        assert len(file_errors) > 0
    
    def test_all_error_categories(self):
        """Test all error categories are defined"""
        categories = {
            ErrorCategory.FILE_ERROR,
            ErrorCategory.PERMISSION_ERROR,
            ErrorCategory.IMPORT_ERROR,
            ErrorCategory.DATABASE_ERROR,
            ErrorCategory.KEY_ERROR,
            ErrorCategory.TYPE_ERROR,
            ErrorCategory.VALUE_ERROR,
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.PARSE_ERROR,
            ErrorCategory.ATTRIBUTE_ERROR,
            ErrorCategory.INDEX_ERROR,
            ErrorCategory.RUNTIME_ERROR,
            ErrorCategory.UNKNOWN
        }
        
        assert len(categories) == 14  # All categories defined


class TestErrorRecord:
    """Test error record data structure"""
    
    def test_error_record_creation(self):
        """Test creating error record"""
        record = ErrorRecord(
            error_type="ValueError",
            error_message="Invalid value",
            function_name="test_func",
            timestamp="2026-04-01T12:00:00Z",
            traceback_str="Traceback...",
            category="value_error",
            severity="error",
            suggestion="Check value",
            related_skill=None,
            auto_fixable=False
        )
        
        assert record.error_type == "ValueError"
        assert record.error_message == "Invalid value"
        assert record.function_name == "test_func"
        assert record.category == "value_error"
    
    def test_error_record_to_dict(self):
        """Test converting error record to dictionary"""
        record = ErrorRecord(
            error_type="TypeError",
            error_message="Wrong type",
            function_name="test",
            timestamp="2026-04-01T12:00:00Z",
            traceback_str="Traceback...",
            category="type_error",
            severity="error",
            suggestion="Check types",
            auto_fixable=False
        )
        
        record_dict = record.to_dict()
        
        assert isinstance(record_dict, dict)
        assert record_dict["error_type"] == "TypeError"
        assert record_dict["category"] == "type_error"
    
    def test_error_record_to_json(self):
        """Test converting error record to JSON"""
        record = ErrorRecord(
            error_type="KeyError",
            error_message="Missing key",
            function_name="test",
            timestamp="2026-04-01T12:00:00Z",
            traceback_str="Traceback...",
            category="key_error",
            severity="warning",
            suggestion="Use .get()",
            auto_fixable=False
        )
        
        json_str = record.to_json()
        parsed = json.loads(json_str)
        
        assert isinstance(json_str, str)
        assert parsed["error_type"] == "KeyError"
        assert "missing key" in parsed["error_message"].lower()


class TestAutoErrorCatcher:
    """Test AutoErrorCatcher context manager"""
    
    def test_catcher_no_error(self):
        """Test catcher with no error"""
        with AutoErrorCatcher("test_op") as catcher:
            result = 1 + 1
        
        assert catcher.has_error is False
        assert catcher.error is None
        assert catcher.error_record is None
    
    def test_catcher_with_error(self):
        """Test catcher with error"""
        with AutoErrorCatcher("test_op") as catcher:
            result = 1 / 0
        
        assert catcher.has_error is True
        assert catcher.error is not None
        assert isinstance(catcher.error, ZeroDivisionError)
        assert catcher.error_record is not None
        assert catcher.error_record.error_type == "ZeroDivisionError"
    
    def test_catcher_get_suggestion(self):
        """Test getting suggestion from catcher"""
        with AutoErrorCatcher("test_op") as catcher:
            result = 1 / 0
        
        suggestion = catcher.get_suggestion()
        
        assert isinstance(suggestion, str)
        assert len(suggestion) > 0
    
    def test_catcher_get_category(self):
        """Test getting category from catcher"""
        with AutoErrorCatcher("test_op") as catcher:
            result = 1 / 0
        
        category = catcher.get_category()
        
        assert isinstance(category, str)
        assert category in ["type_error", "value_error", "runtime_error"]
    
    def test_catcher_save_to_file(self):
        """Test saving error to temp file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with AutoErrorCatcher(
                "test_op",
                save_to_file=True,
                temp_dir=temp_dir
            ) as catcher:
                result = 1 / 0
            
            assert catcher.temp_file_path is not None
            assert os.path.exists(catcher.temp_file_path)
            assert catcher.temp_file_path.startswith(temp_dir)
            
            # Verify file content
            with open(catcher.temp_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "operation" in data
                assert "error" in data
                assert data["operation"] == "test_op"


class TestAutoCatchDecorator:
    """Test auto_catch decorator"""
    
    def test_decorator_no_error(self):
        """Test decorator with no error"""
        @auto_catch()
        def good_func():
            return 42
        
        result = good_func()
        assert result == 42
    
    def test_decorator_with_error(self):
        """Test decorator with error"""
        @auto_catch()
        def bad_func():
            return 1 / 0
        
        with pytest.raises(ZeroDivisionError):
            bad_func()
    
    def test_decorator_custom_name(self):
        """Test decorator with custom operation name"""
        @auto_catch(operation_name="custom_op")
        def my_func():
            return 1 / 0
        
        with pytest.raises(ZeroDivisionError):
            my_func()
    
    def test_decorator_no_logging(self):
        """Test decorator with logging disabled"""
        @auto_catch(log_error=False)
        def silent_func():
            return 1 / 0
        
        with pytest.raises(ZeroDivisionError):
            silent_func()


class TestCatchAndLearn:
    """Test catch_and_learn function"""
    
    def test_catch_and_learn_basic(self):
        """Test basic catch_and_learn usage"""
        try:
            result = 1 / 0
        except Exception as e:
            record = catch_and_learn(e, "test_op")
            
            assert isinstance(record, ErrorRecord)
            assert record.error_type == "ZeroDivisionError"
            assert record.function_name == "test_op"
            assert record.suggestion is not None
    
    def test_catch_and_learn_file_error(self):
        """Test catching file error"""
        try:
            with open("nonexistent_file.txt", "r") as f:
                f.read()
        except Exception as e:
            record = catch_and_learn(e, "file_read")
            
            assert record.error_type == "FileNotFoundError"
            assert record.category == "file_error"
            assert "file path" in record.suggestion.lower()
    
    def test_catch_and_learn_key_error(self):
        """Test catching key error"""
        try:
            d = {"a": 1}
            value = d["b"]
        except Exception as e:
            record = catch_and_learn(e, "dict_access")
            
            assert record.error_type == "KeyError"
            assert record.category == "key_error"
            assert ".get()" in record.suggestion


class TestIntegration:
    """Integration tests"""
    
    def test_full_error_handling_flow(self):
        """Test complete error handling flow"""
        errors_caught = []
        
        @auto_catch(save_to_file=False)
        def risky_operation(value):
            if value < 0:
                raise ValueError("Negative value not allowed")
            return value ** 2
        
        # Test with valid input
        result = risky_operation(5)
        assert result == 25
        
        # Test with invalid input
        try:
            risky_operation(-1)
        except ValueError:
            pass  # Expected
        
        # Manual capture
        try:
            risky_operation(-2)
        except Exception as e:
            record = catch_and_learn(e, "manual_test")
            errors_caught.append(record)
        
        assert len(errors_caught) == 1
        assert errors_caught[0].error_type == "ValueError"
        assert errors_caught[0].category == "value_error"
    
    def test_multiple_error_types(self):
        """Test handling multiple error types"""
        test_cases = [
            (lambda: 1 / 0, "ZeroDivisionError"),
            (lambda: int("abc"), "ValueError"),
            (lambda: {"a": 1}["b"], "KeyError"),
            (lambda: [1, 2][10], "IndexError"),
        ]
        
        for func, expected_type in test_cases:
            try:
                func()
            except Exception as e:
                record = catch_and_learn(e, "multi_test")
                assert record.error_type == expected_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
