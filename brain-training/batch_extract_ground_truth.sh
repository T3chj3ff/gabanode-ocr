#!/bin/bash
# Batch extract ground truth HTML from all tagged PDFs

FIXTURES_DIR="$(cd "$(dirname "$0")/fixtures" && pwd)"
SUCCESS=0
FAILED=0

echo "Brain Training - Batch Ground Truth Extraction"
echo "=============================================="
echo ""

for fixture_dir in "$FIXTURES_DIR"/*-*; do
    if [ ! -d "$fixture_dir" ]; then
        continue
    fi

    fixture_name=$(basename "$fixture_dir")
    reference_pdf="$fixture_dir/reference-tagged.pdf"
    expected_html="$fixture_dir/expected-html.html"

    if [ ! -f "$reference_pdf" ]; then
        echo "[$fixture_name] ✗ No reference-tagged.pdf"
        ((FAILED++))
        continue
    fi

    echo "[$fixture_name] Extracting HTML..."

    # Extract HTML using pdftohtml
    if pdftohtml -noframes -stdout "$reference_pdf" > "$expected_html" 2>/dev/null; then
        file_size=$(stat -f%z "$expected_html" 2>/dev/null || stat -c%s "$expected_html" 2>/dev/null)
        echo "  ✓ Extracted ($file_size bytes)"
        ((SUCCESS++))
    else
        echo "  ✗ Extraction failed"
        ((FAILED++))
    fi
done

echo ""
echo "=============================================="
echo "Extraction Complete"
echo "  ✓ Success: $SUCCESS"
echo "  ✗ Failed: $FAILED"
echo "=============================================="
echo ""
echo "Next: Run benchmark against real ground truth"
echo "  cd benchmark"
echo "  node run-benchmark.js --fixtures=all --prompt=v1-current"
