#!/usr/bin/env python3
"""
WCAG 2.2 Level AA Violation Detector
Analyzes HTML for common accessibility violations using pattern matching.
Not a replacement for axe-core but provides baseline WCAG validation.

Phase 3D: Color contrast (WCAG 1.4.3 AA — min 4.5:1 normal text, 3:1 large text)
  Detects hardcoded inline style= colors that fail the AA contrast ratio against
  an assumed white (#ffffff) background. Only flags colors we can parse
  deterministically (hex, rgb(), named). Skips dynamic/class-based colors.
"""

import json
import re
from pathlib import Path
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# Phase 3D — Color contrast helpers (WCAG 1.4.3 AA)
# ---------------------------------------------------------------------------

# Named CSS colors → hex (common subset likely to appear in generated HTML)
_NAMED_COLORS = {
    'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000',
    'blue': '#0000ff', 'yellow': '#ffff00', 'orange': '#ffa500', 'purple': '#800080',
    'gray': '#808080', 'grey': '#808080', 'lightgray': '#d3d3d3', 'lightgrey': '#d3d3d3',
    'darkgray': '#a9a9a9', 'darkgrey': '#a9a9a9', 'silver': '#c0c0c0',
    'maroon': '#800000', 'navy': '#000080', 'teal': '#008080', 'lime': '#00ff00',
    'aqua': '#00ffff', 'cyan': '#00ffff', 'fuchsia': '#ff00ff', 'magenta': '#ff00ff',
    'pink': '#ffc0cb', 'lightblue': '#add8e6', 'lightyellow': '#ffffe0',
    'lightgreen': '#90ee90', 'darkred': '#8b0000', 'darkblue': '#00008b',
    'darkgreen': '#006400', 'coral': '#ff7f50', 'salmon': '#fa8072',
    'goldenrod': '#daa520', 'gold': '#ffd700', 'khaki': '#f0e68c',
    'indigo': '#4b0082', 'violet': '#ee82ee', 'brown': '#a52a2a',
    'beige': '#f5f5dc', 'ivory': '#fffff0', 'lavender': '#e6e6fa',
    'tan': '#d2b48c', 'wheat': '#f5deb3', 'crimson': '#dc143c',
    'tomato': '#ff6347', 'chocolate': '#d2691e', 'peru': '#cd853f',
}

def _hex_to_rgb(hex_color: str):
    """Parse #rrggbb or #rgb → (r, g, b) tuple of ints 0-255."""
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) != 6:
        return None
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return None

def _parse_color(value: str):
    """Return (r, g, b) from a CSS color string, or None if unparseable."""
    value = value.strip().lower()
    if value.startswith('#'):
        return _hex_to_rgb(value)
    m = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', value)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return _NAMED_COLORS.get(value, None) and _hex_to_rgb(_NAMED_COLORS[value])

def _relative_luminance(r, g, b) -> float:
    """WCAG 2.1 relative luminance (0-1 range)."""
    def lin(c):
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def _contrast_ratio(rgb1, rgb2) -> float:
    """WCAG contrast ratio between two (r,g,b) tuples."""
    l1 = _relative_luminance(*rgb1)
    l2 = _relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker  = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

_WHITE_RGB = (255, 255, 255)
_AA_NORMAL  = 4.5   # WCAG 1.4.3 AA: normal text
_AA_LARGE   = 3.0   # WCAG 1.4.3 AA: large text (≥18pt or ≥14pt bold)

