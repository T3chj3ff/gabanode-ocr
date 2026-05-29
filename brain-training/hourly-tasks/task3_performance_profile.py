#!/usr/bin/env python3
"""Hour 3: Profile each healer pass — timing per fixture, identify bottlenecks."""
import time, json, sys, statistics
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / 'fixtures'
sys.path.insert(0, str(ROOT))
import deterministic_healer as dh

PASSES = [
    ('fix_lang_attribute',   dh.fix_lang_attribute),
    ('fix_main_landmark',    dh.fix_main_landmark),
    ('fix_image_alt',        dh.fix_image_alt),
    ('fix_empty_anchors',    dh.fix_empty_anchors),
    ('fix_empty_links',      dh.fix_empty_links),
    ('fix_form_labels',      dh.fix_form_labels),
    ('fix_table_scope',      dh.fix_table_scope),
    ('fix_heading_hierarchy',dh.fix_heading_hierarchy),
    ('fix_table_headers',    dh.fix_table_headers),
    ('fix_form_ids',         dh.fix_form_ids),
    ('fix_page_title',       dh.fix_page_title),
    ('fix_duplicate_ids',    dh.fix_duplicate_ids),
    ('fix_button_labels',    dh.fix_button_labels),
]

print("=" * 60)
print("HOUR 3: Performance Profiling — All Passes × All Fixtures")
print("=" * 60)

fixtures = sorted([d for d in FIXTURES.glob('*-*') if d.is_dir()])
pass_times = {name: [] for name, _ in PASSES}
fixture_totals = {}

for fx in fixtures:
    src = fx / 'expected-html.html'
    if not src.exists(): continue
    html = src.read_text()
    total_ms = 0
    for name, fn in PASSES:
        t0 = time.perf_counter()
        html = fn(html)
        elapsed = (time.perf_counter() - t0) * 1000
        pass_times[name].append(elapsed)
        total_ms += elapsed
    fixture_totals[fx.name] = round(total_ms, 3)

report = {
    'generated': datetime.now().isoformat(),
    'fixtures_tested': len(fixtures),
    'pass_timing_ms': {},
    'fixture_totals_ms': fixture_totals,
    'slowest_pass': None,
    'fastest_pass': None,
    'total_pipeline_avg_ms': round(sum(fixture_totals.values()) / len(fixture_totals), 3) if fixture_totals else 0,
}

print(f"\n{'Pass':<26} {'Mean ms':>8} {'Max ms':>8} {'Total ms':>10}")
print("-" * 56)
for name, times in pass_times.items():
    mean_ms = statistics.mean(times)
    max_ms  = max(times)
    total_ms = sum(times)
    report['pass_timing_ms'][name] = {'mean_ms': round(mean_ms,3), 'max_ms': round(max_ms,3), 'total_ms': round(total_ms,3)}
    print(f"  {name:<24} {mean_ms:>8.3f} {max_ms:>8.3f} {total_ms:>10.3f}")

slowest = max(report['pass_timing_ms'], key=lambda k: report['pass_timing_ms'][k]['mean_ms'])
fastest = min(report['pass_timing_ms'], key=lambda k: report['pass_timing_ms'][k]['mean_ms'])
report['slowest_pass'] = slowest
report['fastest_pass'] = fastest

print(f"\nSlowest pass: {slowest} ({report['pass_timing_ms'][slowest]['mean_ms']:.3f}ms avg)")
print(f"Fastest pass: {fastest} ({report['pass_timing_ms'][fastest]['mean_ms']:.3f}ms avg)")
print(f"Avg full pipeline per fixture: {report['total_pipeline_avg_ms']:.3f}ms")

out = ROOT / 'timing_report.json'
out.write_text(json.dumps(report, indent=2))
print(f"\nReport: {out.name}")
