# Phase 2C: Real WCAG Validation & Healing Pipeline

**Date:** 2026-05-13  
**Status:** Ready for execution  
**Blocker Resolution:** Completed

---

## CRITICAL FINDING: Baseline Established

### WCAG 2.2 Level AA Violation Baseline
- **Total baseline violations across all 9 fixtures: 346**
- **Most common violations:**
  - Missing alt text on images: 195 (56%)
  - Empty link text: 133 (38%)
  - Missing `<main>` landmark: 9 (3%)
  - Missing `lang` attribute: 9 (3%)

### Per-Fixture Baseline Violations
```
001-simple-text:       5 violations
002-complex-table:     5 violations
003-scanned-image:     94 violations ← Most image-heavy
004-form-with-fields:  3 violations
005-multi-column:      7 violations
006-images-with-captions: 12 violations
007-nested-lists:      56 violations
008-mixed-content:     139 violations ← Most violations, most complex
009-edge-cases:        25 violations
```

---

## What the Benchmark WAS (Heuristic Scoring)
```
PDF → Extract to HTML → Apply Healing (?)
                       ↓ Heuristic Score
                    49% "healing" (fake)
```

**Problem:** Benchmark doesn't actually heal. It just scores structure changes, ARIA additions, and text preservation—not real violation fixes.

---

## What Healing NEEDS to Be (Real Validation)

```
PDF → Extract HTML (done) → Apply Prompt Variant → Run WCAG Validator
                                   ↓ v1-current
                                   ↓ v6-healing-focused
                         Report: violations_fixed_pct = 
                         (baseline - remaining) / baseline * 100
```

---

## Execution Plan: Real Healing + Validation

### Phase 2C-1: Healing Pipeline Setup (2 hours)

**Goal:** Create a healing pipeline that takes expected-html.html and produces healed output

**Steps:**
1. Create `heal_fixture.py` that:
   - Takes fixture HTML (expected-html.html)
   - Runs through v1-current healing prompt via Gemini API
   - Saves healed output: `healed-v1-current.html`
   - Records violations before/after
   - Logs healing metrics

2. Create `heal_all_fixtures.py` that:
   - Batch processes all 9 fixtures
   - Runs both v1-current and v6-healing-focused
   - Generates `healed-v1-current.html` and `healed-v6-healing-focused.html` per fixture
   - Reports real violation fixes for each

### Phase 2C-2: WCAG-Based Benchmarking (1 hour)

**Goal:** Compare baseline violations to healed violations

**Metrics to generate:**
```
For each fixture + variant:
  - Baseline violations: (from wcag-baseline-report.json)
  - Remaining violations: (run wcag_validator on healed-*.html)
  - Violations fixed: baseline - remaining
  - Healing effectiveness: (baseline - remaining) / baseline * 100

Aggregate across all fixtures:
  - v1-current healing: X% of total violations fixed
  - v6-healing-focused: Y% of total violations fixed
  - Improvement: (Y - X) percentage points
```

### Phase 2C-3: Multi-Model Comparison (Phase 3)

**Goal:** Test alternative models for specialized fixtures

**Models to test:**
1. **Claude 3.5 Sonnet** — Better structured reasoning
   - Expected advantage: Higher healing on complex hierarchies
   - Test on: 007-nested-lists (56 violations), 002-complex-table (5 violations)

2. **GPT-4V** — Superior OCR on scanned content
   - Expected advantage: Better image description for scanned PDFs
   - Test on: 003-scanned-image (94 violations, 84 missing alt text)

3. **Gemini 1.5 Pro** — Long-context handling
   - Expected advantage: Better multi-page reasoning
   - Test on: 008-mixed-content (139 violations), 007-nested-lists (56 violations)

---

## Implementation Requirements

### What's Already Done ✅
- [x] Phase 2A: Real ground truth extraction (all 9 fixtures)
- [x] WCAG baseline validator (wcag_validator.py)
- [x] Violation baseline report (346 total)
- [x] v6-healing-focused prompt variant
- [x] WCAG analysis framework (rebenchmark_with_wcag.py)

### What Needs to Be Done ⏳
- [ ] Healing pipeline: take expected-html.html → apply v1/v6 → save healed-*.html
- [ ] WCAG re-benchmarking: compare baseline to healed violations
- [ ] Real healing effectiveness metrics (violations-fixed %)
- [ ] Multi-model testing with Claude, GPT-4V, Gemini variants

---

## Expected Outcomes

### Conservative Estimate (Based on v6 Design)
- **v1-current baseline healing:** 15-25% of violations fixed
  - Should add `<main>` landmark (9 violations fixed immediately)
  - Should add lang attribute (9 violations fixed immediately)
  - Total quick wins: ~18 violations = 5% of baseline

- **v6-healing-focused improvement:** +10-20 percentage points
  - 4-pass iterative approach should catch more alt text
  - Should improve link text detection
  - Target: 25-45% of violations fixed

### Success Criteria
- [ ] v1-current fixes ≥ 5% of violations (18+ violations)
- [ ] v6-healing-focused fixes ≥ 20% of violations (69+ violations)
- [ ] Improvement gap between variants ≥ 10 percentage points
- [ ] Best model reaches ≥ 40% healing on at least 3 fixtures

---

## Files Generated

**Config & Baselines:**
- ✅ `wcag-baseline-report.json` — Baseline violations per fixture
- ✅ `wcag_validator.py` — WCAG 2.2 detection
- ✅ `rebenchmark_with_wcag.py` — Real healing analysis

**To Be Generated:**
- `heal_fixture.py` — Single fixture healing
- `heal_all_fixtures.py` — Batch healing for all variants
- `healed-v1-current.html` (per fixture)
- `healed-v6-healing-focused.html` (per fixture)
- `healing-analysis-v1-vs-v6.json` — Real comparison
- `multi-model-analysis.json` — Claude, GPT-4V, Gemini results

---

## Next Step

Create healing pipeline that:
1. Reads expected-html.html (baseline)
2. Runs through v1-current prompt variant
3. Saves healed output
4. Validates with WCAG checker
5. Reports violations fixed %

**Estimated time:** 3-4 hours to complete full Phase 2C with real validation

---

**Owner:** Brain Training Team  
**Status:** Ready to implement Phase 2C-1 (healing pipeline)
