# Fixture 003: Scanned Image

**Purpose:** Test OCR confidence and handling of degraded input quality.

**Document Type:** Low-res scanned document (200 DPI), poor contrast, possible handwritten notes.

**Expected Complexity:** Lower target due to source quality (70%+ acceptable).

**Acceptance Criteria:**
- Extraction: ≥70% (source quality is poor)
- Healing: ≥75%
- Combined: ≥72%

**Brain should:**
- Extract best-effort text from low-quality scan
- Flag uncertain sections with [UNCLEAR: ...]
- Preserve readable content
- Note OCR confidence limitations

