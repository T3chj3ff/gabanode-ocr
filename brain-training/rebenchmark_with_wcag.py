#!/usr/bin/env python3
"""
Re-benchmark healing effectiveness using REAL WCAG 2.2 AA violations.
Compares baseline violations against healed HTML violations.

Delegates violation detection to wcag_validator.py (single source of truth).
"""

import json
import sys
from pathlib import Path

# Paths
BRAIN_TRAINING = Path(__file__).parent
FIXTURES_DIR = BRAIN_TRAINING / 'fixtures'
BASELINE_REPORT = BRAIN_TRAINING / 'wcag-baseline-report.json'

# Import shared validator — avoids duplication and drift
sys.path.insert(0, str(BRAIN_TRAINING))
from wcag_validator import validate_wcag_aa


def count_wcag_violations(html_content):
    """Count WCAG 2.2 AA violations using the shared validator."""
    v = validate_wcag_aa(html_content)
    counts = {
        key: (len(value) if isinstance(value, list) else value)
        for key, value in v.items()
        if key != 'total'
    }
    counts['total'] = v.get('total', 0)
    return counts

def load_baseline():
    """Load baseline WCAG violations"""
    if not BASELINE_REPORT.exists():
        print("ERROR: No baseline report found. Run wcag_validator.py first.")
        return None

    with open(BASELINE_REPORT) as f:
        return json.load(f)

def analyze_fixture_healing(fixture_name, baseline_violations, variant='v11-production-ready'):
    """Analyze healing effectiveness for a fixture by reading the healed HTML file."""
    fixture_dir = None
    for d in FIXTURES_DIR.glob(f'{fixture_name}*'):
        if d.is_dir():
            fixture_dir = d
            break

    if not fixture_dir:
        return None

    # Prefer the healed variant file; fall back to expected-html only if absent
    healed_html_file = fixture_dir / f'healed-{variant}.html'
    if not healed_html_file.exists():
        # Fallback: try best-known variant
        for fallback in ['v9-deterministic-full', 'v8-deterministic-images', 'v7-deterministic-basic']:
            candidate = fixture_dir / f'healed-{fallback}.html'
            if candidate.exists():
                healed_html_file = candidate
                break
        else:
            healed_html_file = fixture_dir / 'expected-html.html'

    if not healed_html_file.exists():
        return None

    # Read the healed HTML (NOT the baseline expected-html)
    healed_html = healed_html_file.read_text()

    # Count violations in healed HTML
    healed_violations = count_wcag_violations(healed_html)

    # Calculate violations fixed
    baseline_count = baseline_violations['total']
    remaining_count = healed_violations['total']

    if baseline_count == 0:
        violations_fixed_pct = 100.0 if remaining_count == 0 else 0.0
    else:
        violations_fixed_pct = max(0, (baseline_count - remaining_count) / baseline_count * 100)

    return {
        'fixture': fixture_name,
        'baseline_violations': baseline_count,
        'remaining_violations': remaining_count,
        'violations_fixed': baseline_count - remaining_count,
        'violations_fixed_pct': round(violations_fixed_pct, 1),
        'detail': {
            'baseline': baseline_violations,
            'remaining': healed_violations
        }
    }

def main(variant='v11-production-ready'):
    print(f"WCAG-Based Healing Effectiveness Analysis  [variant: {variant}]")
    print("=" * 70)
    print()

    # Load baseline
    baseline_data = load_baseline()
    if not baseline_data:
        return

    # Create mapping of fixture names to baseline violations
    baseline_map = {}
    for fixture in baseline_data['fixtures']:
        fixture_num = fixture['fixture'].split('-')[0]
        baseline_map[fixture['fixture']] = fixture['violations']

    # Analyze each fixture
    results = []
    total_baseline = 0
    total_remaining = 0

    print("Per-Fixture Analysis:")
    print("-" * 70)

    for fixture_dir in sorted(FIXTURES_DIR.glob('*-*')):
        if not fixture_dir.is_dir():
            continue

        fixture_name = fixture_dir.name
        if fixture_name not in baseline_map:
            print(f"[{fixture_name}] ⚠ No baseline found")
            continue

        baseline_violations = baseline_map[fixture_name]
        analysis = analyze_fixture_healing(fixture_name, baseline_violations, variant=variant)

        if not analysis:
            print(f"[{fixture_name}] ✗ Analysis failed")
            continue

        results.append(analysis)
        total_baseline += analysis['baseline_violations']
        total_remaining += analysis['remaining_violations']

        pct_str = f"{analysis['violations_fixed_pct']}%"
        print(f"[{fixture_name}]")
        print(f"  Baseline: {analysis['baseline_violations']} violations")
        print(f"  Remaining: {analysis['remaining_violations']} violations")
        print(f"  Fixed: {analysis['violations_fixed']} ({pct_str})")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total baseline violations: {total_baseline}")
    print(f"Total remaining violations: {total_remaining}")
    print(f"Total violations fixed: {total_baseline - total_remaining}")

    if total_baseline > 0:
        overall_pct = ((total_baseline - total_remaining) / total_baseline * 100)
        print(f"Overall healing effectiveness: {overall_pct:.1f}%")

    print()
    print("=" * 70)

    # Save detailed report
    report = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'total_baseline_violations': total_baseline,
        'total_remaining_violations': total_remaining,
        'total_violations_fixed': total_baseline - total_remaining,
        'overall_healing_effectiveness_pct': round(
            ((total_baseline - total_remaining) / total_baseline * 100) if total_baseline > 0 else 0, 1
        ),
        'fixtures': results
    }

    report_file = BRAIN_TRAINING / 'wcag-healing-analysis.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved: wcag-healing-analysis.json")
    print()

if __name__ == '__main__':
    import sys
    variant = sys.argv[1] if len(sys.argv) > 1 else 'v11-production-ready'
    main(variant=variant)