def _extract_inline_color_violations(html_content: str) -> list:
    """
    Scan all style= attributes for color: <value> declarations.
    Returns list of dicts with {element, color, ratio, threshold}.
    Assumes white (#ffffff) background — the safest default for documents.
    """
    failures = []
    # Match any tag with a style attribute containing color:
    pattern = re.compile(
        r'<([a-z][a-z0-9]*)[^>]*\bstyle="([^"]*)"[^>]*>',
        re.IGNORECASE | re.DOTALL
    )
    color_decl = re.compile(r'\bcolor\s*:\s*([^;}"]+)', re.IGNORECASE)

    for m in pattern.finditer(html_content):
        tag  = m.group(1).lower().lstrip('<').split()[0]
        style = m.group(2)
        cm = color_decl.search(style)
        if not cm:
            continue
        color_str = cm.group(1).strip()
        rgb = _parse_color(color_str)
        if rgb is None:
            continue  # Can't parse — skip (don't false-positive)
        ratio = _contrast_ratio(rgb, _WHITE_RGB)
        # Large text applies to h1-h6 with >= 18pt or bold — treat all headings as large text
        threshold = _AA_LARGE if tag in ('h1','h2','h3','h4','h5','h6') else _AA_NORMAL
        if ratio < threshold:
            failures.append({
                'element': tag,
                'color': color_str,
                'ratio': round(ratio, 2),
                'threshold': threshold,
                'description': f'<{tag}> color:{color_str} ratio {ratio:.2f}:1 < {threshold}:1 AA'
            })
    return failures

def _extract_style_blocks(html_content: str) -> list:
    """Return inline <style> contents with comments removed."""
    blocks = []
    for m in re.finditer(
        r'<style\b[^>]*>(.*?)</style>',
        html_content,
        re.IGNORECASE | re.DOTALL,
    ):
        css = m.group(1)
        css = re.sub(r'<!--|-->', '', css)
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        blocks.append(css)
    return blocks

def _extract_focus_visible_removed(html_content: str) -> list:
    """Find :focus rules that remove outlines without a visible replacement."""
    failures = []
    css = "\n".join(_extract_style_blocks(html_content))
    focus_rule = re.compile(r'([^{}]*:focus[^{}]*)\{([^{}]*)\}', re.IGNORECASE | re.DOTALL)
    outline_removed = re.compile(
        r'\boutline\s*:\s*(?:none|0(?:\s+none)?)(?:\s*!important)?\s*(?:;|$)',
        re.IGNORECASE,
    )
    visible_replacement = re.compile(
        r'\b(?:outline\s*:\s*(?!\s*(?:none|0)\b)[^;]+|'
        r'box-shadow\s*:\s*(?!none\b)[^;]+|'
        r'border(?:-color|-style|-width)?\s*:\s*(?!none\b)[^;]+|'
        r'background(?:-color)?\s*:\s*[^;]+)',
        re.IGNORECASE,
    )
    for m in focus_rule.finditer(css):
        selector = " ".join(m.group(1).split())
        declarations = m.group(2)
        if outline_removed.search(declarations) and not visible_replacement.search(declarations):
            failures.append(
                f'{selector} removes focus outline without visible replacement (WCAG 2.4.7)'
            )
    return failures

_AUTOCOMPLETE_PATTERNS = [
    (re.compile(r'\b(?:given[-_]?name|first[-_]?name|firstname)\b', re.IGNORECASE), 'given-name'),
    (re.compile(r'\b(?:family[-_]?name|last[-_]?name|lastname|surname)\b', re.IGNORECASE), 'family-name'),
    (re.compile(r'\b(?:email|e[-_]?mail)\b', re.IGNORECASE), 'email'),
    (re.compile(r'\b(?:tel|phone|telephone|mobile)\b', re.IGNORECASE), 'tel'),
    (re.compile(r'\b(?:street[-_]?address|address[-_]?line1|mailing[-_]?address|address|street)\b', re.IGNORECASE), 'street-address'),
    (re.compile(r'\b(?:postal[-_]?code|postcode|zip[-_]?code|zip)\b', re.IGNORECASE), 'postal-code'),
    (re.compile(r'\b(?:country[-_]?name|country)\b', re.IGNORECASE), 'country-name'),
]

def _autocomplete_token_for_field(field: dict):
    """Map input name/id to a WCAG 1.3.5 autocomplete token, if applicable."""
    haystack = f'{field.get("name", "")} {field.get("id", "")}'
    for pattern, token in _AUTOCOMPLETE_PATTERNS:
        if pattern.search(haystack):
            return token
    return None

