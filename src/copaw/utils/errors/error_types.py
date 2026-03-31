# -*- coding: utf-8 -*-
"""
Error types for CoPaw error categorization system.

This module defines error type enumerations and classification schemas
for automatic error categorization and analysis.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict


class ErrorCategory(Enum):
    """Error category enumeration"""
    
    FILE_ERROR = "file_error"
    PERMISSION_ERROR = "permission_error"
    IMPORT_ERROR = "import_error"
    DATABASE_ERROR = "database_error"
    KEY_ERROR = "key_error"
    TYPE_ERROR = "type_error"
    VALUE_ERROR = "value_error"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    ATTRIBUTE_ERROR = "attribute_error"
    INDEX_ERROR = "index_error"
    RUNTIME_ERROR = "runtime_error"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    
    CRITICAL = "critical"  # System crash, data loss
    ERROR = "error"        # Operation failed
    WARNING = "warning"    # Operation completed with issues
    INFO = "info"          # Informational errors


@dataclass
class ErrorType:
    """Error type data structure"""
    
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    suggestion: str
    related_skill: Optional[str] = None
    auto_fixable: bool = False


# Error classification database
ERROR_TYPES_DB: Dict[str, ErrorType] = {
    "FileNotFoundError": ErrorType(
        error_type="FileNotFoundError",
        category=ErrorCategory.FILE_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion=(
            "Check if file path exists. "
            "Use os.path.exists() for pre-check."
        ),
        auto_fixable=False
    ),
    "PermissionError": ErrorType(
        error_type="PermissionError",
        category=ErrorCategory.PERMISSION_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion=(
            "Check file/directory permissions. "
            "Consider running with elevated privileges."
        ),
        auto_fixable=False
    ),
    "ModuleNotFoundError": ErrorType(
        error_type="ModuleNotFoundError",
        category=ErrorCategory.IMPORT_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion=(
            "Check if module is installed. "
            "Try: pip install <module-name>"
        ),
        related_skill="package_manager",
        auto_fixable=True
    ),
    "sqlite3.OperationalError": ErrorType(
        error_type="sqlite3.OperationalError",
        category=ErrorCategory.DATABASE_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion=(
            "Check if database is locked or corrupted. "
            "Consider closing other connections."
        ),
        auto_fixable=False
    ),
    "KeyError": ErrorType(
        error_type="KeyError",
        category=ErrorCategory.KEY_ERROR,
        severity=ErrorSeverity.WARNING,
        suggestion=(
            "Check if dictionary/JSON key exists. "
            "Use .get() method for safe access."
        ),
        auto_fixable=False
    ),
    "TypeError": ErrorType(
        error_type="TypeError",
        category=ErrorCategory.TYPE_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion=(
            "Check if data types match expected types. "
            "Add type hints for clarity."
        ),
        auto_fixable=False
    ),
    "ValueError": ErrorType(
        error_type="ValueError",
        category=ErrorCategory.VALUE_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion="Check if value is within expected range or format.",
        auto_fixable=False
    ),
    "TimeoutError": ErrorType(
        error_type="TimeoutError",
        category=ErrorCategory.TIMEOUT_ERROR,
        severity=ErrorSeverity.WARNING,
        suggestion="Increase timeout value or check network connection.",
        auto_fixable=False
    ),
    "ConnectionError": ErrorType(
        error_type="ConnectionError",
        category=ErrorCategory.NETWORK_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion="Check network connection status. Verify endpoint availability.",
        auto_fixable=False
    ),
    "json.JSONDecodeError": ErrorType(
        error_type="json.JSONDecodeError",
        category=ErrorCategory.PARSE_ERROR,
        severity=ErrorSeverity.WARNING,
        suggestion="Check JSON format. Use JSON validator to verify syntax.",
        auto_fixable=False
    ),
    "AttributeError": ErrorType(
        error_type="AttributeError",
        category=ErrorCategory.ATTRIBUTE_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion="Check if object has the attribute. Use hasattr() for safe access.",
        auto_fixable=False
    ),
    "IndexError": ErrorType(
        error_type="IndexError",
        category=ErrorCategory.INDEX_ERROR,
        severity=ErrorSeverity.WARNING,
        suggestion="Check if index is within list/tuple bounds.",
        auto_fixable=False
    ),
    "RuntimeError": ErrorType(
        error_type="RuntimeError",
        category=ErrorCategory.RUNTIME_ERROR,
        severity=ErrorSeverity.ERROR,
        suggestion="Check runtime conditions and prerequisites.",
        auto_fixable=False
    ),
}


def get_error_type(error_name: str) -> ErrorType:
    """
    Get error type by error name.
    
    Args:
        error_name: Error class name (e.g., "FileNotFoundError")
    
    Returns:
        ErrorType instance, returns UNKNOWN if not found
    """
    return ERROR_TYPES_DB.get(error_name, ErrorType(
        error_type=error_name,
        category=ErrorCategory.UNKNOWN,
        severity=ErrorSeverity.ERROR,
        suggestion="Unknown error type. Please check documentation.",
        auto_fixable=False
    ))


def get_category_errors(category: ErrorCategory) -> list:
    """
    Get all error types for a specific category.
    
    Args:
        category: Error category
    
    Returns:
        List of error type names
    """
    return [
        name for name, error_type in ERROR_TYPES_DB.items()
        if error_type.category == category
    ]
