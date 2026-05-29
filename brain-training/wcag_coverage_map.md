# WCAG 2.2 AA Coverage Map — Project Euclid
**Generated:** 2026-05-25
**Engine:** v11-production-ready

## Summary
| Status | Count |
|--------|-------|
| ✅ Covered | 9 |
| ⚠️ Partial | 6 |
| ❌ Not Covered | 16 |
| — Not Applicable (static docs) | 20 |

## Full Criteria Map

| SC | Name | Level | Engine Pass | Status |
|----|------|-------|-------------|--------|
| 1.1.1 | Non-text Content | A | `fix_image_alt` | ✅ COVERED |
| 1.2.1 | Audio-only / Video-only | A | — | ❌ NOT_COVERED — requires content knowledge |
| 1.2.2 | Captions (Prerecorded) | A | — | ❌ NOT_COVERED — requires media analysis |
| 1.2.3 | Audio Description / Media Alt | A | — | ❌ NOT_COVERED |
| 1.2.4 | Captions (Live) | AA | — | — NOT_APPLICABLE — static docs |
| 1.2.5 | Audio Description (Prerecorded) | AA | — | ❌ NOT_COVERED |
| 1.3.1 | Info and Relationships | A | `fix_main_landmark, fix_table_headers, fix_form_labels, fix_form_ids` | ✅ COVERED — landmark, table, form structure |
| 1.3.2 | Meaningful Sequence | A | — | ⚠️ PARTIAL — heading hierarchy fixed; reading order requires layout analysis |
| 1.3.3 | Sensory Characteristics | A | — | ❌ NOT_COVERED — requires semantic understanding |
| 1.3.4 | Orientation | AA | — | — NOT_APPLICABLE — static HTML |
| 1.3.5 | Identify Input Purpose | AA | `fix_form_ids` | ⚠️ PARTIAL — id/name added; autocomplete attribute not set |
| 1.4.1 | Use of Color | A | — | ❌ NOT_COVERED — requires CSS analysis |
| 1.4.2 | Audio Control | A | — | — NOT_APPLICABLE — static docs |
| 1.4.3 | Contrast (Minimum) | AA | — | ❌ NOT_COVERED — requires computed style analysis |
| 1.4.4 | Resize Text | AA | — | — NOT_APPLICABLE — static HTML |
| 1.4.5 | Images of Text | AA | — | ❌ NOT_COVERED — requires OCR/visual analysis |
| 1.4.10 | Reflow | AA | — | — NOT_APPLICABLE — static HTML |
| 1.4.11 | Non-text Contrast | AA | — | ❌ NOT_COVERED — requires CSS analysis |
| 1.4.12 | Text Spacing | AA | — | — NOT_APPLICABLE — static HTML |
| 1.4.13 | Content on Hover or Focus | AA | — | — NOT_APPLICABLE — static HTML |
| 2.1.1 | Keyboard | A | — | ⚠️ PARTIAL — no interactive elements added; existing elements not broken |
| 2.1.2 | No Keyboard Trap | A | — | ❌ NOT_COVERED |
| 2.1.4 | Character Key Shortcuts | AA | — | — NOT_APPLICABLE |
| 2.2.1 | Timing Adjustable | A | — | — NOT_APPLICABLE — static docs |
| 2.2.2 | Pause, Stop, Hide | A | — | — NOT_APPLICABLE — static docs |
| 2.3.1 | Three Flashes | A | — | — NOT_APPLICABLE — static docs |
| 2.4.1 | Bypass Blocks | A | `fix_main_landmark` | ⚠️ PARTIAL — <main> added; skip nav link not injected |
| 2.4.2 | Page Titled | A | `fix_page_title` | ✅ COVERED |
| 2.4.3 | Focus Order | A | — | ❌ NOT_COVERED — requires DOM order analysis |
| 2.4.4 | Link Purpose (In Context) | A | `fix_empty_links` | ✅ COVERED |
| 2.4.5 | Multiple Ways | AA | — | — NOT_APPLICABLE — single-page docs |
| 2.4.6 | Headings and Labels | AA | `fix_heading_hierarchy` | ✅ COVERED — hierarchy fixed |
| 2.4.7 | Focus Visible | AA | — | ❌ NOT_COVERED — requires CSS |
| 2.4.11 | Focus Not Obscured (Min) | AA | — | — NOT_APPLICABLE |
| 2.5.3 | Label in Name | A | `fix_button_labels` | ⚠️ PARTIAL — aria-label matches visible text where applicable |
| 2.5.4 | Motion Actuation | A | — | — NOT_APPLICABLE |
| 2.5.7 | Dragging Movements | AA | — | — NOT_APPLICABLE |
| 2.5.8 | Target Size (Minimum) | AA | — | ❌ NOT_COVERED — requires CSS |
| 3.1.1 | Language of Page | A | `fix_lang_attribute` | ✅ COVERED |
| 3.1.2 | Language of Parts | AA | — | ❌ NOT_COVERED — requires semantic analysis |
| 3.2.1 | On Focus | A | — | — NOT_APPLICABLE — static docs |
| 3.2.2 | On Input | A | — | — NOT_APPLICABLE — static docs |
| 3.2.3 | Consistent Navigation | AA | — | — NOT_APPLICABLE — single-page docs |
| 3.2.4 | Consistent Identification | AA | — | ⚠️ PARTIAL — duplicate_id fix prevents conflicting names |
| 3.3.1 | Error Identification | A | — | ❌ NOT_COVERED — requires dynamic validation |
| 3.3.2 | Labels or Instructions | A | `fix_form_labels, fix_form_ids` | ✅ COVERED |
| 3.3.3 | Error Suggestion | AA | — | ❌ NOT_COVERED — requires dynamic validation |
| 3.3.4 | Error Prevention | AA | — | — NOT_APPLICABLE — static docs |
| 4.1.1 | Parsing | A | `fix_duplicate_ids` | ✅ COVERED — duplicate IDs deduplicated |
| 4.1.2 | Name, Role, Value | A | `fix_button_labels, fix_form_labels` | ✅ COVERED — buttons and inputs labeled |
| 4.1.3 | Status Messages | AA | — | — NOT_APPLICABLE — static docs |

## Priority Gaps (NOT_COVERED, applicable to PDF-to-HTML)

1. **1.4.3 Contrast** — Inline `color:` / `background-color:` in PDF-to-HTML often fails 4.5:1 ratio. Requires computed style parsing.
2. **1.3.2 Meaningful Sequence** — Reading order issues in multi-column PDF layouts. Requires layout geometry analysis.
3. **3.1.2 Language of Parts** — Foreign-language passages lack `lang` attribute. Requires language detection (LLM or langdetect).
4. **2.4.3 Focus Order** — Tab order follows DOM order; PDF-to-HTML often reorders elements. Requires layout-aware reordering.

## Next Phase Recommendation
Phase 3D: Color contrast analysis — parse inline `style=` attributes, check contrast ratios, inject CSS overrides for failing elements.