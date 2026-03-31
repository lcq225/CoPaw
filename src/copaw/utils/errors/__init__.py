# -*- coding: utf-8 -*-
"""
Error categorization system for CoPaw.

This module provides automatic error capture, classification, and
improvement suggestions for CoPaw agents and skills.

Example usage:
    from copaw.utils.errors import auto_catch, AutoErrorCatcher, catch_and_learn
    
    # Method 1: Decorator
    @auto_catch()
    def my_function():
        return 1 / 0
    
    # Method 2: Context manager
    with AutoErrorCatcher("operation") as catcher:
        dangerous_task()
        if catcher.has_error:
            print(f"Suggestion: {catcher.get_suggestion()}")
    
    # Method 3: Manual capture
    try:
        complex_calculation()
    except Exception as e:
        error_record = catch_and_learn(e, "calculation")
        print(f"Category: {error_record.category}")
"""

from .error_types import (
    ErrorType,
    ErrorCategory,
    ErrorSeverity,
    get_error_type,
    get_category_errors,
    ERROR_TYPES_DB
)

from .error_classifier import (
    ErrorRecord,
    AutoErrorCatcher,
    auto_catch,
    catch_and_learn
)

__all__ = [
    # Error types
    "ErrorType",
    "ErrorCategory",
    "ErrorSeverity",
    "get_error_type",
    "get_category_errors",
    "ERROR_TYPES_DB",
    
    # Error catcher
    "ErrorRecord",
    "AutoErrorCatcher",
    "auto_catch",
    "catch_and_learn",
]
