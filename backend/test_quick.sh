#!/bin/bash

# Quick test script for Day 2 agent
echo "=================================================="
echo "QUICK TEST: Day 2 Research Agent"
echo "=================================================="

# Check if venv is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Check API keys
if ! grep -q "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null; then
    echo "❌ ANTHROPIC_API_KEY not found in .env"
    exit 1
fi

if ! grep -q "TAVILY_API_KEY=tvly" .env 2>/dev/null; then
    echo "❌ TAVILY_API_KEY not found in .env"
    exit 1
fi

echo "✅ Environment checks passed"
echo ""

# Run tests
echo "Running unit tests..."
pytest tests/ -v --tb=short

echo ""
echo "Tests complete!"
