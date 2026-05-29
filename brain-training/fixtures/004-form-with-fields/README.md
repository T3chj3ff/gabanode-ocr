# Fixture 004: PDF Form with Fields

**Purpose:** Test form field detection and accessibility labeling.

**Document Type:** ADA form with text fields, checkboxes, signature lines, field labels.

**Expected Complexity:** Medium (80%+ target).

**Acceptance Criteria:**
- Extraction: ≥80%
- Healing: ≥80%
- Combined: ≥80%

**Brain should:**
- Identify form fields and labels
- Preserve field structure
- Add <label> associations in healing phase
- Mark signature lines with [FORM FIELD: signature]

