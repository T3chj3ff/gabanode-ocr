# Fixture 009: Edge Cases

**Purpose:** Test handling of WCAG violations and unusual document structures.

**Document Type:** Document with deliberate accessibility issues: missing h1, duplicate IDs, no lang attribute, skip-level headings, images without alt, inaccessible forms.

**Expected Complexity:** High (75%+ target acceptable given broken source).

**Acceptance Criteria:**
- Extraction: ≥75% (source has violations)
- Healing: ≥80% (tests healing capability)
- Combined: ≥77%

**Test Scenarios:**
1. Document with no h1 (should add in healing)
2. Heading skip (h1 → h4)
3. Missing language tag
4. Duplicate element IDs
5. Images without alt text
6. Form fields without labels
7. Color-only indicators

**Brain should:**
- Extract content despite violations
- Flag issues in healing phase
- Add missing semantic elements
- Improve accessibility score from baseline

