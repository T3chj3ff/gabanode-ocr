#!/bin/bash
# Test all prompt variants (v1-v5) and compare results

cd "$(dirname "$0")/benchmark"

echo "🧠 Brain Training - Multi-Variant Benchmark"
echo "==========================================="
echo ""

# Test each variant
for variant in v1-current v2-improved-clarity v3-step-by-step v4-examples-based v5-chain-of-thought; do
    echo "Testing: $variant"
    node run-benchmark.js --fixtures=all --prompt=$variant 2>&1 | tail -20
    echo ""
    sleep 2
done

echo "==========================================="
echo "All variants tested. Comparing results..."
echo ""

# Show comparison
echo "📊 COMPARISON RESULTS:"
grep -h "Average" results/benchmark-*.json | tail -5

echo ""
echo "💾 Full results in: results/"
ls -lhS results/benchmark-*.json | head -5
