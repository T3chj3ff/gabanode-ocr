# Benchmark Scoring Rubric

**Objective:** Quantify extraction and healing accuracy across 9 test fixtures using deterministic criteria.

---

## Extraction Accuracy (Maximum 100 points)

Measures how well Gemini extracts text, structure, and semantics from PDF/images into Markdown.

### 1. Heading Hierarchy (10 points)
**Criteria:** Correct h1 → h6 structure with no gaps or misordering.

| Score | Condition |
|-------|-----------|
| 10 | Perfect hierarchy: one h1, proper nesting, no gaps |
| 8 | Minor issues: missing one level, but recoverable |
| 5 | Multiple gaps or incorrect nesting |
| 0 | Headings are flat or inverted |

**Test:** Parse Markdown, verify `#`, `##`, `###` sequence matches expected structure.

---

### 2. Table Fidelity (15 points)
**Criteria:** Tables preserve data accurately, including headers, merged cells (where possible in Markdown), and alignment.

| Score | Condition |
|-------|-----------|
| 15 | All cells present, headers marked, data accurate |
| 12 | One row/column missing or misaligned |
| 8 | Multiple cells incorrect, but table structure preserved |
| 4 | Table present but significant data loss |
| 0 | Table missing or unreadable |

**Test:** Compare extracted table cell-by-cell against expected; calculate accuracy % = (correct cells / total cells) * 15.

---

### 3. Image Descriptions (10 points)
**Criteria:** All images marked with `[IMAGE: description]` or proper alt text.

| Score | Condition |
|-------|-----------|
| 10 | All images have meaningful descriptions |
| 7 | 80%+ of images described; some generic |
| 4 | <50% of images described; weak descriptions |
| 0 | No image markers or descriptions |

**Test:** Count `[IMAGE:` markers; verify descriptions are >5 words and meaningful.

---

### 4. List Preservation (8 points)
**Criteria:** Ordered/unordered lists maintain structure, indentation, and item order.

| Score | Condition |
|-------|-----------|
| 8 | All lists correct, nesting preserved, order correct |
| 6 | One list malformed or missing item |
| 3 | Multiple lists broken, some items out of order |
| 0 | Lists converted to plain text or missing |

**Test:** Parse list markers (`-`, `1.`); validate nesting via indentation; compare item count and order.

---

### 5. Content Completeness (12 points)
**Criteria:** No missing text blocks, sentences, or paragraphs.

| Score | Condition |
|-------|-----------|
| 12 | 100% of text extracted |
| 10 | 95%+ extracted; <1 paragraph missing |
| 7 | 85%+ extracted; 1-2 paragraphs missing |
| 3 | 70%+ extracted; significant content loss |
| 0 | <50% extracted; major sections missing |

**Test:** Line-by-line diff between extracted text and expected text; calculate % complete.

---

### 6. No Hallucination (20 points)
**Criteria:** No invented content, numbers, or figures not in original document.

| Score | Condition |
|-------|-----------|
| 20 | Zero hallucinated content |
| 15 | One hallucinated sentence or figure |
| 10 | 2-3 hallucinated items |
| 5 | 4+ hallucinated items |
| 0 | Significant fabrication (>10% of content) |

**Test:** Scan for plausible-sounding but unverifiable claims; compare against expected document metadata.

---

### 7. Markdown Validity (15 points)
**Criteria:** Output is syntactically valid Markdown; proper escaping; no code-block wrapping.

| Score | Condition |
|-------|-----------|
| 15 | Valid Markdown; no extra backticks |
| 12 | Valid; minor escaping issues |
| 8 | Parseable but some broken syntax |
| 3 | Multiple syntax errors; partially parseable |
| 0 | Invalid Markdown; does not parse |

**Test:** Run through Markdown parser; check for triple-backtick wrapping (should be absent).

---

### 8. WCAG 2.2 Level AA Compliance (10 points)
**Criteria:** Output uses semantic HTML elements (when converted); proper heading hierarchy; alt text; list structure.

