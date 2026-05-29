#!/bin/bash
# Healing Pipeline Execution Script
# Run this locally to execute Phase 2C-1: Batch Healing
#
# Usage:
#   chmod +x run_healing_pipeline.sh
#   ./run_healing_pipeline.sh "AIzaSyBRQTrOkNtpvNt9o8l_nCYW7hLmvWmYYwk"
#
# Or set environment variable:
#   export GEMINI_API_KEY="your-key"
#   ./run_healing_pipeline.sh

set -e

# Get API key from argument or environment
API_KEY="${1:-${GEMINI_API_KEY}}"

if [ -z "$API_KEY" ]; then
    echo "❌ Error: Gemini API key not provided"
    echo ""
    echo "Usage:"
    echo "  ./run_healing_pipeline.sh \"your-api-key\""
    echo ""
    echo "Or set environment variable:"
    echo "  export GEMINI_API_KEY=\"your-api-key\""
    echo "  ./run_healing_pipeline.sh"
    exit 1
fi

# Verify Python and dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

echo "🔧 Installing dependencies..."
pip install google-generativeai --break-system-packages -q

# Navigate to brain-training directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "PHASE 2C-1: Batch Healing Pipeline"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "API Key: ${API_KEY:0:20}..."
echo "Script Directory: $SCRIPT_DIR"
echo ""

# Export API key for Python scripts
export GEMINI_API_KEY="$API_KEY"

# Run the healing pipeline
echo "Starting healing pipeline..."
echo ""

python3 heal_all_fixtures.py

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "✅ Healing pipeline complete!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Generated files:"
echo "  • healing-analysis-v1-vs-v6.json (comprehensive comparison)"
echo "  • healing-summary-v1-current.json (v1 results)"
echo "  • healing-summary-v6-healing-focused.json (v6 results)"
echo "  • healed-v1-current.html (per fixture)"
echo "  • healed-v6-healing-focused.html (per fixture)"
echo ""
echo "Next steps:"
echo "  1. Review healing-analysis-v1-vs-v6.json for detailed results"
echo "  2. Check individual healed-*.html files for quality"
echo "  3. Run Phase 2C-2 (re-benchmarking) if improvement meets criteria"
echo "  4. Consider Phase 2C-3 (multi-model testing) for specialized fixtures"
echo ""
