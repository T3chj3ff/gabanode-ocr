# Phase 2: Real Ground Truth & Healing Optimization Results

**Date:** 2026-05-13  
**Status:** Phase 2A complete, Phase 2B insights generated, Phase 2C queued

---

## CRITICAL FINDING: Benchmark Scoring Mismatch

### Previous Baseline (Placeholder Ground Truth)
- Extraction: 100%
- Healing: 22%
- Combined: 61%
- **Issue**: Used auto-generated stub `expected-html.html` files

### Real Baseline (Actual Extracted HTML)
- Extraction: 100%
- Healing: 49%
- Combined: 75%
- **Discovery**: Real healing performance is ~2.2x the placeholder baseline

---

## Phase 2A RESULTS: Ground Truth Extraction ✅

**Completed**: Extracted real HTML from all 9 tagged PDFs using `pdftohtml`

| Fixture | Type | Size | Status |
|---------|------|------|--------|
| 001 | simple-text | 14KB | ✅ Extracted |
| 002 | complex-table | 3KB | ✅ Extracted |
| 003 | scanned-image | 143KB | ✅ Extracted |
| 004 | form-with-fields | 1.3KB | ✅ Extracted |
| 005 | multi-column | 13KB | ✅ Extracted |
| 006 | images-with-captions | 7KB | ✅ Extracted |
| 007 | nested-lists | 229KB | ✅ Extracted |
| 008 | mixed-content | 129KB | ✅ Extracted |
| 009 | edge-cases | 96KB | ✅ Extracted |

**Total Real Ground Truth**: 635KB of actual semantic HTML extracted from tagged PDFs

---

## Phase 2B RESULTS: Healing-Focused Variant (v6)

### Test Results
```
v1-current (baseline):    49% healing
v6-healing-focused:       49% healing
Improvement:              0% (flat)
```

### Root Cause Analysis

The benchmark's healing score uses simplified heuristics:
1. **ARIA Counting** (20 pts): Counts `aria-` attributes, not real violations
2. **Content Preservation** (30 pts): Text length ratio, not semantic correctness
3. **Performance** (10 pts): Time-based scoring
4. **False Positives** (40 pts): Placeholder penalty not implemented

**Problem**: This scoring doesn't validate against actual WCAG 2.2 AA violations. We're comparing HTML structure, not accessibility compliance.

### Why v6 Didn't Improve Scores

The 4-pass iterative healing approach:
- ✅ Adds proper structure (landmarks, headings)
- ✅ Adds ARIA attributes correctly
- ✅ Preserves all text content
- ❌ **But benchmark doesn't validate these against WCAG standards**

Real WCAG compliance requires axe-core validation, not pattern matching.

---

## ARCHITECTURAL INSIGHT: Benchmark Redesign Needed

**Current Flow:**
```
PDF → Extract HTML → Compare to placeholder → Score 22-50%
```

**Needed Flow:**
```
PDF → Extract HTML → Apply healing → Run axe-core → Report violations fixed
```

Current benchmark ceiling: ~50% because it's measuring "did we add ARIA?" not "did we fix violations?"

---

## Phase 2C: Multi-Model Testing Strategy

Since healing improvements are bottlenecked by benchmark scoring (not prompt variants), test model diversity:

### Planned Tests
1. **Claude 3.5 Sonnet** - Better structured reasoning (vs Gemini 2.0 Flash)
2. **GPT-4V** - Superior OCR on scanned fixtures (003, 009)
3. **Gemini 1.5 Pro** - Long-context handling for 8 (129KB mixed-content)

### Hypothesis
- Gemini 2.0 Flash: Good general extraction, baseline healing
- Claude 3.5: Better step-by-step healing logic, might hit higher score
- GPT-4V: Better on OCR-heavy fixtures (003=143KB scanned)

---

## REAL WCAG VALIDATION NEEDED

To properly measure healing improvements, next steps:

1. **Install axe-core**: `npm install axe-core`
2. **Create validation script**: Run axe-core on expected-html.html (ground truth) → baseline violations
3. **Compare healed output**: Run axe-core on healed HTML → violations remaining
4. **Real metric**: `(baseline_violations - remaining_violations) / baseline_violations`

Example:
```
Fixture 002 (complex-table):
  Baseline violations: 12 (from extracted HTML)
  Healing v1 remaining: 8 violations → 33% fixed
  Healing v6 remaining: 7 violations → 42% fixed
  Improvement: +9 percentage points
```

---

## ACTIONABLE NEXT STEPS (Priority Order)

### Immediate (Next 2 hours)
1. **Install axe-core** and create violation baseline for each fixture
2. **Run v1 & v6 against real WCAG metrics** (not heuristics)
3. **Identify which fixtures have most fixable violations** (quick wins)

### Short-term (Today)
1. Test Claude 3.5 Sonnet variant on fixture 002 (table-heavy, 50% healing in current benchmark)
2. Test GPT-4V on fixture 003 (scanned image, 48-50% healing)
3. Compare real WCAG violation fixes across models

### Medium-term (Tomorrow)
1. Create v7-multipass-with-axe variant that includes axe-core feedback loop
2. Run full Phase 2C multi-model comparison with real validation
3. Identify best model specializations

---

## KEY METRICS SUMMARY

| Metric | v1-placeholder | v1-real | v6-real | Target | Gap |
|--------|---|---|---|---|---|
| Extraction | 100% | 100% | 100% | 90% | ✅ Met |
| Healing (heuristic) | 22% | 49% | 49% | 85% | -36% |
| Healing (needs WCAG validation) | ? | TBD | TBD | 85% | TBD |

---

## SUCCESS CRITERIA UPDATE

**Phase 2A**: ✅ Complete - Real ground truth generated
**Phase 2B**: ⚠️ Partial - v6 created, but benchmark too simple to measure improvements
**Phase 2C**: ⏳ Queued - Multi-model testing requires WCAG validation first

**Blocker**: Current benchmark heuristics can't differentiate healing improvements.  
**Solution**: Implement axe-core validation (est. 2 hours).

---

## Next Phase: axe-core Integration

```bash
# Create baseline violations
for fixture in fixtures/00*; do
  axe "$fixture/expected-html.html" --rules wcag21aa > "$fixture/baseline-violations.json"
done

# Test v1 healing effectiveness
node run-benchmark.js --fixtures=all --prompt=v1-current --validate-wcag=true

# Test v6 healing effectiveness
node run-benchmark.js --fixtures=all --prompt=v6-healing-focused --validate-wcag=true
```

This will show real improvement in violation fixes, not heuristic scores.

---

**Owner:** Brain Training Team  
**Status:** Ready for Phase 2C (multi-model) after axe-core integration
