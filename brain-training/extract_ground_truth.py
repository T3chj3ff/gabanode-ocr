#!/usr/bin/env python3
"""
Extract real ground truth HTML from tagged PDFs using pdftohtml
Generates baseline WCAG violations using axe-core simulation
"""

import subprocess
import json
from pathlib import Path
import re

# Paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"

def extract_html_from_pdf(pdf_path):
    """Extract HTML from PDF using pdftohtml"""
    try:
        # pdftohtml converts PDF to HTML directly
        result = subprocess.run(
            ["pdftohtml", "-noframes", "-stdout", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except FileNotFoundError:
        # pdftohtml not installed, try alternative approach
        print(f"  ⚠ pdftohtml not found, attempting pypdfium2 extraction...")
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument.new()
            pdf.load(str(pdf_path))

            # Extract text with basic HTML markup
            html = "<!DOCTYPE html>\n<html>\n<head><title>Extracted</title></head>\n<body>\n"
            for page_num in range(len(pdf)):
                page = pdf.get_page(page_num)
                text_dict = page.get_textpage().get_text()
                html += f"<p>{text_dict}</p>\n"
            html += "</body>\n</html>"
            return html
        except ImportError:
            print(f"  ✗ Neither pdftohtml nor pypdfium2 available")
            return None
    except Exception as e:
        print(f"  ✗ Extraction error: {e}")
        return None

    return None

def estimate_wcag_violations(html):
    """
    Estimate WCAG violations based on common patterns.
    This is a simulation of axe-core analysis.
    """
    violations = {
        "missing_alt_text": 0,
        "missing_form_labels": 0,
        "color_contrast_low": 0,
        "missing_heading_hierarchy": 0,
        "missing_landmarks": 0,
        "form_field_missing_label": 0,
        "image_no_alt": 0,
        "heading_not_structured": 0,
        "table_no_headers": 0,
        "total": 0
    }

    if not html:
        return violations

    # Count missing alt text on images
    img_count = len(re.findall(r'<img\s+[^>]*(?<!alt)[^>]*>', html, re.IGNORECASE))
    violations["missing_alt_text"] = img_count
    violations["image_no_alt"] = img_count

    # Count form fields without labels
    input_count = len(re.findall(r'<input\s+', html, re.IGNORECASE))
    labeled_count = len(re.findall(r'<label\s+[^>]*for\s*=[^>]*>', html, re.IGNORECASE))
    violations["missing_form_labels"] = max(0, input_count - labeled_count)
    violations["form_field_missing_label"] = violations["missing_form_labels"]

    # Check for heading hierarchy issues
    headings = re.findall(r'<h([1-6])', html, re.IGNORECASE)
    if headings:
        # Check if starts with h1 and maintains sequence
        if headings[0] != '1':
            violations["missing_heading_hierarchy"] += 1
        # Check for jumps (h1 -> h3 without h2)
        for i in range(len(headings) - 1):
            if int(headings[i+1]) > int(headings[i]) + 1:
                violations["heading_not_structured"] += 1

    # Check for tables without headers
    table_count = len(re.findall(r'<table\s*>', html, re.IGNORECASE))
    th_count = len(re.findall(r'<th\s*>', html, re.IGNORECASE))
    if table_count > 0 and th_count == 0:
        violations["table_no_headers"] = table_count

    # Check for landmark structure (body as default)
    landmark_count = len(re.findall(r'<(main|nav|aside|footer|article|section)\s*>', html, re.IGNORECASE))
    if landmark_count == 0:
        violations["missing_landmarks"] = 1

    violations["total"] = sum(v for k, v in violations.items() if k != "total")
    return violations

def process_fixture(fixture_dir):
    """Process a single fixture: extract HTML and estimate violations"""
    fixture_name = fixture_dir.name
    reference_pdf = fixture_dir / "reference-tagged.pdf"

    if not reference_pdf.exists():
        print(f"  ✗ No reference-tagged.pdf found")
        return False

    print(f"  Extracting HTML from {reference_pdf.name}...")
    html = extract_html_from_pdf(reference_pdf)

    if not html:
        print(f"  ✗ Extraction failed")
        return False

    # Save extracted HTML as ground truth
    expected_html = fixture_dir / "expected-html.html"
    expected_html.write_text(html)
    print(f"  ✓ Saved extracted HTML ({len(html)} bytes)")

    # Estimate violations
    violations = estimate_wcag_violations(html)

    # Save violation baseline
    baseline_file = fixture_dir / "baseline-violations.json"
    baseline_file.write_text(json.dumps(violations, indent=2))
    print(f"  ✓ Estimated {violations['total']} WCAG violations")

    return True

def main():
    print("Brain Training - Ground Truth Extraction")
    print("=" * 60)

    if not FIXTURES_DIR.exists():
        print(f"ERROR: Fixtures directory not found: {FIXTURES_DIR}")
        return False

    success_count = 0
    failure_count = 0

    for fixture_dir in sorted(FIXTURES_DIR.glob("*-*")):
        if not fixture_dir.is_dir():
            continue

        print(f"\n[{fixture_dir.name}]")
        if process_fixture(fixture_dir):
            success_count += 1
        else:
            failure_count += 1

    print("\n" + "=" * 60)
    print(f"Ground Truth Generation Complete")
    print(f"  ✓ Successful: {success_count}")
    print(f"  ✗ Failed: {failure_count}")
    print("=" * 60)
    print("\nNext: Run benchmark against real ground truth:")
    print("  node benchmark/run-benchmark.js --fixtures=all --prompt=v1-current")
    print("\nThis will show real healing performance (expect 10-30% vs current 22%)")
    print("=" * 60)

    return failure_count == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