def _extract_prefers_reduced_motion_missing(html_content: str) -> list:
    """Find animation/transition CSS without a reduced-motion override."""
    css = "\n".join(_extract_style_blocks(html_content))
    if not css:
        return []
    if re.search(r'@media\s*\(\s*prefers-reduced-motion\s*:', css, re.IGNORECASE):
        return []

    failures = []
    for name in re.findall(r'@keyframes\s+([a-zA-Z0-9_-]+)', css, re.IGNORECASE):
        failures.append(
            f'@keyframes {name} has no prefers-reduced-motion override (WCAG 2.3.3)'
        )

    rule_re = re.compile(r'([^{}@][^{}]*)\{([^{}]*)\}', re.IGNORECASE | re.DOTALL)
    motion_decl = re.compile(
        r'\b(?:animation(?:-[a-z-]+)?|transition(?:-[a-z-]+)?)\s*:\s*(?!none\b)([^;]+)',
        re.IGNORECASE,
    )
    for m in rule_re.finditer(css):
        selector = " ".join(m.group(1).split())
        declarations = m.group(2)
        if selector.startswith('@'):
            continue
        if motion_decl.search(declarations):
            failures.append(
                f'{selector} uses animation/transition with no prefers-reduced-motion override (WCAG 2.3.3)'
            )
    return failures

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.violations = {}
        self.tag_stack = []
        self.elements = {
            'images': [],
            'links': [],
            'headings': [],
            'forms': [],
            'tables': [],
            'landmarks': [],
            'text_nodes': [],
            'buttons': [],      # Phase 3C: button_missing_label
            'inputs': [],       # Run 48: autocomplete_missing
            'status_regions': [], # Run 48: aria_live_missing
        }
        self._in_button = False
        self._button_text = ''
        self._button_attrs = {}
        self.in_script = False
        self._in_table = False  # track whether we're inside a <table>

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'script':
            self.in_script = True
        if tag == 'style':
            self.in_script = True

        self.tag_stack.append(tag)

        # Image validation
        if tag == 'img':
            self.elements['images'].append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', ''),
                'title': attrs_dict.get('title', ''),
            })

        # Link validation
        if tag == 'a':
            # title or aria-label both satisfy accessible name requirement
            accessible_name = (attrs_dict.get('title', '')
                               or attrs_dict.get('aria-label', '')).strip()
            self.elements['links'].append({
                'href': attrs_dict.get('href', ''),
                'text': '',
                'title': accessible_name,
            })

        # Heading validation
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.elements['headings'].append({
                'tag': tag,
                'text': '',
            })

        # Form validation
        if tag in ['input', 'textarea', 'select']:
            self.elements['forms'].append({
                'type': attrs_dict.get('type', ''),
                'id': attrs_dict.get('id', ''),
                'name': attrs_dict.get('name', ''),
                'label_id': attrs_dict.get('aria-labelledby', ''),
            })
        if tag == 'input':
            self.elements['inputs'].append({
                'type': attrs_dict.get('type', 'text'),
                'id': attrs_dict.get('id', ''),
                'name': attrs_dict.get('name', ''),
                'autocomplete': attrs_dict.get('autocomplete', ''),
            })
        if tag == 'div':
            self.elements['status_regions'].append({
                'id': attrs_dict.get('id', ''),
                'role': attrs_dict.get('role', ''),
                'aria_live': attrs_dict.get('aria-live', ''),
            })

        # Table validation
        if tag == 'table':
            self._in_table = True
            self.elements['tables'].append({
                'has_thead': False,
                'has_th': False,
                'headers': [],
                'rows': 0,
            })
        if tag == 'th' and self.elements['tables']:
            self.elements['tables'][-1]['has_th'] = True

        # Landmark validation
        if tag in ['main', 'nav', 'aside', 'footer', 'article', 'section']:
            self.elements['landmarks'].append(tag)

        # Button validation (Phase 3C)
        if tag == 'button':
            self._in_button = True
            self._button_text = ''
            self._button_attrs = attrs_dict

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        if tag == 'style':
            self.in_script = False
        if tag == 'table':
            self._in_table = False

        # Capture button accessible name (Phase 3C)
        if tag == 'button' and self._in_button:
            self._in_button = False
            aria_label = (self._button_attrs.get('aria-label', '')
                          or self._button_attrs.get('aria-labelledby', '')
                          or self._button_attrs.get('title', '')).strip()
            self.elements['buttons'].append({
                'text':       self._button_text.strip(),
                'aria_label': aria_label,
                'type':       self._button_attrs.get('type', 'button'),
            })

        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_script:
            return

        text = data.strip()
        if not text:
            return

        self.elements['text_nodes'].append(text)

        # Track heading text
        if self.tag_stack and self.tag_stack[-1].startswith('h'):
            if self.elements['headings']:
                self.elements['headings'][-1]['text'] += text

        # Track link text
        if self.tag_stack and 'a' in self.tag_stack:
            if self.elements['links']:
                self.elements['links'][-1]['text'] += text

        # Track button text (Phase 3C)
        if self._in_button:
            self._button_text += text

