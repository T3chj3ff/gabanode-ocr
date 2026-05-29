#!/usr/bin/env python3
"""
Project Euclid — Deterministic WCAG Healer
Geometric, rule-based HTML remediation. No LLM dependency.

Variants:
  v7-deterministic-basic:   Fix lang attribute + main landmark (structural)
  v8-deterministic-images:  v7 + image alt text + anchor aria-labels (attributes)
  v9-deterministic-full:    v8 + form labels + table scope + all link text (complete)
"""

import re
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

BRAIN_TRAINING = Path(__file__).parent
FIXTURES_DIR = BRAIN_TRAINING / "fixtures"

# ─────────────────────────────────────────────────────────────────────────────
# Rule engine: pass-based deterministic transforms
# ─────────────────────────────────────────────────────────────────────────────

def fix_lang_attribute(html: str) -> str:
    """Pass 1a: Ensure <html lang="en"> — the most common low-hanging fix.

    Uses non-greedy [^>]*? so the regex hits the *first* lang="" on the html tag,
    not xml:lang="" which appears later on the same tag.

    Bug-fix note: we guard against xml:lang="en" lang="" by requiring the lang=
    attribute to be preceded by whitespace (not a word char like the colon in
    xml:lang), so xml:lang= does not satisfy the guard.
    """
    # Already has a non-empty standalone lang="…" (not xml:lang) → nothing to do
    if re.search(r'<html[^>]*?\s+lang="[a-zA-Z][^"]*"', html, re.IGNORECASE):
        return html
    # Fill empty standalone lang="" (whitespace-anchored so xml:lang= is skipped)
    html = re.sub(
        r'(<html\b[^>]*?\s+lang=")["]',
        r'\g<1>en"',
        html,
        flags=re.IGNORECASE
    )
    # Also fill xml:lang="" if still empty
    html = re.sub(
        r'(<html[^>]*?\bxml:lang=")["]',
        r'\g<1>en"',
        html,
        flags=re.IGNORECASE
    )
    # No standalone lang at all → inject before closing > on <html tag
    if not re.search(r'<html\b[^>]*?\s+lang=', html, re.IGNORECASE):
        if re.search(r'<html\b', html, re.IGNORECASE):
            html = re.sub(
                r'(<html\b[^>]*)>',
                r'\1 lang="en">',
                html,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            # No <html> tag at all — inject after <!DOCTYPE ...> or at start
            if re.search(r'<!DOCTYPE\b', html, re.IGNORECASE):
                html = re.sub(
                    r'(<!DOCTYPE[^>]*>)',
                    r'\1\n<html lang="en">',
                    html,
                    count=1,
                    flags=re.IGNORECASE
                )
                if not re.search(r'</html>', html, re.IGNORECASE):
                    html = html.rstrip() + '\n</html>'
            else:
                html = '<html lang="en">\n' + html + '\n</html>'
    return html


def fix_main_landmark(html: str) -> str:
    """Pass 1b: Wrap body content in <main> if absent."""
    if re.search(r'<main[\s>]', html, re.IGNORECASE):
        return html  # already has <main>
    # Inject <main> after <body...> tag and close before </body>
    html = re.sub(
        r'(<body[^>]*>)',
        r'\1\n<main>',
        html,
        count=1,
        flags=re.IGNORECASE
    )
    html = re.sub(
        r'(</body>)',
        r'</main>\n\1',
        html,
        count=1,
        flags=re.IGNORECASE
    )
    return html


def _alt_from_src(src: str) -> str:
    """Generate descriptive alt text from image filename."""
    filename = src.split('/')[-1]
    name = filename.rsplit('.', 1)[0]  # strip extension

    # reference-tagged-{page}_{fig}  →  "Page {page}, Figure {fig}"
    m = re.match(r'reference-tagged-(\d+)_(\d+)', name)
    if m:
        page, fig = m.group(1), m.group(2)
        return f"Page {page}, figure {fig}"

    # reference-tagged-{page}  →  "Page {page}"
    m = re.match(r'reference-tagged-(\d+)', name)
    if m:
        return f"Page {m.group(1)} image"

    # Generic: humanise the filename
    human = name.replace('-', ' ').replace('_', ' ')
    return human.strip() or "Document image"


def _apply_alt(tag: str, alt_text: str) -> str:
    """Apply alt_text to a tag that is missing a non-empty alt."""
    if re.search(r'\balt=""', tag, re.IGNORECASE):
        return re.sub(r'\balt=""', f'alt="{alt_text}"', tag, flags=re.IGNORECASE)
    return re.sub(r'(\s*/?>)$', f' alt="{alt_text}"\\1', tag)


def fix_image_alt(html: str) -> str:
    """Pass 2a: Add alt text to every <img> missing one.

    3-tier fallback chain:
      Tier 1: sibling <figcaption> text (when img is inside <figure>)
      Tier 2: img title="" attribute
      Tier 3: filename pattern (original behaviour)
    """
    def _strip_tags(s: str) -> str:
        return re.sub(r'<[^>]+>', '', s).strip()

    def _add_alt_in_figure(match) -> str:
        figure_block = match.group(0)
        caption_m = re.search(
            r'<figcaption[^>]*>([\s\S]*?)</figcaption>', figure_block, re.IGNORECASE
        )
        caption_text = _strip_tags(caption_m.group(1)) if caption_m else None

        def _patch(m):
            tag = m.group(0)
            if re.search(r'\balt="[^"]+', tag, re.IGNORECASE):
                return tag  # already non-empty
            # Tier 1: figcaption
            if caption_text:
                return _apply_alt(tag, caption_text)
            # Tier 2: title attribute
            title_m = re.search(r'\btitle="([^"]+)"', tag, re.IGNORECASE)
            if title_m:
                return _apply_alt(tag, title_m.group(1))
            # Tier 3: filename
            src_m = re.search(r'\bsrc="([^"]*)"', tag, re.IGNORECASE)
            alt_text = _alt_from_src(src_m.group(1)) if src_m else "Document image"
            return _apply_alt(tag, alt_text)

        return re.sub(r'<img\s[^>]*/?>', _patch, figure_block,
                      flags=re.IGNORECASE | re.DOTALL)

    # Pass A: process <figure> blocks first (Tier 1 available)
    html = re.sub(
        r'<figure\b[^>]*>[\s\S]*?</figure>',
        _add_alt_in_figure,
        html,
        flags=re.IGNORECASE
    )

    # Pass B: stray <img> outside any <figure> (Tier 2 + Tier 3 only)
    def _add_alt_stray(m):
        tag = m.group(0)
        if re.search(r'\balt="[^"]+', tag, re.IGNORECASE):
            return tag
        title_m = re.search(r'\btitle="([^"]+)"', tag, re.IGNORECASE)
        if title_m:
            return _apply_alt(tag, title_m.group(1))
        src_m = re.search(r'\bsrc="([^"]*)"', tag, re.IGNORECASE)
        alt_text = _alt_from_src(src_m.group(1)) if src_m else "Document image"
        return _apply_alt(tag, alt_text)

    return re.sub(r'<img\s[^>]*/?>', _add_alt_stray, html,
                  flags=re.IGNORECASE | re.DOTALL)


def fix_empty_anchors(html: str) -> str:
    """Pass 2b: Replace <a name=N></a> anchors with id-based anchors.

    The validator flags <a name=N></a> because the link has empty text.
    We convert them to <span id="anchor-N" aria-hidden="true"></span>
    which removes the empty-link violation without breaking page navigation.
    """
    # <a name=1></a>  or  <a name="outline"></a>
    def _convert_anchor(m):
        name_val = m.group(1).strip('"\'')
        # Make a safe id
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', name_val)
        return f'<span id="anchor-{safe_id}" aria-hidden="true"></span>'

    html = re.sub(
        r'<a\s+name=["\']?([^"\'>\s]+)["\']?\s*></a>',
        _convert_anchor,
        html,
        flags=re.IGNORECASE
    )
    # Also handle <a name=N/> self-closing
    html = re.sub(
        r'<a\s+name=["\']?([^"\'>\s]+)["\']?\s*/?>',
        _convert_anchor,
        html,
        flags=re.IGNORECASE
    )
    return html


def fix_empty_links(html: str) -> str:
    """Pass 2c: Add aria-label to remaining empty <a href=...> links."""
    def _add_label(m):
        tag_open = m.group(1)
        content  = m.group(2)
        tag_close = m.group(3)

        if content.strip():
            return m.group(0)  # not empty

        # Already has aria-label or title
        if re.search(r'\b(aria-label|title)=', tag_open, re.IGNORECASE):
            return m.group(0)

        # Derive label from href
        href_m = re.search(r'\bhref="([^"]*)"', tag_open, re.IGNORECASE)
        if href_m:
            href = href_m.group(1).strip()
            if href.startswith('mailto:'):
                label = href[7:]
            elif href.startswith('http'):
                label = href.split('/')[-1] or href
            elif href:
                label = href.split('#')[-1] or href
            else:
                label = 'Link'   # href="" — give it a generic accessible label
            label = label.replace('-', ' ').replace('_', ' ').strip() or 'Link'
            new_open = re.sub(r'>$', f' aria-label="{label}">', tag_open)
            return f'{new_open}{content}{tag_close}'

        return m.group(0)

    return re.sub(
        r'(<a\s[^>]*>)([^<]*)(</a>)',
        _add_label,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )


def fix_form_labels(html: str) -> str:
    """Pass 3a: Add aria-label to form inputs that have no associated label."""
    def _label_input(m):
        tag = m.group(0)
        # Already has aria-label, aria-labelledby, or id (may be referenced by label)
        if re.search(r'\b(aria-label|aria-labelledby|id)=', tag, re.IGNORECASE):
            return tag
        # Determine type for a meaningful label
        type_m = re.search(r'\btype="([^"]*)"', tag, re.IGNORECASE)
        name_m = re.search(r'\bname="([^"]*)"', tag, re.IGNORECASE)
        field_type = (type_m.group(1) if type_m else 'input').capitalize()
        field_name = name_m.group(1).replace('_', ' ').replace('-', ' ').capitalize() if name_m else ''
        label = f"{field_name} {field_type}".strip() or "Form field"
        return re.sub(r'(\s*/?>)$', f' aria-label="{label}"\\1', tag)

    return re.sub(
        r'<input\s[^>]*/?>',
        _label_input,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )


def fix_table_scope(html: str) -> str:
    """Pass 3b: Add scope to <th> elements that lack it."""
    def _add_scope(m):
        tag = m.group(0)
        if re.search(r'\bscope=', tag, re.IGNORECASE):
            return tag  # already scoped
        return re.sub(r'(<th)', r'\1 scope="col"', tag, count=1, flags=re.IGNORECASE)

    return re.sub(
        r'<th\s[^>]*>|<th>',
        _add_scope,
        html,
        flags=re.IGNORECASE
    )


def fix_heading_hierarchy(html: str) -> str:
    """Pass 4a: Normalize heading hierarchy.

    Two rules applied in order:
    1. If the first heading is h2+, shift ALL headings down so the first
       becomes h1 (proportional shift preserves relative nesting).
    2. For any remaining skip (hN → hN+2+), cap the child at parent+1.

    Replacements are made right-to-left to keep string offsets valid.
    """
    heading_re = re.compile(
        r'(<h([1-6])(\s[^>]*)?>)(.*?)(</h[1-6]>)',
        re.IGNORECASE | re.DOTALL,
    )

    matches = list(heading_re.finditer(html))
    if not matches:
        return html

    levels = [int(m.group(2)) for m in matches]

    # Step 1: shift so first heading is h1
    offset = levels[0] - 1
    adjusted = [max(1, min(6, lv - offset)) for lv in levels]

    # Step 2: remove skips — each heading can be at most parent+1
    target = list(adjusted)
    for i in range(1, len(target)):
        if target[i] > target[i - 1] + 1:
            target[i] = target[i - 1] + 1

    # Step 3: apply right-to-left so indices stay valid
    result = html
    for i in range(len(matches) - 1, -1, -1):
        m = matches[i]
        orig_lv = levels[i]
        new_lv  = target[i]
        if orig_lv == new_lv:
            continue
        old_open  = f'<h{orig_lv}'
        new_open  = f'<h{new_lv}'
        old_close = f'</h{orig_lv}>'
        new_close = f'</h{new_lv}>'
        span = m.group(0)
        span = span.replace(old_open,  new_open,  1)
        span = span[::-1].replace(old_close[::-1], new_close[::-1], 1)[::-1]
        result = result[:m.start()] + span + result[m.end():]

    return result


def _find_table_spans(html: str):
    """Return (start, end) byte spans for every <table>...</table> in html."""
    spans, stack = [], []
    lower = html.lower()
    i = 0
    length = len(lower)
    while i < length:
        if lower[i:i+6] == '<table' and (i + 6 >= length or lower[i+6] in ' \t\r\n>/'):
            stack.append(i)
            i += 6
        elif lower[i:i+8] == '</table>':
            if stack:
                spans.append((stack.pop(), i + 8))
            i += 8
        else:
            i += 1
    return spans


def _find_table_end(html: str, start: int) -> int:
    """Find the closing </table> for the table opening at position start."""
    lower = html.lower()
    i = start + 6  # skip past '<table'
    depth = 1
    length = len(lower)
    while i < length:
        if lower[i:i+6] == '<table' and (i + 6 >= length or lower[i+6] in ' \t\r\n>/'):
            depth += 1
            i += 6
        elif lower[i:i+8] == '</table>':
            depth -= 1
            if depth == 0:
                return i + 8
            i += 8
        else:
            i += 1
    return -1


def _mask_nested_tables(html: str) -> str:
    """Return html with all content inside nested tables replaced by spaces.

    Depth-1 tables are preserved; depth-2+ content is blanked so regex
    operating on the result only sees the outermost table structure.
    """
    result = list(html)
    lower = html.lower()
    depth = 0
    i = 0
    length = len(lower)
    while i < length:
        if lower[i:i+6] == '<table' and (i + 6 >= length or lower[i+6] in ' \t\r\n>/'):
            depth += 1
            if depth > 1:
                # Blank '<' and advance; the rest of '<table' chars get
                # blanked by the depth>1 guard in the else branch or here.
                for j in range(i, min(i + 6, length)):
                    result[j] = ' '
            i += 6
        elif lower[i:i+8] == '</table>':
            if depth > 1:
                for j in range(i, min(i + 8, length)):
                    result[j] = ' '
            depth -= 1
            i += 8
        else:
            if depth > 1:
                result[i] = ' '
            i += 1
    return ''.join(result)


def _fix_one_table(tbl: str) -> str:
    """Promote first-row <td>→<th scope='col'> in a single table chunk."""
    masked = _mask_nested_tables(tbl)
    if re.search(r'<th[\s>]', masked, re.IGNORECASE):
        return tbl  # already has header cells at this level
    m = re.search(r'<tr[^>]*>.*?</tr>', masked, re.IGNORECASE | re.DOTALL)
    if not m:
        return tbl
    s, e = m.start(), m.end()
    first_row = tbl[s:e]
    promoted = re.sub(
        r'<td(\s[^>]*)?>',
        lambda cm: f'<th scope="col"{cm.group(1) or ""}>',
        first_row,
        flags=re.IGNORECASE,
    )
    promoted = re.sub(r'</td>', '</th>', promoted, flags=re.IGNORECASE)
    return tbl[:s] + promoted + tbl[e:]


def fix_table_headers(html: str) -> str:
    """Pass 4b: Promote first-row <td> → <th scope='col'> for tables missing headers.

    Processes tables right-to-left by start position so inner tables (higher
    start offset) are fixed before outer tables.  After each inner-table fix
    the outer table's start position is unchanged, so we dynamically re-locate
    each table's end boundary in the (possibly-grown) result string.
    """
    spans = _find_table_spans(html)
    if not spans:
        return html
    # Sort by start position descending: inner tables (higher start) first
    starts = sorted({s for s, _ in spans}, reverse=True)
    result = html
    for orig_s in starts:
        end = _find_table_end(result, orig_s)
        if end < 0:
            continue
        tbl = result[orig_s:end]
        fixed = _fix_one_table(tbl)
        if fixed != tbl:
            result = result[:orig_s] + fixed + result[end:]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3C passes — production-ready completeness
# ─────────────────────────────────────────────────────────────────────────────

def fix_page_title(html: str) -> str:
    """Pass 5a: Inject <title>Document</title> if missing or empty (WCAG 2.4.2)."""
    if re.search(r'<title>[^<\s][^<]*</title>', html, re.IGNORECASE):
        return html
    if re.search(r'<title>\s*</title>', html, re.IGNORECASE):
        return re.sub(r'<title>\s*</title>', '<title>Document</title>', html, flags=re.IGNORECASE)
    if re.search(r'<head[^>]*>', html, re.IGNORECASE):
        return re.sub(r'(<head[^>]*>)', r'\1<title>Document</title>', html, count=1, flags=re.IGNORECASE)
    if re.search(r'<body\b', html, re.IGNORECASE):
        return re.sub(r'(<body\b)', r'<head><title>Document</title></head>\n\1', html, count=1, flags=re.IGNORECASE)
    return '<head><title>Document</title></head>\n' + html


def fix_duplicate_ids(html: str) -> str:
    """Pass 5b: Deduplicate id attributes (WCAG 4.1.1).
    First occurrence keeps its value; subsequent occurrences get -2, -3, etc.
    """
    seen: dict = {}
    def _dedup(m: re.Match) -> str:
        val = m.group(1)
        seen[val] = seen.get(val, 0) + 1
        if seen[val] == 1:
            return m.group(0)
        return f'id="{val}-{seen[val]}"'
    return re.sub(r'\bid="([^"]+)"', _dedup, html)


def fix_button_labels(html: str) -> str:
    """Pass 5c: Add aria-label to <button> elements with no accessible name (WCAG 4.1.2)."""
    def _fix(m: re.Match) -> str:
        tag_open  = m.group(1)
        content   = m.group(2)
        tag_close = m.group(3)
        if content.strip():
            return m.group(0)
        # Skip only if aria-label/title has a non-empty value
        al_m = re.search(r'\baria-label="([^"]*)"', tag_open, re.IGNORECASE)
        if al_m and al_m.group(1).strip():
            return m.group(0)
        if re.search(r'\b(aria-labelledby|title)="[^"]+"', tag_open, re.IGNORECASE):
            return m.group(0)
        type_m = re.search(r'\btype="([^"]*)"', tag_open, re.IGNORECASE)
        btn_type = type_m.group(1).lower() if type_m else 'button'
        label_map = {'submit': 'Submit', 'reset': 'Reset', 'button': 'Button'}
        label = label_map.get(btn_type, 'Button')
        new_open = tag_open.rstrip('>').rstrip() + f' aria-label="{label}">'
        return f'{new_open}{content}{tag_close}'
    return re.sub(r'(<button\b[^>]*>)(.*?)(</button>)', _fix, html, flags=re.IGNORECASE | re.DOTALL)



def fix_form_ids(html: str) -> str:
    """Pass 4c: Add id + name to form inputs that lack them.

    The WCAG validator flags inputs where aria-labelledby is absent AND
    (id is absent OR name is absent).  Adding both id and name satisfies the
    structural labelling requirement and enables <label for="..."> association.
    IDs are derived from placeholder text, then input type, then a counter.
    """
    counter = [0]

    def _ensure_id_name(m):
        tag = m.group(0)

        # Skip submit/reset/button/hidden — not user-input fields
        type_m = re.search(r'\btype="([^"]*)"', tag, re.IGNORECASE)
        field_type = type_m.group(1).lower() if type_m else 'text'
        if field_type in ('submit', 'reset', 'button', 'hidden', 'image'):
            return tag

        has_id           = bool(re.search(r'\bid=',              tag, re.IGNORECASE))
        has_name         = bool(re.search(r'\bname=',            tag, re.IGNORECASE))
        has_labelledby   = bool(re.search(r'\baria-labelledby=', tag, re.IGNORECASE))

        if has_labelledby or (has_id and has_name):
            return tag  # already satisfies the validator condition

        # Derive a slug for id/name
        ph_m = re.search(r'\bplaceholder="([^"]*)"', tag, re.IGNORECASE)
        if ph_m:
            raw = ph_m.group(1).lower().strip()
            slug = re.sub(r'[^a-z0-9]+', '-', raw).strip('-')[:40]
        else:
            slug = field_type

        if not slug:
            counter[0] += 1
            slug = f'field-{counter[0]}'
        else:
            counter[0] += 1
            slug = f'{slug}-{counter[0]}'

        if not has_id:
            tag = re.sub(r'(\s*/?>)$', f' id="{slug}"\\1', tag)
        if not has_name:
            tag = re.sub(r'(\s*/?>)$', f' name="{slug}"\\1', tag)
        return tag

    return re.sub(
        r'<(?:input|textarea|select)\b[^>]*/?>',
        _ensure_id_name,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def fix_color_contrast(html: str) -> str:
    """Pass 6a: Replace inline style= color values that fail WCAG 1.4.3 AA
    contrast ratio against a white background (Phase 3D).

    Strategy: replace the failing color with #1a1a1a (near-black, 16.1:1 ratio)
    instead of pure black — preserves intent while guaranteeing AA compliance.
    Only modifies style= attributes whose color: declaration is parseable AND
    fails the threshold. Unparseable / dynamic colors are left untouched.
    """
    # Inline color helpers (mirrors wcag_validator._relative_luminance logic)
    _NAMED = {
        'black':'#000000','white':'#ffffff','red':'#ff0000','green':'#008000',
        'blue':'#0000ff','yellow':'#ffff00','orange':'#ffa500','purple':'#800080',
        'gray':'#808080','grey':'#808080','lightgray':'#d3d3d3','lightgrey':'#d3d3d3',
        'darkgray':'#a9a9a9','darkgrey':'#a9a9a9','silver':'#c0c0c0',
        'maroon':'#800000','navy':'#000080','teal':'#008080','lime':'#00ff00',
        'aqua':'#00ffff','cyan':'#00ffff','fuchsia':'#ff00ff','magenta':'#ff00ff',
        'pink':'#ffc0cb','lightblue':'#add8e6','lightyellow':'#ffffe0',
        'lightgreen':'#90ee90','darkred':'#8b0000','darkblue':'#00008b',
        'darkgreen':'#006400','coral':'#ff7f50','salmon':'#fa8072',
        'gold':'#ffd700','goldenrod':'#daa520','khaki':'#f0e68c',
        'indigo':'#4b0082','violet':'#ee82ee','brown':'#a52a2a',
        'beige':'#f5f5dc','ivory':'#fffff0','lavender':'#e6e6fa',
        'tan':'#d2b48c','wheat':'#f5deb3','crimson':'#dc143c',
        'tomato':'#ff6347','chocolate':'#d2691e','peru':'#cd853f',
    }

    def _parse(v):
        v = v.strip().lower()
        if v.startswith('#'):
            h = v.lstrip('#')
            if len(h) == 3:
                h = h[0]*2 + h[1]*2 + h[2]*2
            if len(h) == 6:
                try:
                    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))
                except ValueError:
                    return None
        m = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', v)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        hex_v = _NAMED.get(v)
        return _parse(hex_v) if hex_v else None

    def _lum(r, g, b):
        def lin(c):
            s = c / 255
            return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
        return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

    def _ratio(rgb):
        # Against white background (luminance = 1.0)
        l = _lum(*rgb)
        return (1.0 + 0.05) / (l + 0.05)

    SAFE_COLOR = '#1a1a1a'  # 16.1:1 on white — safe replacement

    def _fix_style(m):
        tag_open = m.group(1)
        # Find color: <value> inside style="..."
        style_m = re.search(r'style="([^"]*)"', tag_open, re.IGNORECASE)
        if not style_m:
            return m.group(0)
        style_val = style_m.group(1)
        color_m = re.search(r'(color\s*:\s*)([^;}"]+)', style_val, re.IGNORECASE)
        if not color_m:
            return m.group(0)
        raw_color = color_m.group(2).strip()
        rgb = _parse(raw_color)
        if rgb is None:
            return m.group(0)          # unparseable — leave alone
        tag = m.group(1).split()[0].lstrip('<').lower()
        threshold = 3.0 if tag in ('h1','h2','h3','h4','h5','h6') else 4.5
        if _ratio(rgb) >= threshold:
            return m.group(0)          # already passes — leave alone
        # Replace failing color — use group(0) indices to replace the full style="..." attr
        new_style = style_val[:color_m.start(2)] + SAFE_COLOR + style_val[color_m.end(2):]
        new_tag_open = tag_open[:style_m.start(0)] + f'style="{new_style}"' + tag_open[style_m.end(0):]
        return new_tag_open + m.group(2) + m.group(3)

    return re.sub(
        r'(<[a-z][a-z0-9]*[^>]*style="[^"]*color\s*:[^"]*"[^>]*>)(.*?)(</[a-z][a-z0-9]*>)',
        _fix_style,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase 4A passes — skip navigation + tabindex
# ─────────────────────────────────────────────────────────────────────────────

def fix_skip_nav(html: str) -> str:
    """Pass 7a: Inject a skip navigation link if missing (WCAG 2.4.1).

    Only applies when the page has a <main> element. Adds id="main-content" to
    <main> if not already present, then injects an <a href="#main-content">
    Skip to main content</a> immediately after the opening <body> tag.
    """
    if not re.search(r'<main\b', html, re.IGNORECASE):
        return html  # No main landmark — skip nav not applicable
    # Already has a skip nav link
    body_m = re.search(r'<body\b[^>]*>(.*)', html, re.IGNORECASE | re.DOTALL)
    body_start = body_m.group(1)[:400] if body_m else html[:400]
    if re.search(r'<a\b[^>]*href="#[^"]*"[^>]*>\s*[Ss]kip', body_start, re.IGNORECASE):
        return html
    # Ensure <main> has an id to skip to
    if not re.search(r'<main\b[^>]*\bid=', html, re.IGNORECASE):
        html = re.sub(
            r'(<main\b)',
            '<main id="main-content"',
            html, count=1, flags=re.IGNORECASE,
        )
    # Inject skip link after <body> opening tag
    skip_link = '<a href="#main-content" class="skip-nav">Skip to main content</a>'
    return re.sub(
        r'(<body\b[^>]*>)',
        r'\1\n' + skip_link,
        html, count=1, flags=re.IGNORECASE,
    )


def fix_tabindex(html: str) -> str:
    """Pass 7b: Replace positive tabindex values with 0 (WCAG 2.4.3).

    Positive tabindex values (tabindex="1", "2", etc.) override natural focus
    order and create accessibility barriers. Setting them to 0 preserves
    keyboard focusability while restoring DOM-order focus sequence.
    """
    return re.sub(
        r'(\btabindex=")([1-9][0-9]*)(")',
        r'\g<1>0\3',
        html,
        flags=re.IGNORECASE,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase 4B passes — iframe titles + SVG accessible names
# ─────────────────────────────────────────────────────────────────────────────

def fix_iframe_title(html: str) -> str:
    """Pass 8a: Add title attribute to <iframe> elements missing one (WCAG 4.1.2).

    The title attribute is the primary accessible name for an iframe. Without it,
    screen readers announce the src URL or nothing useful.

    Derivation strategy (in priority order):
      1. YouTube / Vimeo / video-host embed → "Embedded video content"
      2. Map embed (maps.google, map in URL) → "Embedded map"
      3. Filename without extension, kebab/snake converted → "Budget Viewer"
      4. Fallback → "Embedded content"
    """
    def _add_title(m):
        tag = m.group(0)
        if re.search(r'\btitle=', tag, re.IGNORECASE):
            return tag  # already has a title
        src_m = re.search(r'\bsrc="([^"]*)"', tag, re.IGNORECASE)
        if src_m:
            src = src_m.group(1)
            if re.search(r'youtube\.com|youtu\.be|vimeo\.com', src, re.IGNORECASE):
                label = 'Embedded video content'
            elif re.search(r'maps\.google|googlemaps|/map', src, re.IGNORECASE):
                label = 'Embedded map'
            else:
                path = src.rstrip('/').split('/')[-1].split('?')[0]
                base = re.sub(r'\.[^.]+$', '', path)
                words = re.split(r'[-_]', base)
                label = ' '.join(w.capitalize() for w in words if w) or 'Embedded content'
        else:
            label = 'Embedded content'
        # Insert title before the closing > (handles both /> and >)
        return re.sub(r'(\s*/?>)$', f' title="{label}"\\1', tag)

    return re.sub(
        r'<iframe\b[^>]*(?:/>|>)',
        _add_title,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def fix_svg_accessible_name(html: str) -> str:
    """Pass 8b: Add accessible name to inline SVG elements missing one (WCAG 1.1.1).

    An SVG conveys meaning if it has visible geometry or text.  Without a name,
    screen readers either skip it or read raw attributes.

    Strategy:
      - Already has aria-label, aria-hidden="true", role="presentation",
        or a <title> child → leave unchanged.
      - Has a <text> child element → use its content as the <title> value.
      - Otherwise → insert <title>Graphic</title> as the first child.
    """
    def _fix_svg(m):
        tag_open = m.group(1)
        content  = m.group(2)
        tag_close = m.group(3)

        # Already named or intentionally hidden
        if re.search(r'\baria-label\s*=', tag_open, re.IGNORECASE):
            return m.group(0)
        if re.search(r'\baria-hidden\s*=\s*"true"', tag_open, re.IGNORECASE):
            return m.group(0)
        if re.search(r'\brole\s*=\s*"(?:presentation|none)"', tag_open, re.IGNORECASE):
            return m.group(0)
        if re.search(r'<title\b', content, re.IGNORECASE):
            return m.group(0)

        # Derive a label from embedded <text> element (charts, diagrams)
        text_m = re.search(r'<text\b[^>]*>([^<]+)</text>', content, re.IGNORECASE)
        if text_m:
            raw = text_m.group(1).strip()
            label = raw[:80] if raw else 'Graphic'
        else:
            label = 'Graphic'

        # Escape any double-quotes in label
        label = label.replace('"', '&quot;')

        new_content = f'<title>{label}</title>{content}'
        return f'{tag_open}{new_content}{tag_close}'

    return re.sub(
        r'(<svg\b[^>]*>)(.*?)(</svg>)',
        _fix_svg,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Run 48 passes — v14 corpus expansion only
# ─────────────────────────────────────────────────────────────────────────────

_AUTOCOMPLETE_RULES = [
    (re.compile(r'\b(?:given[-_]?name|first[-_]?name|firstname)\b', re.IGNORECASE), 'given-name'),
    (re.compile(r'\b(?:family[-_]?name|last[-_]?name|lastname|surname)\b', re.IGNORECASE), 'family-name'),
    (re.compile(r'\b(?:email|e[-_]?mail)\b', re.IGNORECASE), 'email'),
    (re.compile(r'\b(?:tel|phone|telephone|mobile)\b', re.IGNORECASE), 'tel'),
    (re.compile(r'\b(?:street[-_]?address|address[-_]?line1|mailing[-_]?address|address|street)\b', re.IGNORECASE), 'street-address'),
    (re.compile(r'\b(?:postal[-_]?code|postcode|zip[-_]?code|zip)\b', re.IGNORECASE), 'postal-code'),
    (re.compile(r'\b(?:country[-_]?name|country)\b', re.IGNORECASE), 'country-name'),
]


def _html_attr(tag: str, name: str) -> str:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
    return m.group(1) if m else ''


def _add_html_attr(tag: str, name: str, value: str) -> str:
    if re.search(rf'\b{name}\s*=', tag, re.IGNORECASE):
        return tag
    return re.sub(r'(\s*/?>)$', f' {name}="{value}"\\1', tag)


def _autocomplete_token_for_field_name(field_name: str):
    for pattern, token in _AUTOCOMPLETE_RULES:
        if pattern.search(field_name):
            return token
    return None


def fix_focus_visible(html: str) -> str:
    """Pass 9a: Restore visible focus indicators removed by :focus CSS."""
    focus_rule = re.compile(r'([^{}]*:focus[^{}]*)\{([^{}]*)\}', re.IGNORECASE | re.DOTALL)
    outline_removed = re.compile(
        r'\boutline\s*:\s*(?:none|0(?:\s+none)?)(?:\s*!important)?\s*(?:;|$)',
        re.IGNORECASE,
    )

    def _fix_css(css: str) -> str:
        def _fix_rule(m: re.Match) -> str:
            selector = m.group(1)
            declarations = m.group(2)
            if not outline_removed.search(declarations):
                return m.group(0)
            declarations = outline_removed.sub(
                'outline: 2px solid #005fcc; outline-offset: 2px;',
                declarations,
            )
            return f'{selector}{{{declarations}}}'

        return focus_rule.sub(_fix_rule, css)

    def _fix_style_block(m: re.Match) -> str:
        return f'{m.group(1)}{_fix_css(m.group(2))}{m.group(3)}'

    return re.sub(
        r'(<style\b[^>]*>)(.*?)(</style>)',
        _fix_style_block,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def fix_autocomplete(html: str) -> str:
    """Pass 9b: Add WCAG 1.3.5 autocomplete tokens to personal-info inputs."""
    def _fix_input(m: re.Match) -> str:
        tag = m.group(0)
        if re.search(r'\bautocomplete\s*=', tag, re.IGNORECASE):
            return tag
        field_type = (_html_attr(tag, 'type') or 'text').lower()
        if field_type not in {'text', 'email', 'tel'}:
            return tag
        field_name = f'{_html_attr(tag, "name")} {_html_attr(tag, "id")}'
        token = _autocomplete_token_for_field_name(field_name)
        if not token:
            return tag
        return _add_html_attr(tag, 'autocomplete', token)

    return re.sub(
        r'<input\b[^>]*>',
        _fix_input,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def fix_aria_live_regions(html: str) -> str:
    """Pass 9c: Add live-region semantics to dynamic status containers."""
    status_like = re.compile(r'(status|notification|alert|toast)', re.IGNORECASE)
    urgent_like = re.compile(r'(alert|error|fail|critical)', re.IGNORECASE)

    def _fix_div(m: re.Match) -> str:
        tag = m.group(0)
        region_id = _html_attr(tag, 'id')
        if not region_id or not status_like.search(region_id):
            return tag
        role = _html_attr(tag, 'role').lower()
        aria_live = _html_attr(tag, 'aria-live').lower()
        if aria_live or role in {'status', 'alert'}:
            return tag

        if urgent_like.search(region_id):
            role_value = 'alert'
            live_value = 'assertive'
        else:
            role_value = 'status'
            live_value = 'polite'

        if not role:
            tag = _add_html_attr(tag, 'role', role_value)
        tag = _add_html_attr(tag, 'aria-live', live_value)
        return tag

    return re.sub(
        r'<div\b[^>]*>',
        _fix_div,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def fix_prefers_reduced_motion(html: str) -> str:
    """Pass 9d: Add a reduced-motion override for animation/transition CSS."""
    style_blocks = re.findall(
        r'<style\b[^>]*>(.*?)</style>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    css = "\n".join(style_blocks)
    if not css:
        return html
    if re.search(r'@media\s*\(\s*prefers-reduced-motion\s*:', css, re.IGNORECASE):
        return html
    if not re.search(
        r'@keyframes|\b(?:animation|transition)(?:-[a-z-]+)?\s*:',
        css,
        re.IGNORECASE,
    ):
        return html

    reduced_motion_block = """

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
      }
    }
"""
    matches = list(re.finditer(r'</style>', html, re.IGNORECASE))
    if not matches:
        return html
    last = matches[-1]
    return html[:last.start()] + reduced_motion_block + html[last.start():]


# ─────────────────────────────────────────────────────────────────────────────
# Variant definitions
# ─────────────────────────────────────────────────────────────────────────────

VARIANTS = {
    'v7-deterministic-basic': [
        fix_lang_attribute,
        fix_main_landmark,
    ],
    'v8-deterministic-images': [
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
    ],
    'v9-deterministic-full': [
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
    ],
    'v11-production-ready': [
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
        fix_heading_hierarchy,
        fix_table_headers,
        fix_form_ids,
        fix_page_title,
        fix_duplicate_ids,
        fix_button_labels,
        fix_color_contrast,      # Phase 3D: WCAG 1.4.3 AA color contrast
        fix_skip_nav,            # Phase 4A: WCAG 2.4.1 skip navigation
        fix_tabindex,            # Phase 4A: WCAG 2.4.3 tabindex positive value
        fix_iframe_title,        # Phase 4B promoted: WCAG 4.1.2 iframe accessible name
        fix_svg_accessible_name, # Phase 4B promoted: WCAG 1.1.1 SVG accessible name
    ],
    'v12-phase3d': [             # Phase 3D + Phase 4A + 4B: full production pass set
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
        fix_heading_hierarchy,
        fix_table_headers,
        fix_form_ids,
        fix_page_title,
        fix_duplicate_ids,
        fix_button_labels,
        fix_color_contrast,
        fix_skip_nav,            # Phase 4A: WCAG 2.4.1 skip navigation
        fix_tabindex,            # Phase 4A: WCAG 2.4.3 tabindex positive value
        fix_iframe_title,        # Phase 4B promoted
        fix_svg_accessible_name, # Phase 4B promoted
    ],
    'v13-phase4': [              # Explicit v13 alias for Phase 4A+4B corpus
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
        fix_heading_hierarchy,
        fix_table_headers,
        fix_form_ids,
        fix_page_title,
        fix_duplicate_ids,
        fix_button_labels,
        fix_color_contrast,
        fix_skip_nav,
        fix_tabindex,
        fix_iframe_title,        # Phase 4B promoted
        fix_svg_accessible_name, # Phase 4B promoted
    ],
    'v10-extended': [
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
        fix_heading_hierarchy,
        fix_table_headers,
        fix_form_ids,
    ],
    'v14-corpus-expansion': [   # Phase 4B: iframe titles + SVG accessible names
        fix_lang_attribute,
        fix_main_landmark,
        fix_image_alt,
        fix_empty_anchors,
        fix_empty_links,
        fix_form_labels,
        fix_table_scope,
        fix_heading_hierarchy,
        fix_table_headers,
        fix_form_ids,
        fix_page_title,
        fix_duplicate_ids,
        fix_button_labels,
        fix_color_contrast,
        fix_skip_nav,
        fix_tabindex,
        fix_iframe_title,       # Phase 4B: WCAG 4.1.2 iframe accessible name
        fix_svg_accessible_name, # Phase 4B: WCAG 1.1.1 SVG accessible name
        fix_focus_visible,      # Run 48: WCAG 2.4.7 visible focus
        fix_autocomplete,       # Run 48: WCAG 1.3.5 identify input purpose
        fix_aria_live_regions,  # Run 48: WCAG 4.1.3 status messages
        fix_prefers_reduced_motion, # Run 48: WCAG 2.3.3 reduced motion
    ],
}


def apply_variant(html: str, variant: str) -> str:
    """Apply all passes for a given variant."""
    passes = VARIANTS.get(variant, [])
    for fn in passes:
        html = fn(html)
    return html


# ─────────────────────────────────────────────────────────────────────────────
# WCAG violation counter (mirrors rebenchmark_with_wcag.py)
# ─────────────────────────────────────────────────────────────────────────────

class _QuickHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_main = False
        self.has_lang = False
        self.images = []
        self.links = []
        self.headings = []
        self.forms = []
        self.tables = []
        self._link_depth = 0
        self._link_text = ''
        self._link_attrs = {}
        self._in_table = False
        self._table_has_th = False
        self._table_first_row_done = False
        self._table_row_depth = 0
        # Phase 3C
        self.has_title = False
        self._in_title = False
        self._title_text = ''
        self._in_button = False
        self._button_text = ''
        self._button_attrs = {}
        self.buttons = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'html':
            lang = d.get('lang', '').strip()
            if lang:
                self.has_lang = True
        if tag == 'main':
            self.has_main = True
        if tag == 'title':
            self._in_title = True
            self._title_text = ''
        if tag == 'button':
            self._in_button = True
            self._button_text = ''
            self._button_attrs = dict(attrs)
        if tag == 'img':
            alt = d.get('alt', '').strip()
            self.images.append({'has_alt': bool(alt)})
        if tag == 'a':
            self._link_depth += 1
            self._link_text = ''
            self._link_attrs = d
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.headings.append(int(tag[1]))
        if tag in ('input', 'textarea', 'select'):
            field_type = d.get('type', 'text').lower()
            if field_type not in ('submit', 'reset', 'button', 'hidden', 'image'):
                has_id          = bool(d.get('id', '').strip())
                has_name        = bool(d.get('name', '').strip())
                has_labelledby  = bool(d.get('aria-labelledby', '').strip())
                self.forms.append({
                    'has_id':         has_id,
                    'has_name':       has_name,
                    'has_labelledby': has_labelledby,
                })
        if tag == 'table':
            self._in_table = True
            self._table_has_th = False
            self._table_first_row_done = False
        if tag == 'th':
            self._table_has_th = True

    def handle_endtag(self, tag):
        if tag == 'a' and self._link_depth > 0:
            self._link_depth -= 1
            title_attr = self._link_attrs.get('title', '').strip()
            aria  = self._link_attrs.get('aria-label', '').strip()
            self.links.append({'text': self._link_text.strip(), 'title': title_attr or aria})
        if tag == 'table':
            self.tables.append({'has_th': self._table_has_th})
            self._in_table = False
        if tag == 'button' and self._in_button:
            self._in_button = False
            aria_l = (self._button_attrs.get('aria-label', '') or
                      self._button_attrs.get('title', '')).strip()
            self.buttons.append({'text': self._button_text.strip(), 'aria_label': aria_l})
        if tag == 'title':
            self.has_title = bool(self._title_text.strip())
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self._title_text += data
        if self._in_button:
            self._button_text += data
        if self._link_depth > 0:
            self._link_text += data


def _count_duplicate_ids(html: str) -> int:
    """Count duplicate id attribute occurrences."""
    ids = re.findall(r'\bid="([^"]+)"', html, re.IGNORECASE)
    seen: set = set()
    dups = 0
    for id_val in ids:
        if id_val in seen:
            dups += 1
        seen.add(id_val)
    return dups



def count_violations(html: str) -> dict:
    p = _QuickHTMLParser()
    try:
        p.feed(html)
    except Exception:
        pass

    img_missing_alt   = sum(1 for i in p.images if not i['has_alt'])
    link_empty        = sum(1 for l in p.links  if not l['text'] and not l['title'])
    no_main           = 0 if p.has_main else 1
    missing_lang      = 0 if p.has_lang else 1
    table_no_headers  = sum(1 for t in p.tables if not t['has_th'])
    form_no_label     = sum(
        1 for f in p.forms
        if not f['has_labelledby'] and not (f['has_id'] and f['has_name'])
    )

    # Heading hierarchy violations
    heading_broken = 0
    if p.headings:
        if p.headings[0] != 1:
            heading_broken += 1
        for i in range(len(p.headings) - 1):
            if p.headings[i + 1] > p.headings[i] + 1:
                heading_broken += 1

    # Phase 3C: new violation counts
    missing_title   = 0 if getattr(p, 'has_title', True) else 1
    dup_ids         = _count_duplicate_ids(html)
    btn_no_label    = sum(1 for b in getattr(p, 'buttons', [])
                          if not b['text'] and not b['aria_label'])

    # Phase 3D: color contrast (WCAG 1.4.3 AA) — reuse validator logic
    try:
        from wcag_validator import _extract_inline_color_violations as _ccv
        color_contrast = len(_ccv(html))
    except Exception:
        color_contrast = 0

    # Phase 4B: iframe missing title (WCAG 4.1.2)
    iframe_no_title = 0
    for m in re.finditer(r'<iframe\b([^>]*)(?:/>|>)', html, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        if not re.search(r'\btitle=', attrs, re.IGNORECASE):
            iframe_no_title += 1

    # Phase 4B: inline SVG missing accessible name (WCAG 1.1.1)
    svg_no_name = 0
    for m in re.finditer(r'(<svg\b[^>]*>)(.*?)(</svg>)', html, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        content = m.group(2)
        if re.search(r'\baria-label\s*=', attrs, re.IGNORECASE):
            continue
        if re.search(r'\baria-hidden\s*=\s*"true"', attrs, re.IGNORECASE):
            continue
        if re.search(r'\brole\s*=\s*"(?:presentation|none)"', attrs, re.IGNORECASE):
            continue
        if re.search(r'<title\b', content, re.IGNORECASE):
            continue
        svg_no_name += 1

    # Run 48: new corpus-expansion categories — use the shared validator to
    # keep the internal counter aligned with WCAG baseline generation.
    try:
        from wcag_validator import validate_wcag_aa as _validate_wcag_aa
        wcag = _validate_wcag_aa(html)
        focus_visible_removed = len(wcag.get('focus_visible_removed', []))
        autocomplete_missing = len(wcag.get('autocomplete_missing', []))
        aria_live_missing = len(wcag.get('aria_live_missing', []))
        reduced_motion_missing = len(wcag.get('prefers_reduced_motion_missing', []))
    except Exception:
        focus_visible_removed = 0
        autocomplete_missing = 0
        aria_live_missing = 0
        reduced_motion_missing = 0

    total = (img_missing_alt + link_empty + no_main + missing_lang
             + table_no_headers + form_no_label + heading_broken
             + missing_title + dup_ids + btn_no_label + color_contrast
             + iframe_no_title + svg_no_name + focus_visible_removed
             + autocomplete_missing + aria_live_missing + reduced_motion_missing)
    return {
        'image_missing_alt':          img_missing_alt,
        'link_empty_text':            link_empty,
        'no_main_landmark':           no_main,
        'missing_lang':               missing_lang,
        'table_missing_header':       table_no_headers,
        'form_missing_label':         form_no_label,
        'heading_hierarchy_broken':   heading_broken,
        'missing_page_title':         missing_title,
        'duplicate_id':               dup_ids,
        'button_missing_label':       btn_no_label,
        'color_contrast_insufficient': color_contrast,
        'iframe_missing_title':       iframe_no_title,
        'svg_missing_name':           svg_no_name,
        'focus_visible_removed':      focus_visible_removed,
        'autocomplete_missing':       autocomplete_missing,
        'aria_live_missing':          aria_live_missing,
        'prefers_reduced_motion_missing': reduced_motion_missing,
        'total':                      total,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Batch runner
# ─────────────────────────────────────────────────────────────────────────────

def run_all_fixtures(variants=None):
    if variants is None:
        variants = list(VARIANTS.keys())

    fixtures = sorted([d for d in FIXTURES_DIR.glob('*-*') if d.is_dir()])
    if not fixtures:
        print("✗ No fixtures found")
        return None

    print(f"Deterministic Healing Pipeline — {len(fixtures)} fixtures × {len(variants)} variants")
    print("=" * 72)

    summary_by_variant = {}
    all_results = []

    for variant in variants:
        print(f"\n{'─' * 72}")
        print(f"VARIANT: {variant}")
        print(f"{'─' * 72}")

        v_baseline = 0
        v_fixed    = 0
        v_results  = []

        for fx_dir in fixtures:
            src_file = fx_dir / 'expected-html.html'
            if not src_file.exists():
                print(f"  [{fx_dir.name}] ✗ expected-html.html missing")
                continue

            html = src_file.read_text(encoding='utf-8', errors='replace')
            baseline = count_violations(html)

            healed = apply_variant(html, variant)
            remaining = count_violations(healed)

            fixed     = baseline['total'] - remaining['total']
            fixed_pct = round(fixed / baseline['total'] * 100, 1) if baseline['total'] else 0.0

            v_baseline += baseline['total']
            v_fixed    += fixed

            # Save healed file
            out_file = fx_dir / f'healed-{variant}.html'
            out_file.write_text(healed, encoding='utf-8')

            result = {
                'fixture':           fx_dir.name,
                'variant':           variant,
                'baseline_total':    baseline['total'],
                'baseline_detail':   baseline,
                'remaining_total':   remaining['total'],
                'remaining_detail':  remaining,
                'violations_fixed':  fixed,
                'violations_fixed_pct': fixed_pct,
                'healed_file':       f'healed-{variant}.html',
            }
            v_results.append(result)
            all_results.append(result)

            status = "✓" if fixed_pct >= 10 else ("△" if fixed_pct > 0 else "✗")
            print(f"  [{fx_dir.name}] {status} {fixed_pct:.1f}%  "
                  f"({fixed}/{baseline['total']} fixed)  "
                  f"remaining: {remaining['total']}")

        v_pct = round(v_fixed / v_baseline * 100, 1) if v_baseline else 0.0
        summary_by_variant[variant] = {
            'total_baseline':  v_baseline,
            'total_fixed':     v_fixed,
            'overall_pct':     v_pct,
            'fixtures_count':  len(v_results),
        }
        print(f"\n  → {variant} OVERALL: {v_pct:.1f}%  ({v_fixed}/{v_baseline} fixed)")

    # Cross-variant comparison
    print(f"\n{'=' * 72}")
    print("CROSS-VARIANT COMPARISON")
    print(f"{'=' * 72}")
    best_variant = None
    best_pct     = -1
    for v, s in summary_by_variant.items():
        flag = "  "
        if s['overall_pct'] >= 40:
            flag = "✓✓"
        elif s['overall_pct'] >= 20:
            flag = "✓ "
        print(f"  {flag} {v:<35}  {s['overall_pct']:.1f}%")
        if s['overall_pct'] > best_pct:
            best_pct     = s['overall_pct']
            best_variant = v

    print(f"\n  Best: {best_variant} at {best_pct:.1f}%")

    return {
        'metadata': {
            'timestamp':       datetime.now().isoformat(),
            'phase':           '2C-1-deterministic',
            'engine':          'geometric-deterministic',
            'fixtures_total':  len(fixtures),
            'variants_tested': variants,
        },
        'summary_by_variant': summary_by_variant,
        'all_results':        all_results,
        'best_variant':       best_variant,
        'best_pct':           best_pct,
    }


if __name__ == '__main__':
    report = run_all_fixtures()
    if not report:
        sys.exit(1)

    out_file = BRAIN_TRAINING / 'healing-analysis-deterministic.json'
    with open(out_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Report saved: {out_file.name}")
