#!/usr/bin/env python3
"""Hour 4: Map engine coverage against full WCAG 2.2 AA criteria, generate gap report."""
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent

WCAG_22_AA = [
    # 1.1 Text Alternatives
    ('1.1.1', 'Non-text Content',            'A',  'fix_image_alt',        'COVERED'),
    # 1.2 Time-based Media
    ('1.2.1', 'Audio-only / Video-only',     'A',  None,                   'NOT_COVERED — requires content knowledge'),
    ('1.2.2', 'Captions (Prerecorded)',       'A',  None,                   'NOT_COVERED — requires media analysis'),
    ('1.2.3', 'Audio Description / Media Alt','A',  None,                   'NOT_COVERED'),
    ('1.2.4', 'Captions (Live)',              'AA', None,                   'NOT_APPLICABLE — static docs'),
    ('1.2.5', 'Audio Description (Prerecorded)','AA',None,                  'NOT_COVERED'),
    # 1.3 Adaptable
    ('1.3.1', 'Info and Relationships',       'A',  'fix_main_landmark, fix_table_headers, fix_form_labels, fix_form_ids', 'COVERED — landmark, table, form structure'),
    ('1.3.2', 'Meaningful Sequence',          'A',  None,                   'PARTIAL — heading hierarchy fixed; reading order requires layout analysis'),
    ('1.3.3', 'Sensory Characteristics',      'A',  None,                   'NOT_COVERED — requires semantic understanding'),
    ('1.3.4', 'Orientation',                  'AA', None,                   'NOT_APPLICABLE — static HTML'),
    ('1.3.5', 'Identify Input Purpose',       'AA', 'fix_form_ids',        'PARTIAL — id/name added; autocomplete attribute not set'),
    # 1.4 Distinguishable
    ('1.4.1', 'Use of Color',                 'A',  None,                   'NOT_COVERED — requires CSS analysis'),
    ('1.4.2', 'Audio Control',                'A',  None,                   'NOT_APPLICABLE — static docs'),
    ('1.4.3', 'Contrast (Minimum)',           'AA', None,                   'NOT_COVERED — requires computed style analysis'),
    ('1.4.4', 'Resize Text',                  'AA', None,                   'NOT_APPLICABLE — static HTML'),
    ('1.4.5', 'Images of Text',               'AA', None,                   'NOT_COVERED — requires OCR/visual analysis'),
    ('1.4.10','Reflow',                        'AA', None,                   'NOT_APPLICABLE — static HTML'),
    ('1.4.11','Non-text Contrast',            'AA', None,                   'NOT_COVERED — requires CSS analysis'),
    ('1.4.12','Text Spacing',                  'AA', None,                   'NOT_APPLICABLE — static HTML'),
    ('1.4.13','Content on Hover or Focus',    'AA', None,                   'NOT_APPLICABLE — static HTML'),
    # 2.1 Keyboard
    ('2.1.1', 'Keyboard',                     'A',  None,                   'PARTIAL — no interactive elements added; existing elements not broken'),
    ('2.1.2', 'No Keyboard Trap',             'A',  None,                   'NOT_COVERED'),
    ('2.1.4', 'Character Key Shortcuts',      'AA', None,                   'NOT_APPLICABLE'),
    # 2.2 Enough Time
    ('2.2.1', 'Timing Adjustable',            'A',  None,                   'NOT_APPLICABLE — static docs'),
    ('2.2.2', 'Pause, Stop, Hide',            'A',  None,                   'NOT_APPLICABLE — static docs'),
    # 2.3 Seizures
    ('2.3.1', 'Three Flashes',                'A',  None,                   'NOT_APPLICABLE — static docs'),
    # 2.4 Navigable
    ('2.4.1', 'Bypass Blocks',                'A',  'fix_main_landmark',   'PARTIAL — <main> added; skip nav link not injected'),
    ('2.4.2', 'Page Titled',                  'A',  'fix_page_title',      'COVERED'),
    ('2.4.3', 'Focus Order',                  'A',  None,                   'NOT_COVERED — requires DOM order analysis'),
    ('2.4.4', 'Link Purpose (In Context)',    'A',  'fix_empty_links',     'COVERED'),
    ('2.4.5', 'Multiple Ways',                'AA', None,                   'NOT_APPLICABLE — single-page docs'),
    ('2.4.6', 'Headings and Labels',          'AA', 'fix_heading_hierarchy','COVERED — hierarchy fixed'),
    ('2.4.7', 'Focus Visible',                'AA', None,                   'NOT_COVERED — requires CSS'),
    ('2.4.11','Focus Not Obscured (Min)',      'AA', None,                   'NOT_APPLICABLE'),
    # 2.5 Input Modalities
    ('2.5.3', 'Label in Name',                'A',  'fix_button_labels',   'PARTIAL — aria-label matches visible text where applicable'),
    ('2.5.4', 'Motion Actuation',             'A',  None,                   'NOT_APPLICABLE'),
    ('2.5.7', 'Dragging Movements',           'AA', None,                   'NOT_APPLICABLE'),
    ('2.5.8', 'Target Size (Minimum)',        'AA', None,                   'NOT_COVERED — requires CSS'),
    # 3.1 Readable
    ('3.1.1', 'Language of Page',             'A',  'fix_lang_attribute',  'COVERED'),
    ('3.1.2', 'Language of Parts',            'AA', None,                   'NOT_COVERED — requires semantic analysis'),
    # 3.2 Predictable
    ('3.2.1', 'On Focus',                     'A',  None,                   'NOT_APPLICABLE — static docs'),
    ('3.2.2', 'On Input',                     'A',  None,                   'NOT_APPLICABLE — static docs'),
    ('3.2.3', 'Consistent Navigation',        'AA', None,                   'NOT_APPLICABLE — single-page docs'),
    ('3.2.4', 'Consistent Identification',    'AA', None,                   'PARTIAL — duplicate_id fix prevents conflicting names'),
    # 3.3 Input Assistance
    ('3.3.1', 'Error Identification',         'A',  None,                   'NOT_COVERED — requires dynamic validation'),
    ('3.3.2', 'Labels or Instructions',       'A',  'fix_form_labels, fix_form_ids', 'COVERED'),
    ('3.3.3', 'Error Suggestion',             'AA', None,                   'NOT_COVERED — requires dynamic validation'),
    ('3.3.4', 'Error Prevention',             'AA', None,                   'NOT_APPLICABLE — static docs'),
    # 4.1 Compatible
    ('4.1.1', 'Parsing',                      'A',  'fix_duplicate_ids',   'COVERED — duplicate IDs deduplicated'),
    ('4.1.2', 'Name, Role, Value',            'A',  'fix_button_labels, fix_form_labels', 'COVERED — buttons and inputs labeled'),
    ('4.1.3', 'Status Messages',              'AA', None,                   'NOT_APPLICABLE — static docs'),
]

