# -*- coding: utf-8 -*-
"""
Auto Pattern Detector - Automatically detect error patterns for CoPaw.

Features:
- Frequency analysis for recurring errors
- Trend detection (increasing/decreasing/stable)
- Anomaly detection (unusual patterns)
- Pattern-based suggestions

Usage:
    detector = AutoPatternDetector()
    detector.add_error(error_record)
    patterns = detector.detect_patterns()
    suggestions = detector.generate_suggestions()
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import json

from copaw.utils.errors import ErrorRecord

logger = logging.getLogger(__name__)


@dataclass
class PatternInfo:
    """Pattern information data structure"""
    
    pattern_type: str  # frequency, trend, anomaly
    error_type: str
    category: str
    count: int
    frequency: float  # errors per hour
    trend: str  # increasing, decreasing, stable
    confidence: float  # 0.0-1.0
    suggestion: str
    first_seen: str
    last_seen: str
    related_errors: List[str] = field(default_factory=list)


class AutoPatternDetector:
    """
    Automatic pattern detector for error analysis.
    
    Example:
        detector = AutoPatternDetector()
        
        # Add errors
        for error in error_list:
            detector.add_error(error)
        
        # Detect patterns
        patterns = detector.detect_patterns()
        
        # Get suggestions
        suggestions = detector.generate_suggestions()
    """
    
    def __init__(
        self,
        time_window_hours: int = 24,
        min_frequency: int = 3,
        anomaly_threshold: float = 2.0
    ):
        """
        Initialize pattern detector.
        
        Args:
            time_window_hours: Time window for analysis (default: 24 hours)
            min_frequency: Minimum errors to consider as pattern (default: 3)
            anomaly_threshold: Standard deviations for anomaly (default: 2.0)
        """
        self.time_window_hours = time_window_hours
        self.min_frequency = min_frequency
        self.anomaly_threshold = anomaly_threshold
        
        self.errors: List[ErrorRecord] = []
        self.error_by_type: Dict[str, List[ErrorRecord]] = defaultdict(list)
        self.error_by_category: Dict[str, List[ErrorRecord]] = defaultdict(list)
        self.hourly_counts: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        
        self._patterns: List[PatternInfo] = []
        self._analyzed = False
    
    def add_error(self, error: ErrorRecord) -> None:
        """
        Add an error record for pattern analysis.
        
        Args:
            error: ErrorRecord instance
        """
        self.errors.append(error)
        self.error_by_type[error.error_type].append(error)
        self.error_by_category[error.category].append(error)
        
        # Track hourly counts
        try:
            timestamp = datetime.fromisoformat(error.timestamp.replace('Z', '+00:00'))
            hour = timestamp.hour
            self.hourly_counts[error.error_type][hour] += 1
        except Exception as e:
            logger.debug(f"Failed to parse timestamp: {e}")
        
        self._analyzed = False
    
    def add_errors(self, errors: List[ErrorRecord]) -> None:
        """
        Add multiple error records.
        
        Args:
            errors: List of ErrorRecord instances
        """
        for error in errors:
            self.add_error(error)
    
    def detect_patterns(self) -> List[PatternInfo]:
        """
        Detect patterns in error data.
        
        Returns:
            List of PatternInfo instances
        """
        self._patterns = []
        
        # Detect frequency patterns
        self._detect_frequency_patterns()
        
        # Detect trend patterns
        self._detect_trend_patterns()
        
        # Detect anomaly patterns
        self._detect_anomaly_patterns()
        
        self._analyzed = True
        logger.info(f"Detected {len(self._patterns)} patterns")
        return self._patterns
    
    def _detect_frequency_patterns(self) -> None:
        """Detect high-frequency error patterns"""
        for error_type, errors in self.error_by_type.items():
            if len(errors) >= self.min_frequency:
                # Calculate frequency (errors per hour)
                time_span = self._calculate_time_span(errors)
                frequency = len(errors) / max(time_span, 1)
                
                # Get category
                category = errors[0].category if errors else "unknown"
                
                # Generate suggestion
                suggestion = self._generate_frequency_suggestion(
                    error_type, category, len(errors), frequency
                )
                
                pattern = PatternInfo(
                    pattern_type="frequency",
                    error_type=error_type,
                    category=category,
                    count=len(errors),
                    frequency=frequency,
                    trend=self._calculate_trend(errors),
                    confidence=min(1.0, len(errors) / 10.0),
                    suggestion=suggestion,
                    first_seen=errors[0].timestamp,
                    last_seen=errors[-1].timestamp,
                    related_errors=[e.error_message for e in errors[:5]]
                )
                
                self._patterns.append(pattern)
    
    def _detect_trend_patterns(self) -> None:
        """Detect trending error patterns"""
        for error_type, errors in self.error_by_type.items():
            if len(errors) >= 5:  # Need more data for trend
                trend = self._calculate_trend(errors)
                
                if trend in ["increasing", "decreasing"]:
                    category = errors[0].category if errors else "unknown"
                    
                    suggestion = self._generate_trend_suggestion(
                        error_type, category, trend
                    )
                    
                    pattern = PatternInfo(
                        pattern_type="trend",
                        error_type=error_type,
                        category=category,
                        count=len(errors),
                        frequency=len(errors) / self.time_window_hours,
                        trend=trend,
                        confidence=0.7,
                        suggestion=suggestion,
                        first_seen=errors[0].timestamp,
                        last_seen=errors[-1].timestamp
                    )
                    
                    self._patterns.append(pattern)
    
    def _detect_anomaly_patterns(self) -> None:
        """Detect anomalous error patterns"""
        for error_type, hourly_data in self.hourly_counts.items():
            if len(hourly_data) < 3:
                continue
            
            # Calculate statistics
            counts = list(hourly_data.values())
            avg = sum(counts) / len(counts)
            std = (sum((x - avg) ** 2 for x in counts) / len(counts)) ** 0.5
            
            # Detect anomalies
            for hour, count in hourly_data.items():
                if std > 0 and (count - avg) / std > self.anomaly_threshold:
                    errors = self.error_by_type.get(error_type, [])
                    category = errors[0].category if errors else "unknown"
                    
                    suggestion = self._generate_anomaly_suggestion(
                        error_type, category, count, avg
                    )
                    
                    pattern = PatternInfo(
                        pattern_type="anomaly",
                        error_type=error_type,
                        category=category,
                        count=count,
                        frequency=count,
                        trend="spike",
                        confidence=0.8,
                        suggestion=suggestion,
                        first_seen=datetime.now().isoformat(),
                        last_seen=datetime.now().isoformat()
                    )
                    
                    self._patterns.append(pattern)
    
    def _calculate_time_span(self, errors: List[ErrorRecord]) -> float:
        """Calculate time span in hours"""
        if len(errors) < 2:
            return 1.0
        
        try:
            first = datetime.fromisoformat(errors[0].timestamp.replace('Z', '+00:00'))
            last = datetime.fromisoformat(errors[-1].timestamp.replace('Z', '+00:00'))
            span = (last - first).total_seconds() / 3600
            return max(span, 1.0)
        except Exception:
            return self.time_window_hours
    
    def _calculate_trend(self, errors: List[ErrorRecord]) -> str:
        """Calculate error trend"""
        if len(errors) < 5:
            return "stable"
        
        # Split into two halves
        mid = len(errors) // 2
        first_half = len(errors[:mid])
        second_half = len(errors[mid:])
        
        # Compare
        if second_half > first_half * 1.5:
            return "increasing"
        elif second_half < first_half * 0.5:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_frequency_suggestion(
        self,
        error_type: str,
        category: str,
        count: int,
        frequency: float
    ) -> str:
        """Generate suggestion for high-frequency errors"""
        if frequency > 10:
            return (
                f"Critical: {error_type} occurs {frequency:.1f} times/hour. "
                f"Immediate attention required. Consider adding validation or error handling."
            )
        elif frequency > 5:
            return (
                f"Warning: {error_type} occurs {frequency:.1f} times/hour. "
                f"Review code for common causes and add preventive measures."
            )
        else:
            return (
                f"Notice: {error_type} has occurred {count} times. "
                f"Monitor for increasing frequency."
            )
    
    def _generate_trend_suggestion(
        self,
        error_type: str,
        category: str,
        trend: str
    ) -> str:
        """Generate suggestion for trending errors"""
        if trend == "increasing":
            return (
                f"Alert: {error_type} is increasing. "
                f"Recent changes may have introduced this. "
                f"Review commits and add regression tests."
            )
        elif trend == "decreasing":
            return (
                f"Good: {error_type} is decreasing. "
                f"Recent fixes appear effective. "
                f"Continue monitoring."
            )
        return ""
    
    def _generate_anomaly_suggestion(
        self,
        error_type: str,
        category: str,
        count: int,
        avg: float
    ) -> str:
        """Generate suggestion for anomalous errors"""
        return (
            f"Anomaly: {error_type} spiked to {count} occurrences "
            f"(avg: {avg:.1f}). "
            f"Check external factors (deployment, traffic, etc.)."
        )
    
    def generate_suggestions(self) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions based on detected patterns.
        
        Returns:
            List of suggestion dictionaries
        """
        if not self._analyzed:
            self.detect_patterns()
        
        suggestions = []
        for pattern in self._patterns:
            suggestion = {
                "priority": self._calculate_priority(pattern),
                "error_type": pattern.error_type,
                "category": pattern.category,
                "pattern_type": pattern.pattern_type,
                "suggestion": pattern.suggestion,
                "confidence": pattern.confidence,
                "metrics": {
                    "count": pattern.count,
                    "frequency": pattern.frequency,
                    "trend": pattern.trend
                }
            }
            suggestions.append(suggestion)
        
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        return suggestions
    
    def _calculate_priority(self, pattern: PatternInfo) -> int:
        """Calculate suggestion priority (1-10)"""
        priority = 5
        
        # Adjust by pattern type
        if pattern.pattern_type == "anomaly":
            priority += 2
        elif pattern.pattern_type == "trend" and pattern.trend == "increasing":
            priority += 3
        
        # Adjust by frequency
        if pattern.frequency > 10:
            priority += 2
        elif pattern.frequency > 5:
            priority += 1
        
        # Adjust by count
        if pattern.count > 20:
            priority += 1
        
        return min(10, priority)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get pattern analysis summary.
        
        Returns:
            Summary dictionary
        """
        if not self._analyzed:
            self.detect_patterns()
        
        return {
            "total_errors": len(self.errors),
            "unique_error_types": len(self.error_by_type),
            "unique_categories": len(self.error_by_category),
            "patterns_detected": len(self._patterns),
            "high_priority_suggestions": len(
                [p for p in self._patterns if self._calculate_priority(p) >= 7]
            ),
            "time_window_hours": self.time_window_hours,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def to_json(self) -> str:
        """Export patterns to JSON"""
        if not self._analyzed:
            self.detect_patterns()
        
        data = {
            "summary": self.get_summary(),
            "patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "error_type": p.error_type,
                    "category": p.category,
                    "count": p.count,
                    "frequency": p.frequency,
                    "trend": p.trend,
                    "confidence": p.confidence,
                    "suggestion": p.suggestion,
                    "first_seen": p.first_seen,
                    "last_seen": p.last_seen
                }
                for p in self._patterns
            ]
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
