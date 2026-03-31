# Self-Evolution for CoPaw

**Complete self-improving AI agent engine with automatic error capture, pattern detection, AI-powered attribution analysis, and evolution dashboard.**

---

## 🚀 Quick Start

### 1. Error Capture

```python
from copaw.utils.errors import auto_catch, AutoErrorCatcher, catch_and_learn

# Method 1: Decorator
@auto_catch()
def my_function():
    return 1 / 0  # Automatically caught and classified

# Method 2: Context Manager
with AutoErrorCatcher("operation") as catcher:
    dangerous_task()
    if catcher.has_error:
        print(f"Suggestion: {catcher.get_suggestion()}")

# Method 3: Manual Capture
try:
    complex_calculation()
except Exception as e:
    error_record = catch_and_learn(e, "calculation")
    print(f"Category: {error_record.category}")
```

### 2. Pattern Detection

```python
from copaw.agents.evolution import AutoPatternDetector

detector = AutoPatternDetector()

# Add errors
for error in error_list:
    detector.add_error(error)

# Detect patterns
patterns = detector.detect_patterns()

# Get suggestions
suggestions = detector.generate_suggestions()
for s in suggestions:
    print(f"Priority {s['priority']}: {s['suggestion']}")
```

### 3. AI Attribution

```python
from copaw.agents.evolution import AIAttributor

attributor = AIAttributor()

# Analyze error
result = attributor.analyze(error_record)
print(f"Root cause: {result.root_cause}")
print(f"Responsibility: {result.responsibility}")
print(f"Suggestion: {result.suggestion}")

# 5-Why chain
for i, why in enumerate(result.why_chain, 1):
    print(f"{i}. {why}")
```

### 4. Evolution Dashboard

```python
from copaw.agents.evolution import EvolutionDashboard, EvolutionMetrics

dashboard = EvolutionDashboard()

# Add metrics
dashboard.add_metrics_dict({
    "errors_captured": 25,
    "patterns_detected": 8,
    "suggestions_generated": 12,
    "improvements_applied": 5
})

# Generate report
report = dashboard.generate_report()
print(f"Evolution Score: {report['summary']['evolution_score']:.1f}/100")

# Export to markdown
dashboard.export_markdown("evolution_report.md")
```

---

## 🎯 Features

### Error Categorization

- **14 Error Categories:** file_error, permission_error, import_error, database_error, key_error, type_error, value_error, timeout_error, network_error, parse_error, attribute_error, index_error, runtime_error, unknown
- **3 Capture Methods:** Decorator, Context Manager, Manual
- **Automatic Suggestions:** Actionable improvement suggestions for each error type
- **96% Test Coverage:** Comprehensive test suite

### Pattern Detection

- **Frequency Analysis:** Identify recurring errors
- **Trend Detection:** Increasing, decreasing, or stable patterns
- **Anomaly Detection:** Unusual spikes and outliers
- **Priority Scoring:** Focus on high-impact issues

### AI Attribution

- **5-Why Root Cause Analysis:** Deep dive into error causes
- **Responsibility Attribution:** code, data, config, environment, user
- **Preventive Measures:** Actionable recommendations
- **Confidence Scoring:** Know how reliable the analysis is

### Evolution Dashboard

- **Progress Tracking:** Monitor self-improvement over time
- **Analytics Visualization:** Charts and trends
- **Markdown Reports:** Export to markdown/PDF
- **Evolution Score:** 0-100 score for overall progress

---

## 🏗️ Architecture

```
copaw/
├── utils/
│   └── errors/
│       ├── __init__.py
│       ├── error_types.py          # Error type definitions
│       └── error_classifier.py     # Error capture logic
└── agents/
    └── evolution/
        ├── __init__.py
        ├── pattern_detector.py     # Pattern detection
        ├── ai_attributor.py        # AI attribution
        └── dashboard.py            # Dashboard & reporting
```

---

## 📊 Complete Workflow

```
1. Error Occurs
       ↓
2. AutoErrorCatcher captures and classifies
       ↓
3. PatternDetector analyzes recurring patterns
       ↓
4. AIAttributor performs 5-Why analysis
       ↓
5. Dashboard tracks progress
       ↓
6. Improvements applied
       ↓
7. Agent evolves and improves
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/test_errors/ tests/test_evolution/ -v

# With coverage
pytest tests/ --cov=copaw.utils.errors --cov=copaw.agents.evolution --cov-report=term-missing

# Verification script
python verify_errors.py
```

### Expected Results

```
============================= test session starts ==============================
collected 35 items

tests/test_errors/test_error_types.py::TestErrorTypes::test_get_known_error_type PASSED
tests/test_errors/test_error_types.py::TestErrorTypes::test_get_unknown_error_type PASSED
...
tests/test_evolution/test_pattern_detector.py::TestPatternDetector::test_frequency_detection PASSED
tests/test_evolution/test_pattern_detector.py::TestPatternDetector::test_trend_detection PASSED
...
======================== 35 passed in 3.45s ========================
```

---

## 📈 Evolution Score

The evolution score (0-100) measures self-improvement progress:

| Score Range | Status | Description |
|-------------|--------|-------------|
| 0-20 | 🌱 Beginner | Just started error capture |
| 21-40 | 🌿 Learning | Detecting patterns |
| 41-60 | 🌳 Growing | Generating suggestions |
| 61-80 | 🌲 Maturing | Applying improvements |
| 81-100 | 🏆 Master | Full self-evolution loop |

---

## 🔗 Related

- **Issue #2473:** https://github.com/agentscope-ai/CoPaw/issues/2473
- **Error Categorization:** `copaw.utils.errors`
- **Pattern Detection:** `copaw.agents.evolution.AutoPatternDetector`
- **AI Attribution:** `copaw.agents.evolution.AIAttributor`
- **Dashboard:** `copaw.agents.evolution.EvolutionDashboard`

---

## 📝 License

Apache-2.0 License

---

**Ready to make your CoPaw agents self-improving? Start with error capture today! 🚀**