| Score | Condition |
|-------|-----------|
| 10 | Compliant on all counts |
| 8 | Minor semantic issues (e.g., missing h1 mention) |
| 5 | Multiple accessibility gaps |
| 0 | Not accessible |

**Test:** Convert Markdown to HTML via `markdownToHtml()`; run axe-core or manual WCAG check.

---

## Extraction Accuracy Summary

```
TOTAL_EXTRACTION = Heading(10) + Table(15) + Images(10) + Lists(8) + 
                   Completeness(12) + Hallucination(20) + Markdown(15) + WCAG(10)
= /100 points
```

---

## HTML Healing Accuracy (Maximum 100 points)

Measures how well the healing phase fixes detected violations without breaking content.

### 1. Violations Fixed (20 points)
**Criteria:** Percentage of detected violations that are actually resolved.

| Score | Condition |
|-------|-----------|
| 20 | 100% of violations fixed |
| 18 | 95%+ fixed |
| 15 | 85%+ fixed |
| 10 | 70%+ fixed |
| 5 | 50%+ fixed |
| 0 | <50% fixed |

**Formula:** (violations_resolved / violations_detected) * 20

---

### 2. False Positives Penalty (-15 points max)
**Criteria:** Healing should not introduce new violations.

| Score | Condition |
|-------|-----------|
| 0 | No new violations introduced |
| -5 | 1-2 new violations created |
| -10 | 3-5 new violations created |
| -15 | 6+ new violations created |

---

### 3. Content Preservation (30 points)
**Criteria:** Text content remains unchanged; only HTML attributes/structure modified.

| Score | Condition |
|-------|-----------|
| 30 | Text identical to pre-healing version |
| 25 | Minor whitespace changes only |
| 20 | <1% text changed (typo fixes acceptable) |
| 10 | 1-5% text altered |
| 0 | Content significantly rewritten |

**Test:** Diff extracted text before/after healing; calculate % changes.

---

### 4. Performance: Heal Time (10 points)
**Criteria:** Healing completes in acceptable time (target <20s avg).

| Score | Condition |
|-------|-----------|
| 10 | <15s |
| 8 | 15-20s |
| 5 | 20-30s |
| 2 | 30-45s |
| 0 | >45s (approaching 60s timeout) |

---

## Healing Accuracy Summary

```
TOTAL_HEALING = ViolationsFixed(20) + FalsePositives(-15) + 
                ContentPreservation(30) + Performance(10)
= /100 points (can be negative if too many false positives)
```

---

## Combined Score

```
COMBINED_SCORE = (EXTRACTION + HEALING) / 2
= /100 (average of extraction and healing accuracy)
```

---

## Example Scoring

### Fixture 002: Complex Table

**Extraction Scoring:**
- Heading hierarchy: 10/10 (correct structure)
- Table fidelity: 12/15 (one cell misaligned)
- Image descriptions: 10/10 (no images)
- List preservation: 8/8 (no lists)
- Content completeness: 12/12 (100% extracted)
- No hallucination: 20/20 (clean)
- Markdown validity: 15/15 (perfect)
- WCAG compliance: 9/10 (minor semantic note)
- **EXTRACTION TOTAL: 96/100**

**Healing Scoring:**
- Violations fixed: 18/20 (9/10 violations fixed)
- False positives: 0/-15 (no new violations)
- Content preservation: 30/30 (text unchanged)
- Performance: 8/10 (18 seconds)
- **HEALING TOTAL: 56/100**

**COMBINED SCORE: (96 + 56) / 2 = 76%** ✓ Meets 75%+ target for complex tables

---

## Threshold Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 90%+ | Excellent | Ship to production |
| 80-89% | Good | Minor improvements needed |
| 70-79% | Acceptable | Note limitations in fixture |
| <70% | Poor | Investigate prompt/detection issues |

---

## Running Baseline Benchmarks

```bash
# Score a single fixture
node run-benchmark.js --fixture=001-simple-text --prompt=v1-current

# Score all fixtures with current prompt
node run-benchmark.js --fixtures=all --prompt=v1-current

# Output: results/baseline-v1-current-2026-05-13.json
```

See `run-benchmark.js` for implementation details.

