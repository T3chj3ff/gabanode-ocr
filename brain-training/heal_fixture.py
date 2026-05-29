#!/usr/bin/env python3
"""
Healing Pipeline: Single Fixture Processor
Reads expected-html.html, applies healing prompts (v1-current, v6-healing-focused),
saves healed outputs, and validates with WCAG checker.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Try to import Gemini API — prefer new google-genai, fall back to deprecated google-generativeai
HAS_GEMINI = False
_GEMINI_CLIENT_MODE = None  # 'new' | 'legacy'

try:
    import google.genai as _genai_new  # preferred: pip install google-genai
    HAS_GEMINI = True
    _GEMINI_CLIENT_MODE = 'new'
except ImportError:
    try:
        import google.generativeai as _genai_legacy  # deprecated fallback
        HAS_GEMINI = True
        _GEMINI_CLIENT_MODE = 'legacy'
    except ImportError:
        print("⚠ No Gemini package found. Install with: pip install google-genai --break-system-packages")

# Deterministic healer (no API required — Project Euclid v8)
try:
    from deterministic_healer import apply_variant as _det_apply_variant, count_violations as _det_count_violations
    HAS_DETERMINISTIC = True
except ImportError:
    HAS_DETERMINISTIC = False

# Import WCAG validator from same directory
from rebenchmark_with_wcag import count_wcag_violations

BRAIN_TRAINING = Path(__file__).parent
FIXTURES_DIR = BRAIN_TRAINING / 'fixtures'

# V1-Current healing prompt (baseline)
V1_HEALING_PROMPT = """You are a WCAG 2.2 Level AA accessibility compliance expert.

Analyze the provided HTML and apply these healing passes in order:

PASS 1: Structure & Landmarks
- Wrap content in <main> if not present
- Ensure proper heading hierarchy (h1 → h2 → h3)
- Convert text-only lists to proper <ul>/<ol> structure

PASS 2: Attributes
- Add descriptive alt text to all images (based on context)
- Add aria-label or title to empty links
- Add name attributes to form inputs

PASS 3: Semantic
- Add ARIA roles where needed (button, navigation, etc.)
- Add table header scope (scope="col" or scope="row")
- Add aria-describedby for complex form fields

PASS 4: Validation
- Ensure all links have descriptive text
- Add lang attribute to <html> tag
- Verify no empty elements

Output ONLY the healed HTML, no explanations."""

# V6-Healing-Focused prompt (4-pass iterative)
V6_HEALING_PROMPT = """You are a WCAG 2.2 Level AA accessibility compliance expert.

Apply these 4-pass iterative healing approach:

PASS 1: Structure & Landmarks
- Add <main> landmark wrapping primary content
- Fix heading hierarchy to start with h1
- Convert semantic lists from text to proper markup
- Add <nav>, <aside>, <article>, <section> landmarks where appropriate

PASS 2: Attributes (Critical for Violations)
- Add descriptive alt text to all images (extract from surrounding content or infer)
- Add aria-label or title to empty <a> elements
- Add id + aria-labelledby to form inputs without labels
- Add aria-describedby for error messages

PASS 3: Semantic Enrichment
- Add ARIA roles (combobox, tablist, etc.) for interactive elements
- Add table header scope attributes (scope="col" for columns, scope="row" for rows)
- Add aria-live regions for dynamic content
- Add aria-disabled for non-interactive disabled elements

PASS 4: Validation & Polish
- Ensure all links have non-empty, descriptive text
- Add xml:lang and lang attributes to <html>
- Remove empty or whitespace-only elements
- Add aria-hidden="true" to decorative elements
- Verify complete landmark structure

