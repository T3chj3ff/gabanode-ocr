#!/usr/bin/env python3
"""Hour 1: Full regression check on v11 + axe-core test manifest generation."""
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import deterministic_healer as dh
import wcag_validator as wv

print("=" * 60)
print("HOUR 1: Regression Check + Axe-Core Manifest")
print("=" * 60)

report = dh.run_all_fixtures(variants=['v11-production-ready'])
overall = report['summary_by_variant']['v11-production-ready']['overall_pct']
status = "PASS ✅" if overall == 100.0 else f"FAIL ❌ ({overall}%)"
print(f"\nRegression: {status}")

# Build axe manifest
fixtures_dir = ROOT / 'fixtures'
manifest = {'generated': datetime.now().isoformat(), 'engine': 'v11-production-ready', 'fixtures': [], 'summary': {}}
total_base, total_rem = 0, 0
for fx in sorted(fixtures_dir.glob('*-*')):
    if not fx.is_dir(): continue
    baseline_f = fx / 'wcag-baseline.json'
    healed_f   = fx / 'healed-v11-production-ready.html'
    if not baseline_f.exists() or not healed_f.exists(): continue
    base = json.loads(baseline_f.read_text())
    bcount = base['violations']['total']
    healed_html = healed_f.read_text()
    rem = wv.validate_wcag_aa(healed_html)['total']
    total_base += bcount; total_rem += rem
    manifest['fixtures'].append({
        'id': fx.name, 'baseline_violations': bcount,
        'remaining_violations': rem, 'healing_pct': round((bcount-rem)/bcount*100,1) if bcount else 0.0,
        'axe_ready': rem == 0
    })

manifest['summary'] = {'total_fixtures': len(manifest['fixtures']), 'all_at_100pct': total_rem == 0,
                        'total_baseline_violations': total_base, 'total_remaining': total_rem}
out = ROOT / 'axe_test_manifest.json'
out.write_text(json.dumps(manifest, indent=2))
print(f"Axe manifest: {out.name} ({len(manifest['fixtures'])} fixtures, all_at_100={manifest['summary']['all_at_100pct']})")
