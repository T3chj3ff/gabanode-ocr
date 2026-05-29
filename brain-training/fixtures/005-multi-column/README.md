# Fixture 005: Multi-Column Layout

**Purpose:** Test extraction of multi-column text layouts (newspaper-style).

**Document Type:** 2-3 column layout with flowing text across columns.

**Expected Complexity:** Medium (80%+ target).

**Acceptance Criteria:**
- Extraction: ≥80%
- Healing: ≥80%
- Combined: ≥80%

**Brain should:**
- Recognize multi-column structure
- Extract text in reading order (top-to-bottom per column, then next column)
- Preserve section boundaries
- Note column structure in output

