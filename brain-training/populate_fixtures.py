#!/usr/bin/env python3
"""
Brain Training Fixture Population & Automation
Locates reference PDFs, populates fixtures, generates ground truth, runs benchmarks
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime
import sys

# Paths - handle both user filesystem and workspace mounts
script_dir = Path(__file__).parent.resolve()
FIXTURES_DIR = script_dir / "fixtures"
BENCHMARK_DIR = script_dir / "benchmark"

# Fixture mapping: (fixture_num, source_pdf_name, doc_type, complexity_target)
FIXTURE_MAPPING = [
    (1, "PDFUA-Ref-2-03_AcademicAbstract.pdf", "simple-text", "95%"),
    (2, "PDFUA-Ref-2-02_Invoice.pdf", "complex-table", "85%"),
    (3, "PDFUA-Ref-2-09_Scanned.pdf", "scanned-image", "70%"),
    (4, "PDFUA-Ref-2-10_Form.pdf", "form-with-fields", "80%"),
    (5, "PDFUA-Ref-2-06_Brochure.pdf", "multi-column", "80%"),
    (6, "PDFUA-Ref-2-04_Presentation.pdf", "images-with-captions", "85%"),
    (7, "PDFUA-Ref-2-08_BookChapter.pdf", "nested-lists", "85%"),
    (8, "PDFUA-Ref-2-01_Magazine-danish.pdf", "mixed-content", "80%"),
    (9, "PDFUA-Ref-2-05_BookChapter-german.pdf", "edge-cases", "77%"),
]

def populate_fixtures(ref_pdfs_path):
    """Copy PDFs and create ground-truth files for each fixture"""

    ref_pdfs_path = Path(ref_pdfs_path)

    if not ref_pdfs_path.exists():
        print(f"ERROR: reference_pdfs not found at {ref_pdfs_path}")
        return False

    tagged_pdfs = ref_pdfs_path
    stripped_pdfs = ref_pdfs_path / "_stripped"

    if not stripped_pdfs.exists():
        print(f"ERROR: _stripped folder not found at {stripped_pdfs}")
        return False

    success_count = 0

    for fixture_num, source_pdf, doc_type, target in FIXTURE_MAPPING:
        fixture_dir = FIXTURES_DIR / f"{fixture_num:03d}-{doc_type}"
        if not fixture_dir.exists():
            print(f"WARNING: Fixture directory {fixture_dir} not found, skipping")
            continue

        # Copy untagged PDF as source.pdf
        source_path = stripped_pdfs / source_pdf
        target_source = fixture_dir / "source.pdf"

        if source_path.exists():
            try:
                shutil.copy2(source_path, target_source)
                print(f"✓ Copied {source_pdf} → {fixture_num:03d}-{doc_type}/source.pdf")
            except Exception as e:
                print(f"✗ Failed to copy {source_pdf}: {e}")
                continue
        else:
            print(f"WARNING: {source_pdf} not found in {stripped_pdfs}")
            continue

        # Copy tagged PDF as reference for ground truth
        tagged_path = tagged_pdfs / source_pdf
        if tagged_path.exists():
            try:
                shutil.copy2(tagged_path, fixture_dir / "reference-tagged.pdf")
                print(f"  → Reference tagged PDF saved")
            except Exception as e:
                print(f"  ⚠ Could not save reference: {e}")

        # Create placeholder expected outputs
        expected_md = fixture_dir / "expected-md.md"
        if not expected_md.exists():
            expected_md.write_text(
                f"# Fixture {fixture_num}: {doc_type.replace('-', ' ').title()}\n\n"
                f"Expected Markdown output from {source_pdf}.\n\n"
                f"Target Accuracy: {target}\n\n"
                f"[Content to be extracted and verified against tagged PDF]\n"
            )

        expected_html = fixture_dir / "expected-html.html"
        if not expected_html.exists():
            expected_html.write_text(
                f"<!DOCTYPE html>\n"
                f"<html>\n<head><title>Fixture {fixture_num}</title></head>\n"
                f"<body>\n"
                f"<h1>Fixture {fixture_num}: {doc_type.replace('-', ' ').title()}</h1>\n"
                f"<p>Expected healed HTML from {source_pdf}</p>\n"
                f"<p>Target Accuracy: {target}</p>\n"
                f"</body>\n</html>\n"
            )

        # Create score threshold
        expected_score = fixture_dir / "expected-score.json"
        if not expected_score.exists():
            score_data = {
                "fixture": f"{fixture_num:03d}",
                "doc_type": doc_type,
                "source_pdf": source_pdf,
                "extraction_target": int(target.rstrip('%')),
                "healing_target": int(target.rstrip('%')),
                "combined_target": int(target.rstrip('%'))
            }
            expected_score.write_text(json.dumps(score_data, indent=2))

        success_count += 1

    return success_count > 0

def generate_report():
    """Generate summary report of fixture population"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "fixtures_populated": sum(1 for f in FIXTURES_DIR.glob("*") if (f / "source.pdf").exists()),
        "total_fixtures": len(list(FIXTURES_DIR.glob("*"))),
        "baseline_benchmark_ready": (BENCHMARK_DIR / "run-benchmark.js").exists()
    }

    print("\n" + "="*60)
    print("FIXTURE POPULATION REPORT")
    print("="*60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Fixtures Populated: {report['fixtures_populated']}/{report['total_fixtures']}")
    print(f"Benchmark Script: {'✓ Ready' if report['baseline_benchmark_ready'] else '✗ Missing'}")

    return report

def main():
    print("Brain Training - Fixture Population Automation")
    print("="*60)

    # Get reference_pdfs path
    if len(sys.argv) < 2:
        print("ERROR: Must provide path to reference_pdfs as argument")
        print("Usage: python3 populate_fixtures.py /path/to/reference_pdfs")
        sys.exit(1)

    ref_pdfs = sys.argv[1]

    print(f"\n[1/2] Locating reference_pdfs at {ref_pdfs}...")
    if not Path(ref_pdfs).exists():
        print(f"ERROR: Path does not exist: {ref_pdfs}")
        sys.exit(1)
    print(f"✓ Found reference_pdfs")

    # Step 2: Populate fixtures
    print("\n[2/2] Populating 9 fixtures with PDFs...")
    if populate_fixtures(ref_pdfs):
        print("✓ Fixtures populated successfully")
    else:
        print("✗ Fixture population failed")
        sys.exit(1)

    # Generate report
    report = generate_report()

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Run baseline benchmark:")
    print(f"   cd {BENCHMARK_DIR}")
    print("   node run-benchmark.js --fixtures=all --prompt=v1-current")
    print("\n2. Test prompt variants (v2-v5) against all fixtures")
    print("\n3. Compare results and select best variant for production")
    print("="*60)

if __name__ == "__main__":
    main()
