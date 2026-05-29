# Phase 2C: Project Euclid Healing Pipeline

**Status:** Run 48 complete — WCAG-30 corpus at 100% with `v14-corpus-expansion`  
**Date:** 2026-05-28  
**Current production variant:** `v14-corpus-expansion`

---

## Current Production Variant

As of Run 48, the validator detects 4 additional WCAG violation classes:
focus-visible removal (WCAG 2.4.7), missing autocomplete tokens (WCAG 1.3.5),
missing live-region semantics (WCAG 4.1.3), and missing reduced-motion overrides
(WCAG 2.3.3). That is why v11-v13 score 93.2% on the WCAG-30 corpus even
though they remain 100% on the earlier WCAG-26 corpus.

| Variant | Corpus | Status | Use for |
|---|---|---|---|
| v14-corpus-expansion | WCAG-30 (527 violations) | ✅ Canonical (Run 48+) | All new deployments |
| v13-phase4 | WCAG-26 (499 violations) | 📦 Historical | Reproducing pre-Run-48 results |
| v12-phase3d | WCAG-26 | 📦 Historical | Reference only |
| v11-production-ready | WCAG-26 | 📦 Historical | Reference only |
| v7-v10 | WCAG-26 | 🧪 Ablation baselines | Benchmarking |

Use `python3 deterministic_healer.py` to regenerate healed outputs and
`python3 rebenchmark_with_wcag.py v14-corpus-expansion` to verify the canonical
variant. Do not use the older Gemini prompt scripts for production scoring.

---

## Historical LLM Pipeline Context

The sections below document the original Phase 2C-1 Gemini prompt pipeline. They
are retained for reference; Run 48 production scoring is deterministic and uses
`v14-corpus-expansion`.

## What Was Built

### Core Scripts

1. **heal_fixture.py** — Single fixture healing processor
   - Reads `expected-html.html` from a fixture
   - Applies healing prompt via Gemini 1.5 Pro
   - Runs either v1-current or v6-healing-focused variant
   - Validates healed HTML with WCAG checker
   - Saves `healed-{variant}.html`
   - Reports violations fixed %

   Usage:
   ```bash
   python3 heal_fixture.py 001-simple-text v1-current
   python3 heal_fixture.py 008-mixed-content v6-healing-focused
   ```

2. **heal_all_fixtures.py** — Batch healing processor
   - Discovers all 9 fixtures in `fixtures/` directory
   - Runs each through both v1-current and v6-healing-focused
   - Generates healed-*.html files per fixture
   - Produces comprehensive comparison report
   - Outputs: `healing-analysis-v1-vs-v6.json`

   Usage:
   ```bash
   python3 heal_all_fixtures.py
   ```

### Healing Prompt Variants

**v1-current (baseline):**
- Pass 1: Structure & landmarks (main tag, heading hierarchy)
- Pass 2: Attributes (alt text, form labels, titles)
- Pass 3: Semantic (ARIA, roles, table scope)
- Pass 4: Validation & polish

**v6-healing-focused (4-pass iterative):**
- Pass 1: Structure & landmarks with context awareness
- Pass 2: Attributes with explicit focus on missing alt text + empty links
- Pass 3: Semantic enrichment (ARIA, roles, table scope, aria-live)
- Pass 4: Validation & polish with aria-hidden cleanup

---

## Current Blockers

### Missing API Credentials
The healing pipeline requires Gemini API access. To proceed:

**Option 1: Set environment variable (recommended)**
```bash
export GEMINI_API_KEY="your-api-key-here"
python3 heal_all_fixtures.py
```

**Option 2: Pass as argument**
```bash
python3 heal_all_fixtures.py "your-api-key-here"
```

**Option 3: Create .env file**
```bash
# In brain-training directory:
echo "GEMINI_API_KEY=your-api-key-here" > .env.local

# Then use in Python:
from dotenv import load_dotenv
load_dotenv('.env.local')
```

### Alternative: Use different model
If Gemini API is not available, the scripts can be adapted for:
- **Claude API** (claude-3-5-sonnet-20241022)
- **GPT-4V** (gpt-4-vision-preview)

Scripts would need minor modifications to support these.

---

## Expected Workflow (Once Credentials Available)

### Phase 2C-1: Healing Pipeline
```
1. python3 heal_all_fixtures.py
   ↓
2. Generates healed-v1-current.html and healed-v6-healing-focused.html
   per fixture (18 files total)
   ↓
3. Validates each with WCAG 2.2 AA checker
   ↓
4. Produces healing-analysis-v1-vs-v6.json with:
   - Per-fixture violation comparison
   - Per-variant aggregate metrics
   - Improvement percentage (v6 vs v1)
```

### Expected Results
- **v1-current baseline healing:** 15-25% of violations fixed
  - Quick wins: main landmark (9 violations), lang attribute (9 violations)
  
- **v6-healing-focused:** 25-45% of violations fixed
  - Iterative approach should catch more missing alt text
  - Better link text generation
  
- **Improvement target:** ≥10 percentage points (v6 - v1)

### Success Criteria
- [ ] v1-current fixes ≥ 5% of violations (18+ violations)
- [ ] v6-healing-focused fixes ≥ 20% of violations (69+ violations)
- [ ] Improvement gap ≥ 10 percentage points
- [ ] Best model reaches ≥ 40% healing on at least 3 fixtures

---

## Files Created

| File | Purpose |
|------|---------|
| `heal_fixture.py` | Single fixture healing (both variants) |
| `heal_all_fixtures.py` | Batch processing all 9 fixtures |
| `HEALING_PIPELINE_README.md` | This file |

## Files That Will Be Generated

| File | Purpose |
|------|---------|
| `healed-v1-current.html` (per fixture) | Healed HTML using v1-current variant |
| `healed-v6-healing-focused.html` (per fixture) | Healed HTML using v6-healing-focused variant |
| `healing-{variant}-result.json` (per fixture) | Per-fixture healing metrics |
| `healing-analysis-v1-vs-v6.json` | Comprehensive comparison report |
| `healing-summary-v1-current.json` | v1 aggregate results |
| `healing-summary-v6-healing-focused.json` | v6 aggregate results |

---

## Baseline (for Reference)

From Phase 2C-0 WCAG validation:
- **Total baseline violations:** 346
- **Per-fixture distribution:**
  - 001-simple-text: 5
  - 002-complex-table: 5
  - 003-scanned-image: 94 (image-heavy)
  - 004-form-with-fields: 3
  - 005-multi-column: 7
  - 006-images-with-captions: 12
  - 007-nested-lists: 56
  - 008-mixed-content: 139 (most complex)
  - 009-edge-cases: 25

- **Violation breakdown:**
  - Missing alt text: 195 (56%)
  - Empty link text: 133 (38%)
  - Missing main landmark: 9 (3%)
  - Missing lang attribute: 9 (3%)

---

## Next Steps (Phase 2C-2)

Once healing is complete:

1. **WCAG Re-Benchmarking**
   - Compare baseline violations to healed violations
   - Calculate violations-fixed % per fixture + variant
   - Aggregate across all fixtures

2. **Multi-Model Comparison (Phase 3)**
   - Test Claude 3.5 Sonnet on complex hierarchies (007, 002)
   - Test GPT-4V on scanned content (003)
   - Test Gemini 1.5 Pro on multi-page content (008, 007)

3. **Optimization**
   - Identify which prompt variant wins per fixture type
   - Refine best-performing variant for production

---

**Owner:** Brain Training Team  
**Status:** Awaiting API credentials to execute healing pipeline