Output ONLY the healed HTML with no explanations, comments, or markdown."""

def setup_gemini(api_key=None):
    """
    Initialize Gemini API client.
    Supports both google-genai (new) and google-generativeai (legacy).
    Returns an opaque handle used by _call_gemini().
    """
    if not HAS_GEMINI:
        return None

    if not api_key:
        import os
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

    if not api_key:
        print("⚠ GEMINI_API_KEY or GOOGLE_API_KEY not set in environment")
        return None

    try:
        if _GEMINI_CLIENT_MODE == 'new':
            # google-genai >= 1.0 (google.genai.Client)
            client = _genai_new.Client(api_key=api_key)
            return {'mode': 'new', 'client': client, 'model': 'gemini-2.0-flash'}
        else:
            # google-generativeai legacy
            _genai_legacy.configure(api_key=api_key)
            return {'mode': 'legacy', 'model': _genai_legacy.GenerativeModel('gemini-1.5-pro')}
    except Exception as e:
        print(f"✗ Failed to initialize Gemini: {e}")
        return None


def _call_gemini(handle: dict, prompt: str) -> str:
    """Call Gemini with the appropriate client handle and return response text."""
    if handle['mode'] == 'new':
        resp = handle['client'].models.generate_content(
            model=handle['model'], contents=prompt
        )
        return resp.text or ''
    else:
        resp = handle['model'].generate_content(prompt)
        return resp.text or ''

_DETERMINISTIC_VARIANTS = {
    'v7-deterministic-basic', 'v8-deterministic-images', 'v9-deterministic-full',
    'v7', 'v8', 'v9',
}
# Short-alias → canonical deterministic_healer.py variant name
_DET_ALIAS = {
    'v7': 'v7-deterministic-basic',
    'v8': 'v8-deterministic-images',
    'v9': 'v9-deterministic-full',
}


def heal_fixture(fixture_path, variant='v1-current', api_key=None):
    """
    Heal a single fixture using the specified variant.

    Args:
        fixture_path: Path to fixture directory.
        variant:      'v1-current', 'v6-healing-focused' (Gemini LLM) or
                      'v7' / 'v8' / 'v9' / 'v7-deterministic-basic' /
                      'v8-deterministic-images' / 'v9-deterministic-full'
                      (deterministic — no API required).
        api_key:      Optional Gemini API key (ignored for deterministic variants).

    Returns:
        dict with healing results and metrics.
    """
    fixture_path = Path(fixture_path)
    expected_html_file = fixture_path / 'expected-html.html'

    if not expected_html_file.exists():
        return {'error': f'expected-html.html not found in {fixture_path.name}'}

    baseline_html = expected_html_file.read_text()
    baseline_violations = count_wcag_violations(baseline_html)

    # ── Deterministic path (no API) ──────────────────────────────────────────
    if variant in _DETERMINISTIC_VARIANTS:
        if not HAS_DETERMINISTIC:
            return {
                'error': 'deterministic_healer.py not importable from this location',
                'fixture': fixture_path.name,
                'variant': variant,
                'baseline_violations': baseline_violations['total'],
            }
        det_variant     = _DET_ALIAS.get(variant, variant)
        healed_html     = _det_apply_variant(baseline_html, det_variant)
        healed_viol     = count_wcag_violations(healed_html)
        violations_fixed = baseline_violations['total'] - healed_viol['total']
        pct = (violations_fixed / baseline_violations['total'] * 100) if baseline_violations['total'] else 0.0

        healed_filename = f'healed-{variant}.html'
        (fixture_path / healed_filename).write_text(healed_html)

        return {
            'fixture':              fixture_path.name,
            'variant':              variant,
            'engine':               'deterministic',
            'baseline_violations':  baseline_violations['total'],
            'healed_violations':    healed_viol['total'],
            'violations_fixed':     violations_fixed,
            'violations_fixed_pct': round(pct, 1),
            'healed_file':          healed_filename,
            'timestamp':            datetime.now().isoformat(),
        }

    # ── LLM (Gemini) path ────────────────────────────────────────────────────
    prompt = V6_HEALING_PROMPT if variant == 'v6-healing-focused' else V1_HEALING_PROMPT

    gemini_handle = setup_gemini(api_key)
    if not gemini_handle:
        return {
            'error': 'Gemini API not available',
            'fixture': fixture_path.name,
            'variant': variant,
            'baseline_violations': baseline_violations['total'],
        }

    try:
        print(f"  → Calling Gemini [{_GEMINI_CLIENT_MODE}] for {variant}...", end='', flush=True)

        full_prompt = f"{prompt}\n\nHTML to heal:\n```html\n{baseline_html}\n```"
        healed_html = _call_gemini(gemini_handle, full_prompt)

        if not healed_html:
            print(" ✗ Empty response")
            return {'error': 'Empty Gemini response', 'fixture': fixture_path.name, 'variant': variant}

        # Strip markdown fences if present
        if healed_html.startswith('```'):
            healed_html = healed_html.split('\n', 1)[1]
        if healed_html.endswith('```'):
            healed_html = healed_html.rsplit('\n', 1)[0]

        healed_violations = count_wcag_violations(healed_html)
        violations_fixed  = baseline_violations['total'] - healed_violations['total']
        pct = (violations_fixed / baseline_violations['total'] * 100) if baseline_violations['total'] else 0.0

        healed_filename = f'healed-{variant}.html'
        (fixture_path / healed_filename).write_text(healed_html)

        print(f" ✓ {pct:.1f}% fixed")

        return {
            'fixture':              fixture_path.name,
            'variant':              variant,
            'engine':               f'gemini-{_GEMINI_CLIENT_MODE}',
            'baseline_violations':  baseline_violations['total'],
            'healed_violations':    healed_violations['total'],
            'violations_fixed':     violations_fixed,
            'violations_fixed_pct': round(pct, 1),
            'healed_file':          healed_filename,
            'timestamp':            datetime.now().isoformat(),
        }

    except Exception as e:
        print(f" ✗ {e}")
        return {
            'error':               str(e),
            'fixture':             fixture_path.name,
            'variant':             variant,
            'baseline_violations': baseline_violations['total'],
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: heal_fixture.py <fixture_name> [variant] [api_key]")
        print("  fixture_name: e.g., '001-simple-text' or '008-mixed-content'")
        print("  variant: 'v1-current' (default) or 'v6-healing-focused'")
        print("  api_key: Optional Gemini API key (or set GEMINI_API_KEY env var)")
        return

    fixture_name = sys.argv[1]
    variant = sys.argv[2] if len(sys.argv) > 2 else 'v1-current'
    api_key = sys.argv[3] if len(sys.argv) > 3 else None

    # Find fixture directory
    fixture_dir = None
    for d in FIXTURES_DIR.glob(f'*{fixture_name}*'):
        if d.is_dir():
            fixture_dir = d
            break

    if not fixture_dir:
        print(f"✗ Fixture '{fixture_name}' not found")
        return

    print(f"Healing fixture: {fixture_dir.name}")
    print(f"Variant: {variant}")
    print()

    result = heal_fixture(fixture_dir, variant, api_key)

    print()
    print("=" * 70)
    print("HEALING RESULT")
    print("=" * 70)
    print(json.dumps(result, indent=2))

    # Save result
    result_file = fixture_dir / f'healing-{variant}-result.json'
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print()
    print(f"Result saved: {result_file.name}")

if __name__ == '__main__':
    main()