covered = [r for r in WCAG_22_AA if r[4].startswith('COVERED')]
partial  = [r for r in WCAG_22_AA if r[4].startswith('PARTIAL')]
not_cov  = [r for r in WCAG_22_AA if r[4].startswith('NOT_COVERED')]
not_app  = [r for r in WCAG_22_AA if r[4].startswith('NOT_APPLICABLE')]

lines = [
    f'# WCAG 2.2 AA Coverage Map — Project Euclid',
    f'**Generated:** {datetime.now().strftime("%Y-%m-%d")}',
    f'**Engine:** v11-production-ready',
    f'',
    f'## Summary',
    f'| Status | Count |',
    f'|--------|-------|',
    f'| ✅ Covered | {len(covered)} |',
    f'| ⚠️ Partial | {len(partial)} |',
    f'| ❌ Not Covered | {len(not_cov)} |',
    f'| — Not Applicable (static docs) | {len(not_app)} |',
    f'',
    f'## Full Criteria Map',
    f'',
    f'| SC | Name | Level | Engine Pass | Status |',
    f'|----|------|-------|-------------|--------|',
]
for sc, name, lvl, fn, status in WCAG_22_AA:
    icon = '✅' if status.startswith('COVERED') else ('⚠️' if status.startswith('PARTIAL') else ('—' if status.startswith('NOT_APPLICABLE') else '❌'))
    fn_str = f'`{fn}`' if fn else '—'
    lines.append(f'| {sc} | {name} | {lvl} | {fn_str} | {icon} {status} |')

lines += [
    '', '## Priority Gaps (NOT_COVERED, applicable to PDF-to-HTML)',
    '',
    '1. **1.4.3 Contrast** — Inline `color:` / `background-color:` in PDF-to-HTML often fails 4.5:1 ratio. Requires computed style parsing.',
    '2. **1.3.2 Meaningful Sequence** — Reading order issues in multi-column PDF layouts. Requires layout geometry analysis.',
    '3. **3.1.2 Language of Parts** — Foreign-language passages lack `lang` attribute. Requires language detection (LLM or langdetect).',
    '4. **2.4.3 Focus Order** — Tab order follows DOM order; PDF-to-HTML often reorders elements. Requires layout-aware reordering.',
    '',
    '## Next Phase Recommendation',
    'Phase 3D: Color contrast analysis — parse inline `style=` attributes, check contrast ratios, inject CSS overrides for failing elements.',
]

out = ROOT / 'wcag_coverage_map.md'
out.write_text('\n'.join(lines))
print(f"WCAG 2.2 AA Coverage Map written: {out.name}")
print(f"  Covered:    {len(covered)}")
print(f"  Partial:    {len(partial)}")
print(f"  Not covered:{len(not_cov)}")
print(f"  N/A:        {len(not_app)}")
print(f"\nTop gap for Phase 3D: 1.4.3 Color Contrast (1.4.3)")
