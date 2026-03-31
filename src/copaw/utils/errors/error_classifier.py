# -*- coding: utf-8 -*-
"""
Auto Error Catcher - Automatically capture and classify errors for CoPaw.

Features:
- Decorator-based automatic error capture
- Context manager error handling
- Manual error capture
- Automatic error classification
- Improvement suggestions generation

Usage:
    # Method 1: Decorator
    @auto_catch()
    def my_function():
        ...
    
    # Method 2: Context manager
    with AutoErrorCatcher("operation_name") as catcher:
        dangerous_operation()
        if catcher.has_error:
            print(f"Suggestion: {catcher.get_suggestion()}")
    
    # Method 3: Manual capture
    try:
        dangerous_operation()
    except Exception as e:
        error_record = catch_and_learn(e, "operation_name")
        print(f"Category: {error_record.category}")
"""

import functools
import logging
import traceback
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import os
import sys
import json
import tempfile

from .error_types import (
    ErrorType,
    ErrorCategory,
    ErrorSeverity,
    get_error_type,
    ERROR_TYPES_DB
)

logger = logging.getLogger(__name__)


@dataclass
class ErrorRecord:
    """Error record data structure"""
    
    error_type: str
    error_message: str
    function_name: str
    timestamp: str
    traceback_str: str
    category: str
    severity: str
    suggestion: str
    related_skill: Optional[str] = None
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class AutoErrorCatcher:
    """
    Automatic error catcher context manager.
    
    Example:
        with AutoErrorCatcher("my_operation") as catcher:
            dangerous_operation()
        
        if catcher.has_error:
            print(f"Error: {catcher.error}")
            print(f"Suggestion: {catcher.get_suggestion()}")
    """
    
    def __init__(
        self,
        operation_name: str,
        log_error: bool = True,
        save_to_file: bool = False,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize error catcher.
        
        Args:
            operation_name: Name of the operation for identification
            log_error: Whether to log errors (default: True)
            save_to_file: Whether to save error to temp file (default: False)
            temp_dir: Custom temp directory (default: system temp)
        """
        self.operation_name = operation_name
        self.log_error = log_error
        self.save_to_file = save_to_file
        self.temp_dir = temp_dir
        
        self.has_error = False
        self.error: Optional[Exception] = None
        self.error_record: Optional[ErrorRecord] = None
        self.temp_file_path: Optional[str] = None
    
    def __enter__(self):
        """Enter context"""
        self.has_error = False
        self.error = None
        self.error_record = None
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - catch and process errors"""
        if exc_val is not None:
            self.has_error = True
            self.error = exc_val
            
            # Create error record
            self.error_record = self._create_error_record(
                error=exc_val,
                traceback_str=traceback.format_exc()
            )
            
            # Log error
            if self.log_error:
                self._log_error()
            
            # Save to file
            if self.save_to_file:
                self.temp_file_path = self._save_to_file(exc_val, exc_tb)
            
            # Don't suppress the exception
            return False
        
        return True
    
    def _create_error_record(
        self,
        error: Exception,
        traceback_str: str
    ) -> ErrorRecord:
        """Create error record"""
        error_name = type(error).__name__
        error_type_info = get_error_type(error_name)
        
        return ErrorRecord(
            error_type=error_name,
            error_message=str(error),
            function_name=self.operation_name,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            traceback_str=traceback_str,
            category=error_type_info.category.value,
            severity=error_type_info.severity.value,
            suggestion=error_type_info.suggestion,
            related_skill=error_type_info.related_skill,
            auto_fixable=error_type_info.auto_fixable
        )
    
    def _log_error(self):
        """Log error message"""
        if self.error_record:
            logger.error(
                f"Error in {self.operation_name}: "
                f"[{self.error_record.category}] "
                f"{self.error_record.error_type} - "
                f"{self.error_record.error_message}"
            )
    
    def _save_to_file(
        self,
        exc: BaseException,
        tb: Optional[Any] = None
    ) -> str:
        """Save error to temp file"""
        try:
            fd, path = tempfile.mkstemp(
                prefix=f"copaw_error_{self.operation_name}_",
                suffix=".json",
                dir=self.temp_dir
            )
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump({
                    "operation": self.operation_name,
                    "error": self.error_record.to_dict() if self.error_record else None,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            return path
            
        except Exception as e:
            logger.error(f"Failed to save error to file: {e}")
            return None
    
    def get_suggestion(self) -> str:
        """Get improvement suggestion"""
        if self.error_record:
            return self.error_record.suggestion
        return "No error recorded"
    
    def get_category(self) -> Optional[str]:
        """Get error category"""
        if self.error_record:
            return self.error_record.category
        return None


def auto_catch(
    operation_name: Optional[str] = None,
    log_error: bool = True,
    save_to_file: bool = False
) -> Callable:
    """
    Decorator for automatic error capture.
    
    Args:
        operation_name: Operation name (default: function name)
        log_error: Whether to log errors (default: True)
        save_to_file: Whether to save errors to temp file (default: False)
    
    Returns:
        Decorated function
    
    Example:
        @auto_catch()
        def my_function():
            return 1 / 0
        
        @auto_catch("custom_name", save_to_file=True)
        def another_function():
            raise ValueError("test")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            catcher = AutoErrorCatcher(
                op_name,
                log_error=log_error,
                save_to_file=save_to_file
            )
            
            try:
                with catcher:
                    return func(*args, **kwargs)
            except Exception as e:
                # Exception already handled by catcher
                raise
        
        return wrapper
    return decorator


def catch_and_learn(
    error: Exception,
    operation_name: str,
    log_error: bool = True
) -> ErrorRecord:
    """
    Manually catch and learn from an error.
    
    Args:
        error: Exception instance
        operation_name: Operation name
        log_error: Whether to log error (default: True)
    
    Returns:
        ErrorRecord instance
    
    Example:
        try:
            dangerous_operation()
        except Exception as e:
            error_record = catch_and_learn(e, "dangerous_op")
            print(f"Suggestion: {error_record.suggestion}")
    """
    traceback_str = traceback.format_exc()
    error_name = type(error).__name__
    error_type_info = get_error_type(error_name)
    
    record = ErrorRecord(
        error_type=error_name,
        error_message=str(error),
        function_name=operation_name,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        traceback_str=traceback_str,
        category=error_type_info.category.value,
        severity=error_type_info.severity.value,
        suggestion=error_type_info.suggestion,
        related_skill=error_type_info.related_skill,
        auto_fixable=error_type_info.auto_fixable
    )
    
    if log_error:
        logger.error(
            f"Error in {operation_name}: "
            f"[{record.category}] {record.error_type} - "
            f"{record.error_message}"
        )
    
    return record
