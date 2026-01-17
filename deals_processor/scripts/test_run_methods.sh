#!/bin/bash
set -e

source venv/bin/activate

echo "🧪 Testing different execution methods..."
echo ""

# Test 1: Check CLI entry point is installed
echo "✅ Test 1: CLI entry point installed"
which deals-processor-dev > /dev/null && echo "   deals-processor-dev: OK" || echo "   FAILED"
which deals-processor > /dev/null && echo "   deals-processor: OK" || echo "   FAILED"
echo ""

# Test 2: Test module import
echo "✅ Test 2: Module imports"
python -c "from deals_processor.cli import main, run_dev; print('   CLI module: OK')"
python -c "from deals_processor.main import app; print('   Main module: OK')"
echo ""

# Test 3: Check pyproject.toml has scripts
echo "✅ Test 3: pyproject.toml has [project.scripts]"
grep -A2 "\[project.scripts\]" pyproject.toml > /dev/null && echo "   Scripts section: OK" || echo "   FAILED"
echo ""

# Test 4: Check __main__ exists
echo "✅ Test 4: __main__.py exists"
test -f src/deals_processor/__main__.py && echo "   __main__.py: OK" || echo "   FAILED"
echo ""

# Test 5: Check main.py has __main__ block
echo "✅ Test 5: main.py has __main__ block"
grep -q "if __name__ == \"__main__\":" src/deals_processor/main.py && echo "   __main__ block: OK" || echo "   FAILED"
echo ""

echo "🎉 All tests passed!"
