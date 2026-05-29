#!/usr/bin/env python3
"""
Batch Healing Pipeline: Process All Fixtures
Runs all 9 fixtures through both v1-current and v6-healing-focused variants,
generates healed HTML files, and produces comprehensive healing analysis report.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Try to import Gemini API — prefer new google-genai, fall back to deprecated google-generativeai
HAS_GEMINI = False
_GEMINI_CLIENT_MODE = None  # 'new' | 'legacy'

try:
    import google.genai as genai  # preferred: pip install google-genai
    HAS_GEMINI = True
    _GEMINI_CLIENT_MODE = 'new'
except ImportError:
    try:
        import google.generativeai as genai  # deprecated fallback
        HAS_GEMINI = True
        _GEMINI_CLIENT_MODE = 'legacy'
    except ImportError:
        pass  # heal_fixture will handle missing Gemini gracefully

from heal_fixture import heal_fixture, setup_gemini

BRAIN_TRAINING = Path(__file__).parent
FIXTURES_DIR = BRAIN_TRAINING / 'fixtures'

def heal_all_fixtures(api_key=None, variants=None):
    """
    Heal all fixtures with specified variants.

    Args:
        api_key: Optional Gemini API key
        variants: List of variants to test (default: ['v1-current', 'v6-healing-focused'])

    Returns:
        dict with comprehensive healing analysis
    """
    if variants is None:
        variants = ['v1-current', 'v6-healing-focused']

    # Verify Gemini is available
    if HAS_GEMINI:
        model = setup_gemini(api_key)
        if not model:
            print("✗ Cannot initialize Gemini API. Set GEMINI_API_KEY environment variable.")
            return None
    else:
        print("⚠ google-generativeai not installed. Healing pipeline requires it.")
        print("  Install with: pip install google-generativeai --break-system-packages")
        return None

    print("PHASE 2C-1: Batch Healing Pipeline")
    print("=" * 70)
    print(f"Fixtures: All 9 in {FIXTURES_DIR}")
    print(f"Variants: {', '.join(variants)}")
    print(f"Total jobs: {len(list(FIXTURES_DIR.glob('*-*'))) * len(variants)}")
    print()

    # Discover all fixtures
    fixtures = sorted([d for d in FIXTURES_DIR.glob('*-*') if d.is_dir()])

    if not fixtures:
        print("✗ No fixtures found")
        return None

    # Process each fixture × variant
    all_results = []
    summary_by_variant = {}

    for variant in variants:
        print(f"\n{'=' * 70}")
        print(f"VARIANT: {variant}")
        print(f"{'=' * 70}\n")

        variant_results = []
        variant_total_baseline = 0
        variant_total_fixed = 0

        for fixture_dir in fixtures:
            fixture_name = fixture_dir.name
            print(f"[{fixture_name}]", end=' ', flush=True)

            result = heal_fixture(fixture_dir, variant, api_key)

            if 'error' in result:
                print(f"✗ {result['error']}")
            else:
                print(
                    f"✓ {result['violations_fixed_pct']:.1f}% "
                    f"({result['violations_fixed']}/{result['baseline_violations']})"
                )
                variant_results.append(result)
                variant_total_baseline += result['baseline_violations']
                variant_total_fixed += result['violations_fixed']

            all_results.append(result)

        # Calculate variant summary
        if variant_total_baseline > 0:
            variant_pct = (variant_total_fixed / variant_total_baseline * 100)
        else:
            variant_pct = 0

        summary_by_variant[variant] = {
            'total_baseline_violations': variant_total_baseline,
            'total_violations_fixed': variant_total_fixed,
            'overall_healing_pct': round(variant_pct, 1),
            'fixtures_processed': len(variant_results),
            'fixtures_with_errors': len(fixtures) - len(variant_results),
        }

        print(f"\n{variant} Summary:")
        print(f"  Baseline: {variant_total_baseline} violations")
        print(f"  Fixed: {variant_total_fixed} violations")
        print(f"  Healing effectiveness: {variant_pct:.1f}%")

    # Comparison analysis
    print(f"\n{'=' * 70}")
    print("COMPARISON: v1-current vs v6-healing-focused")
    print(f"{'=' * 70}\n")

    v1_results = summary_by_variant.get('v1-current', {})
    v6_results = summary_by_variant.get('v6-healing-focused', {})

    if v1_results and v6_results:
        v1_pct = v1_results.get('overall_healing_pct', 0)
        v6_pct = v6_results.get('overall_healing_pct', 0)
        improvement = v6_pct - v1_pct

        print(f"v1-current healing:         {v1_pct:.1f}%")
        print(f"v6-healing-focused healing: {v6_pct:.1f}%")
        print(f"Improvement:                +{improvement:.1f} percentage points")

        if improvement >= 10:
            print(f"\n✓ SUCCESS: v6 improves healing by {improvement:.1f}pp (target: ≥10pp)")
        else:
            print(f"\n⚠ v6 improvement is {improvement:.1f}pp (target: ≥10pp)")

    # Compile comprehensive report
    report = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'phase': '2C-1',
            'pipeline': 'batch-healing',
            'fixtures_total': len(fixtures),
            'variants_tested': variants,
        },
        'summary_by_variant': summary_by_variant,
        'all_results': all_results,
        'comparison': {
            'v1_healing_pct': v1_results.get('overall_healing_pct', 0),
            'v6_healing_pct': v6_results.get('overall_healing_pct', 0),
            'improvement_pct': (v6_results.get('overall_healing_pct', 0) - v1_results.get('overall_healing_pct', 0)),
        },
    }

    return report

def main():
    print()

    # Get API key from argument or environment
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

    # Run healing pipeline
    report = heal_all_fixtures(api_key)

    if not report:
        print("\n✗ Healing pipeline failed")
        sys.exit(1)

    print(f"\n{'=' * 70}")
    print("HEALING ANALYSIS REPORT")
    print(f"{'=' * 70}\n")
    print(json.dumps(report, indent=2))

    # Save comprehensive report
    report_file = BRAIN_TRAINING / 'healing-analysis-v1-vs-v6.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print()
    print(f"✓ Report saved: {report_file.name}")
    print()

    # Save variant-specific reports
    for variant, summary in report['summary_by_variant'].items():
        variant_file = BRAIN_TRAINING / f'healing-summary-{variant}.json'
        with open(variant_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary saved: {variant_file.name}")

    print()
    print("Next steps:")
    print("  1. Review healing-analysis-v1-vs-v6.json for detailed results")
    print("  2. Check individual healed-*.html files in each fixture directory")
    print("  3. Run multi-model testing (Phase 3) if improvement meets criteria")

if __name__ == '__main__':
    main()
