# Test Reports

This directory contains comprehensive test reports for the Living Documentation System.

## Report Files

### XML Reports (CI/CD Integration)
- **junit.xml** - JUnit format test results (compatible with Jenkins, GitLab CI, GitHub Actions)
- **coverage.xml** - Cobertura format coverage data (compatible with SonarQube, Codecov, Coveralls)

### HTML Reports (Human-Readable)
- **htmlcov/** - Interactive HTML coverage report
  - Open `htmlcov/index.html` in a browser to view detailed line-by-line coverage
  - Shows which lines are covered, missed, or excluded
  - Includes branch coverage information

### Text Reports
- **test_output.txt** - Complete test execution log with coverage summary

## Viewing Reports

### HTML Coverage Report
```bash
# Open in browser
xdg-open reports/htmlcov/index.html

# Or use Python's HTTP server
cd reports/htmlcov
python -m http.server 8080
# Then visit http://localhost:8080
```

### Test Results Summary
```bash
cat reports/test_output.txt
```

## Latest Test Run

**Date**: 2026-01-31  
**Tests Passed**: 50/50 ✅  
**Coverage**: 65% (diagram_generator module)

### Coverage by Module
- `ast_relations.py`: 93%
- `repo_scanner.py`: 93%
- `heuristics.py`: 100%
- `ast_traverser.py`: 81%
- `generate_repo_diagrams.py`: 62%
- `renderers.py`: 58%
- `graph_model.py`: 57%

## Regenerating Reports

```bash
# Run tests and generate all reports
export PYTHONPATH=$PYTHONPATH:./backend:.
pytest tests \
  --cov=diagram_generator \
  --cov-report=xml:reports/coverage.xml \
  --cov-report=html:reports/htmlcov \
  --junitxml=reports/junit.xml \
  -v
```
