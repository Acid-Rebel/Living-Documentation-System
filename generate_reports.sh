#!/bin/bash
# Script to regenerate all test reports

set -e

echo "🧪 Running tests and generating reports..."

# Set up environment
export PYTHONPATH=$PYTHONPATH:./backend:.
export DJANGO_SETTINGS_MODULE=backend.settings

# Create reports directory
mkdir -p reports

# Run tests with all report formats
/root/Living-Documentation-System/venv/bin/python -m pytest tests \
  --cov=diagram_generator \
  --cov-report=xml:reports/coverage.xml \
  --cov-report=html:reports/htmlcov \
  --cov-report=term-missing \
  --junitxml=reports/junit.xml \
  -v | tee reports/test_output.txt

echo ""
echo "✅ Reports generated successfully!"
echo ""
echo "📊 Available reports:"
echo "  - XML (CI/CD): reports/junit.xml, reports/coverage.xml"
echo "  - HTML: reports/htmlcov/index.html"
echo "  - Text: reports/test_output.txt"
echo ""
echo "To view HTML report:"
echo "  xdg-open reports/htmlcov/index.html"
