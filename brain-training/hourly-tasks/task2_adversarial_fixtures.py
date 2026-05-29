#!/usr/bin/env python3
"""Hour 2: Create 2 adversarial fixtures and validate v11 handles them."""
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / 'fixtures'
sys.path.insert(0, str(ROOT))

import deterministic_healer as dh
import wcag_validator as wv

print("=" * 60)
print("HOUR 2: Adversarial Fixtures (019, 020)")
print("=" * 60)

# Fixture 019: Deeply nested tables — no headers at any level
fx019 = FIXTURES / '019-nested-tables'
fx019.mkdir(exist_ok=True)
(fx019 / 'expected-html.html').write_text("""<!DOCTYPE html>
<html lang="en">
<head><title>Budget Matrix — Nested Tables</title></head>
<body><main>
<h1>Departmental Budget Matrix</h1>
<table>
<tr><td>Department</td><td>Q1</td><td>Q2</td><td>Q3</td><td>Q4</td></tr>
<tr><td>Public Works</td><td>
  <table>
  <tr><td>Labor</td><td>Materials</td><td>Equipment</td></tr>
  <tr><td>$120k</td><td>$45k</td><td>$30k</td></tr>
  </table>
</td><td>$198k</td><td>$210k</td><td>$225k</td></tr>
<tr><td>Parks</td><td>
  <table>
  <tr><td>Maintenance</td><td>Programs</td><td>Capital</td></tr>
  <tr><td>$55k</td><td>$30k</td><td>$15k</td></tr>
  </table>
</td><td>$102k</td><td>$98k</td><td>$110k</td></tr>
</table>
<button></button>
<button type="submit"></button>
</main></body></html>""")
(fx019 / 'source-metadata.json').write_text(json.dumps({
    'fixture_id': '019', 'name': 'nested-tables', 'phase': '3C-adversarial',
    'description': 'Deeply nested tables with no <th> headers at any level + empty buttons'
}, indent=2))

# Fixture 020: Unicode / international content — common in multilingual gov docs
fx020 = FIXTURES / '020-unicode-content'
fx020.mkdir(exist_ok=True)
(fx020 / 'expected-html.html').write_text("""<!DOCTYPE html>
<html>
<head></head>
<body>
<h2>Aviso Público / Public Notice / 公告</h2>
<p>The City of Maplewood provides services in multiple languages.</p>
<img src="notice-es.png">
<img src="notice-zh.png">
<img src="notice-ar.png">
<table>
<tr><td>Español</td><td>中文</td><td>العربية</td><td>Tiếng Việt</td></tr>
<tr><td>Servicios disponibles</td><td>可用服务</td><td>الخدمات المتاحة</td><td>Dịch vụ có sẵn</td></tr>
</table>
<a name="1"></a>
<a name="2"></a>
<a name="1"></a>
<p>Para información: <a href="mailto:info@maplewood.gov"></a></p>
<button></button>
</body>
</html>""")
(fx020 / 'source-metadata.json').write_text(json.dumps({
    'fixture_id': '020', 'name': 'unicode-content', 'phase': '3C-adversarial',
    'description': 'Multilingual government notice with Unicode content — tests that healer handles non-ASCII without corruption'
}, indent=2))

# Run wcag_validator on both new fixtures to establish baseline
for fx in [fx019, fx020]:
    html = (fx / 'expected-html.html').read_text()
    v = wv.validate_wcag_aa(html)
    baseline = {'fixture': fx.name, 'violations': v, 'html_size': len(html), 'timestamp': datetime.now().isoformat()}
    (fx / 'wcag-baseline.json').write_text(json.dumps(baseline, indent=2))
    print(f"[{fx.name}] baseline: {v['total']} violations")

# Run v11 on new fixtures only
report = dh.run_all_fixtures(variants=['v11-production-ready'])
for r in report['all_results']:
    if r['fixture'] in ('019-nested-tables', '020-unicode-content'):
        pct = r['violations_fixed_pct']
        status = "✅" if pct == 100.0 else f"⚠️ {pct}%"
        print(f"[{r['fixture']}] v11: {status} ({r['violations_fixed']}/{r['baseline_total']} fixed)")

print("\nDone — fixtures 019-020 created and validated.")
