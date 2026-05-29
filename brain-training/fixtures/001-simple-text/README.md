# Fixture 001: Simple Text (Baseline)

**Purpose:** Establish baseline extraction accuracy with a plain document.

**Document Type:** 2-3 page article with body text, minimal formatting, no tables or images.

**Expected Complexity:** Low (95%+ target)

**Files in this fixture:**
- `source.pdf` — Original PDF file
- `source-metadata.json` — Document metadata (page count, format, size)
- `expected-md.md` — Ground-truth Markdown extraction
- `expected-md-notes.md` — Reasoning for expected output choices
- `expected-html.html` — Target healed HTML output
- `expected-score.json` — Target accuracy scores

**Test Scenarios:**
1. Plain paragraph extraction
2. Heading hierarchy (h1, h2, h3)
3. Basic text preservation
4. No hallucination

**Acceptance Criteria:**
- Extraction: ≥95%
- Healing: ≥85%
- Combined: ≥90%

---

## Output Template

When run against prompts, each variant generates:
- `brain-output-v1-current.md` — Extracted Markdown from v1
- `brain-output-v2-improved-clarity.md` — Extracted Markdown from v2
- `brain-output-v3-step-by-step.md` — Extracted Markdown from v3
- Etc. for all variants

And healing outputs:
- `brain-output-v1-current-healed.html` — Healed HTML from v1
- Etc. for all variants

Each output gets scored against expected-md.md and expected-html.html.

