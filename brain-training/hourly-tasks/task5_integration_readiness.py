#!/usr/bin/env python3
"""Hour 5: HTML5 validity check + integration readiness report for pdf-htmlremediation."""
import re, json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / 'fixtures'
sys.path.insert(0, str(ROOT))
import wcag_validator as wv

print("=" * 60)
print("HOUR 5: Integration Readiness Report")
print("=" * 60)

checks = []
for fx in sorted(FIXTURES.glob('*-*')):
    if not fx.is_dir(): continue
    healed = fx / 'healed-v11-production-ready.html'
    if not healed.exists(): continue
    html = healed.read_text()

    issues = []
    # 1. Has DOCTYPE
    if not re.search(r'<!DOCTYPE\s+html', html, re.IGNORECASE):
        issues.append('missing_doctype')
    # 2. Has <html lang>
    if not re.search(r'<html\b[^>]*\s+lang="[a-zA-Z]', html, re.IGNORECASE):
        issues.append('missing_lang')
    # 3. Has <head><title>
    if not re.search(r'<title>[^<]+</title>', html, re.IGNORECASE):
        issues.append('missing_title')
    # 4. Has <main>
    if not re.search(r'<main[\s>]', html, re.IGNORECASE):
        issues.append('missing_main')
    # 5. No duplicate IDs
    ids = re.findall(r'\bid="([^"]+)"', html, re.IGNORECASE)
    if len(ids) != len(set(ids)):
        issues.append('duplicate_ids')
    # 6. WCAG violations remaining
    v = wv.validate_wcag_aa(html)
    remaining = v['total']

    status = '✅ READY' if not issues and remaining == 0 else f'⚠️ {len(issues)} structural + {remaining} WCAG'
    print(f"  [{fx.name}] {status}")
    checks.append({
        'fixture': fx.name,
        'structural_issues': issues,
        'wcag_remaining': remaining,
        'ready': not issues and remaining == 0
    })

ready_count = sum(1 for c in checks if c['ready'])
total = len(checks)
print(f"\nReady: {ready_count}/{total} fixtures")

# Recommendation for pdf-htmlremediation integration
report_lines = [
    f'# Integration Readiness Report — Project Euclid v11',
    f'**Generated:** {datetime.now().strftime("%Y-%m-%d")}',
    f'**Engine:** v11-production-ready',
    f'**Result:** {ready_count}/{total} fixtures fully integration-ready',
    f'',
    f'## Fixture Status',
    f'| Fixture | Structural | WCAG Remaining | Status |',
    f'|---------|-----------|----------------|--------|',
]
for c in checks:
    structural = ', '.join(c['structural_issues']) if c['structural_issues'] else 'None'
    icon = '✅' if c['ready'] else '⚠️'
    report_lines.append(f"| {c['fixture']} | {structural} | {c['wcag_remaining']} | {icon} |")

report_lines += [
    f'',
    f'## Integration Recommendation',
    f'',
    f'v11-production-ready is **{"READY" if ready_count == total else "CONDITIONALLY READY"}** for integration into `pdf-htmlremediation`.',
    f'',
    f'**Integration steps:**',
    f'1. Copy `deterministic_healer.py` → `pdf-htmlremediation/src/healer.py`',
    f'2. Entry point: `apply_variant(html, "v11-production-ready")`',
    f'3. Wire `wcag_validator.validate_wcag_aa()` as the post-heal QA check',
    f'4. Expose per-fixture healing % via arena-dashboard WCAG audit UI',
    f'5. Add timing instrumentation (see `timing_report.json` from Hour 3)',
    f'',
    f'**Phase 3D (next):** Color contrast analysis — 1.4.3 AA criterion',
]

out = ROOT / 'integration_readiness_report.md'
out.write_text('\n'.join(report_lines))
print(f"Report: {out.name}")