def validate_wcag_aa(html_content):
    """Analyze HTML for WCAG 2.2 AA violations"""
    violations = {
        'image_missing_alt': [],
        'link_empty_text': [],
        'heading_hierarchy_broken': [],
        'form_input_missing_label': [],
        'table_missing_header_scope': [],
        'no_main_landmark': [],
        'text_only_lists': [],
        'missing_lang_attribute': [],
        # Phase 3C — new violation types
        'missing_page_title': [],
        'duplicate_id': [],
        'button_missing_label': [],
        # Phase 3D — color contrast (WCAG 1.4.3 AA)
        'color_contrast_insufficient': [],
        # Phase 4A — skip navigation (WCAG 2.4.1)
        'skip_nav_missing': [],
        # Phase 4B — tabindex positive value (WCAG 2.4.3)
        'tabindex_positive_value': [],
        # Phase 4B — iframe missing title (WCAG 4.1.2)
        'iframe_missing_title': [],
        # Phase 4B — inline SVG missing accessible name (WCAG 1.1.1)
        'svg_missing_accessible_name': [],
        # Run 48 — corpus expansion detectors
        'focus_visible_removed': [],
        'autocomplete_missing': [],
        'aria_live_missing': [],
        'prefers_reduced_motion_missing': [],
        'total': 0
    }

    if not html_content:
        return violations

    # Parse HTML
    parser = HTMLValidator()
    try:
        parser.feed(html_content)
    except:
        pass

    # Check for images without alt text
    for img in parser.elements['images']:
        if not img['alt'] and not img['title']:
            violations['image_missing_alt'].append(img['src'])

    # Check for links without text
    for link in parser.elements['links']:
        if not link['text'].strip() and not link['title']:
            violations['link_empty_text'].append(link['href'])

    # Check heading hierarchy
    headings = parser.elements['headings']
    if headings:
        first_heading = int(headings[0]['tag'][1])
        if first_heading != 1:
            violations['heading_hierarchy_broken'].append(f"First heading is {first_heading}, should be h1")

        for i in range(len(headings) - 1):
            curr = int(headings[i]['tag'][1])
            next_h = int(headings[i+1]['tag'][1])
            if next_h > curr + 1:
                violations['heading_hierarchy_broken'].append(f"{headings[i]['tag']} → {headings[i+1]['tag']} (skip detected)")

    # Check form inputs — submit/reset/button/hidden/image do not require labels per WCAG SC 1.3.1
    _no_label_required = {'submit', 'reset', 'button', 'hidden', 'image'}
    for form in parser.elements['forms']:
        if form['type'].lower() in _no_label_required:
            continue
        if not form['label_id'] and (not form['id'] or not form['name']):
            violations['form_input_missing_label'].append(f"Input type={form['type']}, id={form['id']}")

    # Check for landmarks
    if not parser.elements['landmarks']:
        violations['no_main_landmark'].append('Missing <main> landmark')

    # Check HTML lang attribute — use regex so lang= anywhere in the <html> tag is found
    # (not just '<html lang=' as a direct substring, which misses xml:lang="x" lang="en" patterns)
    import re as _re
    if not _re.search(r'<html\b[^>]*\s+lang="[a-zA-Z]', html_content, _re.IGNORECASE):
        violations['missing_lang_attribute'].append('HTML missing lang attribute')

    # Check tables — per-table: flag tables that contain no <th> elements
    for table in parser.elements['tables']:
        if not table.get('has_th', False):
            violations['table_missing_header_scope'].append('Table missing <th> elements')

    # Phase 3C: Check for missing/empty <title> (WCAG 2.4.2)
    if not re.search(r'<title>[^<\s][^<]*</title>', html_content, re.IGNORECASE):
        violations['missing_page_title'].append('Missing or empty <title> element')

    # Phase 3C: Check for duplicate id attributes (WCAG 4.1.1)
    all_ids = re.findall(r'\bid="([^"]+)"', html_content, re.IGNORECASE)
    seen_ids = set()
    for id_val in all_ids:
        if id_val in seen_ids:
            violations['duplicate_id'].append(f'Duplicate id="{id_val}"')
        seen_ids.add(id_val)

    # Phase 3C: Check for buttons without accessible names (WCAG 4.1.2)
    for btn in parser.elements['buttons']:
        if not btn['text'] and not btn['aria_label']:
            violations['button_missing_label'].append(
                f'Button type={btn["type"]} has no accessible name'
            )

    # Phase 3D: Color contrast (WCAG 1.4.3 AA)
    for failure in _extract_inline_color_violations(html_content):
        violations['color_contrast_insufficient'].append(failure['description'])

    # Phase 4A: Skip navigation (WCAG 2.4.1)
    # Required when page has repeated nav + main content. Check for skip link near body start.
    if re.search(r'<main\b', html_content, re.IGNORECASE):
        body_m = re.search(r'<body\b[^>]*>(.*)', html_content, re.IGNORECASE | re.DOTALL)
        body_start = body_m.group(1)[:400] if body_m else html_content[:400]
        has_skip = re.search(
            r'<a\b[^>]*href="#[^"]*"[^>]*>\s*[Ss]kip',
            body_start, re.IGNORECASE
        )
        if not has_skip:
            violations['skip_nav_missing'].append(
                'No skip navigation link before main content (WCAG 2.4.1)'
            )

    # Phase 4B: Positive tabindex values (WCAG 2.4.3)
    for m in re.finditer(r'\btabindex="([1-9][0-9]*)"', html_content, re.IGNORECASE):
        violations['tabindex_positive_value'].append(
            f'tabindex="{m.group(1)}" disrupts natural focus order'
        )

    # Phase 4B: iframe missing title attribute (WCAG 4.1.2)
    for m in re.finditer(r'<iframe\b([^>]*)(?:/>|>)', html_content, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        if not re.search(r'\btitle=', attrs, re.IGNORECASE):
            src_m = re.search(r'\bsrc="([^"]*)"', attrs, re.IGNORECASE)
            src = src_m.group(1) if src_m else '(no src)'
            violations['iframe_missing_title'].append(
                f'<iframe src="{src}"> missing title attribute (WCAG 4.1.2)'
            )

    # Phase 4B: inline SVG missing accessible name (WCAG 1.1.1)
    for m in re.finditer(r'(<svg\b[^>]*>)(.*?)(</svg>)', html_content, re.IGNORECASE | re.DOTALL):
        tag_attrs = m.group(1)
        content   = m.group(2)
        if re.search(r'\baria-label\s*=', tag_attrs, re.IGNORECASE):
            continue
        if re.search(r'\baria-hidden\s*=\s*"true"', tag_attrs, re.IGNORECASE):
            continue
        if re.search(r'\brole\s*=\s*"(?:presentation|none)"', tag_attrs, re.IGNORECASE):
            continue
        if re.search(r'<title\b', content, re.IGNORECASE):
            continue
        violations['svg_missing_accessible_name'].append(
            'Inline <svg> has no accessible name — add <title>, aria-label, or role="presentation" (WCAG 1.1.1)'
        )

    # Run 48: Focus visible removed (WCAG 2.4.7)
    violations['focus_visible_removed'].extend(
        _extract_focus_visible_removed(html_content)
    )

    # Run 48: Identify Input Purpose (WCAG 1.3.5)
    for field in parser.elements['inputs']:
        field_type = (field.get('type') or 'text').lower()
        if field_type not in {'text', 'email', 'tel'}:
            continue
        token = _autocomplete_token_for_field(field)
        if token and not (field.get('autocomplete') or '').strip():
            field_name = field.get('name') or field.get('id') or '(unnamed)'
            violations['autocomplete_missing'].append(
                f'Input "{field_name}" should include autocomplete="{token}" (WCAG 1.3.5)'
            )

    # Run 48: Status Messages (WCAG 4.1.3)
    for region in parser.elements['status_regions']:
        region_id = (region.get('id') or '').strip()
        if not re.search(r'(status|notification|alert|toast)', region_id, re.IGNORECASE):
            continue
        role = (region.get('role') or '').strip().lower()
        aria_live = (region.get('aria_live') or '').strip().lower()
        if aria_live or role in {'status', 'alert'}:
            continue
        violations['aria_live_missing'].append(
            f'<div id="{region_id}"> appears to be a dynamic status region without aria-live or status/alert role (WCAG 4.1.3)'
        )

    # Run 48: Animation from Interactions (WCAG 2.3.3)
    violations['prefers_reduced_motion_missing'].extend(
        _extract_prefers_reduced_motion_missing(html_content)
    )

    # Count total violations
    violations['total'] = sum(len(v) for k, v in violations.items() if k != 'total')

    return violations

def generate_baseline_for_fixture(fixture_dir):
    """Generate WCAG baseline for a fixture"""
    fixture_path = Path(fixture_dir)
    expected_html = fixture_path / 'expected-html.html'

    if not expected_html.exists():
        return None

    try:
        html_content = expected_html.read_text()
        violations = validate_wcag_aa(html_content)

        baseline = {
            'fixture': fixture_path.name,
            'html_size': len(html_content),
            'violations': violations,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
        }

        return baseline
    except Exception as e:
        print(f"Error validating {fixture_path.name}: {e}")
        return None

def main():
    brain_training = Path(__file__).parent
    fixtures_dir = brain_training / 'fixtures'

    print("WCAG 2.2 Level AA Baseline Violation Detection")
    print("=" * 60)
    print()

    results = []
    total_violations = 0

    for fixture_dir in sorted(fixtures_dir.glob('*-*')):
        if not fixture_dir.is_dir():
            continue

        print(f"[{fixture_dir.name}]", end='', flush=True)
        baseline = generate_baseline_for_fixture(fixture_dir)

        if baseline:
            violations_count = baseline['violations']['total']
            total_violations += violations_count

            # Save baseline
            baseline_file = fixture_dir / 'wcag-baseline.json'
            baseline_file.write_text(json.dumps(baseline, indent=2))

            print(f" ✓ {violations_count} violations detected")
            results.append(baseline)
        else:
            print(" ✗ Validation failed")

    print()
    print("=" * 60)
    print(f"Total Baseline Violations Across All Fixtures: {total_violations}")
    print("=" * 60)
    print()
    print("Violation Summary:")

    # Aggregate stats
    all_violations = {}
    for result in results:
        for key, value in result['violations'].items():
            if key != 'total':
                if key not in all_violations:
                    all_violations[key] = 0
                all_violations[key] += len(value) if isinstance(value, list) else value

    for violation_type, count in sorted(all_violations.items(), key=lambda x: x[1], reverse=True):
        print(f"  {violation_type}: {count}")

    # Save aggregate report
    report_file = brain_training / 'wcag-baseline-report.json'
    report = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'total_violations': total_violations,
        'fixtures_tested': len(results),
        'violation_summary': all_violations,
        'fixtures': results,
    }
    report_file.write_text(json.dumps(report, indent=2))
    print()
    print(f"Report saved: wcag-baseline-report.json")

if __name__ == '__main__':
    main()
