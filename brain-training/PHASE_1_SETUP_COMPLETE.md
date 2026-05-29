# Phase 1: Setup Complete ✅

**Date:** 2026-05-12  
**Status:** Framework structure created and ready for fixture population

---

## What's Been Created

### 1. Directory Structure ✅
```
brain-training/
├── fixtures/               (9 directories, 001-009)
│   ├── 001-simple-text/
│   ├── 002-complex-table/
│   ├── 003-scanned-image/
│   ├── 004-form-with-fields/
│   ├── 005-multi-column/
│   ├── 006-images-with-captions/
│   ├── 007-nested-lists/
│   ├── 008-mixed-content/
│   └── 009-edge-cases/
├── benchmark/
│   ├── run-benchmark.js    (Test runner with scoring)
│   ├── scoring-rubric.md   (Detailed scoring methodology)
│   └── results/            (Output directory for test runs)
├── prompt-variants/
│   ├── v1-current.js       (Baseline: current prompts)
│   ├── v2-improved-clarity.js   (Improved constraints)
│   ├── v3-step-by-step.js  (Decomposed extraction)
│   ├── v4-examples-based.js (Few-shot learning)
│   └── v5-chain-of-thought.js (Reasoning before output)
└── README.md               (Quick-start guide)
```

### 2. Benchmark System ✅
- **Scoring Rubric:** 100-point extraction score + 100-point healing score
- **Metrics:** Heading hierarchy, table fidelity, image descriptions, list preservation, content completeness, hallucination detection, Markdown validity, WCAG compliance
- **Test Runner:** Node.js script to run fixtures, score outputs, and generate reports
- **Results Storage:** JSON format for tracking prompt performance over time

### 3. Prompt Variants ✅
| Variant | Strategy | Expected Impact |
|---------|----------|-----------------|
| v1 | Current baseline | Establish baseline accuracy |
| v2 | Explicit constraints + examples | Reduce hallucination |
| v3 | Step-by-step decomposition | Force deliberate extraction |
| v4 | Few-shot examples (good/bad) | Improve formatting accuracy |
| v5 | Chain-of-thought reasoning | Highest accuracy (slower) |

### 4. Test Fixtures (9 Total) ✅
| # | Type | Purpose | Target |
|---|------|---------|--------|
| 001 | Simple text | Baseline | 90%+ |
| 002 | Complex table | Table handling | 85%+ |
| 003 | Scanned image | OCR degradation | 70%+ |
| 004 | PDF form | Form detection | 80%+ |
| 005 | Multi-column | Column layout | 80%+ |
| 006 | Images+captions | Alt text quality | 85%+ |
| 007 | Nested lists | Deep nesting | 85%+ |
| 008 | Mixed content | All elements | 80%+ |
| 009 | Edge cases | Violations | 77%+ |

**Fixture Content:** Each has README.md with test scenarios. Waiting for actual PDFs and expected outputs.

---

## Next Steps (Week 1)

### Immediate (This Phase, Before Running Tests)
- [ ] Obtain/create 9 test PDF files (source.pdf in each fixture directory)
- [ ] Generate ground-truth expected-md.md for each fixture (manual extraction)
- [ ] Generate ground-truth expected-html.html for each fixture (manual healing target)
- [ ] Populate expected-score.json with target thresholds

### After Fixtures Are Ready
- [ ] Run baseline benchmark: `node benchmark/run-benchmark.js --fixtures=all --prompt=v1-current`
- [ ] Review baseline results against targets
- [ ] Document any gaps between baseline and targets

### Week 2 (Prompt Optimization)
- [ ] Test v2-improved-clarity against all 9 fixtures
- [ ] Test v3-step-by-step against all 9 fixtures
- [ ] Test v4-examples-based against all 9 fixtures
- [ ] Test v5-chain-of-thought against selected difficult fixtures (002, 007, 008, 009)
- [ ] Compare results: create benchmark comparison report

### Week 3 (Deployment & Validation)
- [ ] Select best-performing prompt variant
- [ ] Deploy improved prompt to production (app/api/ocr/route.js)
- [ ] Run against Exhibit_1_Test.pdf (15MB real-world test)
- [ ] Batch-scan 50 PDFs from Cabinet_Lab/GovTech/cityofmaplewood
- [ ] Measure improvements: time-to-fix, accuracy gain, healing rounds reduction

---

## Running Tests

Once fixtures are populated with PDFs:

```bash
# Run all fixtures with v1-current baseline
node benchmark/run-benchmark.js --fixtures=all --prompt=v1-current

# Test a single fixture with new prompt
node benchmark/run-benchmark.js --fixture=002-complex-table --prompt=v2-improved-clarity

# Compare two variants side-by-side
node benchmark/compare-prompts.js v1-current v2-improved-clarity
```

Results saved to: `benchmark/results/benchmark-[variant]-[timestamp].json`

---

## Key Files

| File | Purpose |
|------|---------|
| `BRAIN_TRAINING.md` | Master training plan (3-week roadmap) |
| `README.md` | Quick-start guide |
| `benchmark/scoring-rubric.md` | Detailed scoring methodology (8 extraction metrics + 4 healing metrics) |
| `benchmark/run-benchmark.js` | Test runner (340 lines, scoring logic) |
| `prompt-variants/v*.js` | 5 prompt variants for A/B testing |

---

## Current Blockers

❌ **Missing:** Actual PDF files for fixtures  
- Need to source or create 9 test PDFs covering all scenarios
- Can use Exhibit_1_Test.pdf as a starting point for 002-complex-table

❌ **Missing:** Ground-truth expected outputs  
- Expected-md.md and expected-html.html are templates
- Need manual verification or reference implementation

---

## Success Metrics (Week 1 Target)

| Metric | Target | Status |
|--------|--------|--------|
| Framework structure | 100% complete | ✅ |
| Benchmark scorer | Working | ✅ |
| Prompt variants | 5 variants ready | ✅ |
| Fixture directories | 9 directories | ✅ |
| Fixture templates | All have README | ✅ |
| Test runner | Executable | ✅ |
| **Fixtures populated** | **9/9** | ⏳ Pending PDF sourcing |
| Baseline established | N/A | ⏳ Pending fixture completion |

---

## Authority & Approval

**L1 Approval:** Jeff approved "recover + strengthen" for Project Dora decision  
**Task Ownership:** Brain Training Phase 1 (Framework Setup) — Claude (autonomous L2)  
**Escalation Path:** If fixtures cannot be sourced, escalate to Jeff for PDF location/creation direction

---

**Ready to Proceed When:** Fixture PDFs and expected outputs are available  
**Estimated Time to Completion (Week 1):** 2-3 days with PDFs; waiting on source material

