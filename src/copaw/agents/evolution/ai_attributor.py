# -*- coding: utf-8 -*-
"""
AI Attributor - AI-powered root cause analysis for CoPaw.

Features:
- 5-Why root cause analysis
- Responsibility attribution (code, data, config, environment)
- Suggestion generation
- Integration with CoPaw LLM providers

Usage:
    attributor = AIAttributor()
    analysis = attributor.analyze(error_record)
    print(f"Root cause: {analysis.root_cause}")
    print(f"Suggestion: {analysis.suggestion}")
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from copaw.utils.errors import ErrorRecord

logger = logging.getLogger(__name__)


@dataclass
class AttributionResult:
    """AI attribution analysis result"""

    error_type: str
    root_cause: str
    responsibility: str  # code, data, config, environment, user
    confidence: float  # 0.0-1.0
    why_chain: List[str]  # 5-Why chain
    suggestion: str
    preventive_measures: List[str]
    related_docs: List[str]
    analysis_timestamp: str


class AIAttributor:
    """
    AI-powered attribution analyzer.

    Uses 5-Why method for root cause analysis.

    Example:
        attributor = AIAttributor()
        result = attributor.analyze(error_record)
        print(result.root_cause)
    """

    def __init__(self, use_llm: bool = False):
        """
        Initialize AI attributor.

        Args:
            use_llm: Use LLM for analysis (default: False, uses rule-based)
        """
        self.use_llm = use_llm
        self._llm_client = None

        # Pre-defined why chains for common errors
        self.why_chains = self._load_why_chains()

    def _load_why_chains(self) -> Dict[str, List[str]]:
        """Load pre-defined 5-Why chains"""
        return {
            "FileNotFoundError": [
                "Why? File path does not exist",
                "Why? File was moved or deleted",
                "Why? No validation before access",
                "Why? Assumed file always exists",
                "Why? No error handling strategy",
            ],
            "KeyError": [
                "Why? Key not in dictionary",
                "Why? Data structure changed",
                "Why? No schema validation",
                "Why? Assumed key always exists",
                "Why? No defensive programming",
            ],
            "TypeError": [
                "Why? Wrong data type",
                "Why? Input not validated",
                "Why? No type hints enforced",
                "Why? Assumed correct input",
                "Why? No input validation layer",
            ],
            "ModuleNotFoundError": [
                "Why? Module not installed",
                "Why? Dependency missing",
                "Why? requirements.txt incomplete",
                "Why? No dependency check",
                "Why? No environment validation",
            ],
            "TimeoutError": [
                "Why? Operation timed out",
                "Why? Network slow or unavailable",
                "Why? No retry mechanism",
                "Why? Assumed fast response",
                "Why? No timeout handling strategy",
            ],
            "ValueError": [
                "Why? Invalid value",
                "Why? Input not validated",
                "Why? No range checking",
                "Why? Assumed valid input",
                "Why? No validation layer",
            ],
        }

    def analyze(self, error: ErrorRecord) -> AttributionResult:
        """
        Analyze error and attribute root cause.

        Args:
            error: ErrorRecord instance

        Returns:
            AttributionResult instance
        """
        if self.use_llm and self._llm_client:
            return self._analyze_with_llm(error)
        else:
            return self._analyze_rule_based(error)

    def _analyze_rule_based(self, error: ErrorRecord) -> AttributionResult:
        """Rule-based attribution analysis"""

        # Get 5-Why chain
        why_chain = self.why_chains.get(
            error.error_type,
            self._generate_generic_why_chain(error),
        )

        # Determine root cause
        root_cause = why_chain[-1] if why_chain else "Unknown root cause"

        # Attribute responsibility
        responsibility = self._attribute_responsibility(error)

        # Generate suggestion
        suggestion = self._generate_suggestion(error, responsibility)

        # Generate preventive measures
        preventive_measures = self._generate_preventive_measures(
            error,
            responsibility,
        )

        # Calculate confidence
        confidence = self._calculate_confidence(error, why_chain)

        return AttributionResult(
            error_type=error.error_type,
            root_cause=root_cause,
            responsibility=responsibility,
            confidence=confidence,
            why_chain=why_chain,
            suggestion=suggestion,
            preventive_measures=preventive_measures,
            related_docs=self._get_related_docs(error),
            analysis_timestamp=datetime.now().isoformat(),
        )

    def _analyze_with_llm(self, error: ErrorRecord) -> AttributionResult:
        """LLM-based attribution analysis (placeholder)"""
        # TODO: Integrate with CoPaw LLM providers
        logger.warning("LLM analysis not yet implemented, using rule-based")
        return self._analyze_rule_based(error)

    def _attribute_responsibility(self, error: ErrorRecord) -> str:
        """Attribute responsibility for the error"""
        category = error.category

        # Mapping from category to responsibility
        responsibility_map = {
            "file_error": "environment",
            "permission_error": "environment",
            "import_error": "environment",
            "database_error": "config",
            "key_error": "code",
            "type_error": "code",
            "value_error": "data",
            "timeout_error": "environment",
            "network_error": "environment",
            "parse_error": "data",
            "attribute_error": "code",
            "index_error": "code",
            "runtime_error": "code",
            "unknown": "code",
        }

        return responsibility_map.get(category, "code")

    def _generate_suggestion(
        self,
        error: ErrorRecord,
        responsibility: str,
    ) -> str:
        """Generate improvement suggestion"""
        suggestions = {
            "code": (
                f"Code fix: Add validation and error handling for "
                f"{error.error_type}. Use try-except and input validation."
            ),
            "data": (
                "Data issue: Validate input data before processing. "
                "Add data schema validation and sanitization."
            ),
            "config": (
                "Config issue: Review configuration settings. "
                "Add config validation and default values."
            ),
            "environment": (
                "Environment issue: Check environment setup. "
                "Add environment validation and fallback mechanisms."
            ),
            "user": (
                "User error: Improve user guidance and error messages. "
                "Add input validation and clear instructions."
            ),
        }

        base_suggestion = suggestions.get(responsibility, error.suggestion)
        return f"{base_suggestion} {error.suggestion}"

    def _generate_preventive_measures(
        self,
        _error: ErrorRecord,
        responsibility: str,
    ) -> List[str]:
        """Generate preventive measures"""
        measures = {
            "code": [
                "Add input validation",
                "Implement try-except blocks",
                "Add type hints and enforce them",
                "Write unit tests for edge cases",
                "Add logging for debugging",
            ],
            "data": [
                "Implement data schema validation",
                "Add data sanitization",
                "Validate data before processing",
                "Add data quality checks",
                "Implement data versioning",
            ],
            "config": [
                "Add config validation",
                "Implement default values",
                "Add config schema",
                "Validate config on startup",
                "Document required settings",
            ],
            "environment": [
                "Add environment validation",
                "Implement fallback mechanisms",
                "Add retry logic",
                "Monitor environment health",
                "Document dependencies",
            ],
            "user": [
                "Improve error messages",
                "Add input validation",
                "Provide clear instructions",
                "Add user guidance",
                "Implement helpful error recovery",
            ],
        }

        return measures.get(
            responsibility,
            ["Review and improve error handling"],
        )

    def _generate_generic_why_chain(self, error: ErrorRecord) -> List[str]:
        """Generate generic 5-Why chain"""
        return [
            f"Why? {error.error_message}",
            f"Why? {error.category} occurred",
            "Why? No preventive measure in place",
            "Why? Assumed conditions always true",
            "Why? No defensive programming",
        ]

    def _calculate_confidence(
        self,
        error: ErrorRecord,
        _why_chain: List[str],
    ) -> float:
        """Calculate confidence score"""
        confidence = 0.5

        # Higher confidence for known error types
        if error.error_type in self.why_chains:
            confidence += 0.3

        # Higher confidence with more context
        if error.traceback_str and len(error.traceback_str) > 100:
            confidence += 0.1

        # Higher confidence for categorized errors
        if error.category != "unknown":
            confidence += 0.1

        return min(1.0, confidence)

    def _get_related_docs(self, error: ErrorRecord) -> List[str]:
        """Get related documentation"""
        docs = {
            "FileNotFoundError": [
                "https://docs.python.org/3/library/os.path.html",
                (
                    "https://docs.python.org/3/library/"
                    "exceptions.html#FileNotFoundError"
                ),
            ],
            "KeyError": [
                (
                    "https://docs.python.org/3/library/"
                    "stdtypes.html#dict.get"
                ),
            ],
            "TypeError": [
                "https://docs.python.org/3/library/typing.html",
            ],
            "ModuleNotFoundError": [
                "https://pip.pypa.io/en/stable/cli/pip_install/",
            ],
        }

        return docs.get(error.error_type, [])

    def analyze_batch(
        self,
        errors: List[ErrorRecord],
    ) -> List[AttributionResult]:
        """
        Analyze multiple errors.

        Args:
            errors: List of ErrorRecord instances

        Returns:
            List of AttributionResult instances
        """
        results = []
        for error in errors:
            result = self.analyze(error)
            results.append(result)
        return results

    def generate_summary(
        self,
        results: List[AttributionResult],
    ) -> Dict[str, Any]:
        """
        Generate attribution analysis summary.

        Args:
            results: List of AttributionResult instances

        Returns:
            Summary dictionary
        """
        summary = {
            "total_analyzed": len(results),
            "by_responsibility": {},
            "by_error_type": {},
            "avg_confidence": 0.0,
            "top_root_causes": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Count by responsibility
        responsibility_counts: Dict[str, int] = {}
        for result in results:
            resp = result.responsibility
            responsibility_counts[resp] = (
                responsibility_counts.get(resp, 0) + 1
            )

            # Count by error type
            error_type = result.error_type
            by_error_type: Dict[str, int] = summary[
                "by_error_type"
            ]  # type: ignore
            by_error_type[error_type] = (
                by_error_type.get(
                    error_type,
                    0,
                )
                + 1
            )

        summary["by_responsibility"] = responsibility_counts

        # Calculate average confidence
        if results:
            summary["avg_confidence"] = sum(
                r.confidence for r in results
            ) / len(results)

        # Top root causes
        root_cause_counts = {}
        for result in results:
            rc = result.root_cause
            root_cause_counts[rc] = root_cause_counts.get(rc, 0) + 1

        summary["top_root_causes"] = sorted(
            root_cause_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return summary
