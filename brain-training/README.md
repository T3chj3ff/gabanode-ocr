# Brain Training Framework — PDF Remediation Engine

**Phase 1: Test Fixture Library & Baseline Benchmarking**

This directory contains the systematic training system for improving the GABAnode PDF remediation engine's AI accuracy.

## Quick Start

```bash
cd brain-training

# Run baseline benchmark across all fixtures
node benchmark/run-benchmark.js --fixtures=all --prompt=v1-current

# Test a single fixture with a new prompt
node benchmark/run-benchmark.js --fixture=002-complex-table --prompt=v2-improved-clarity

# Compare two prompt variants
node benchmark/compare-prompts.js v1-current v2-improved-clarity
```

## Directory Structure

```
brain-training/
├── fixtures/              # 9 test cases from simple to complex
├── benchmark/             # Scoring and test runner
├── prompt-variants/       # 5 prompt variants for A/B testing
└── README.md
```

## Fixtures (001-009)

| Fixture | Type | Purpose | Expected Score |
|---------|------|---------|-----------------|
| 001 | Plain text | Baseline extraction | 95%+ |
| 002 | Complex tables | Table fidelity with merged cells | 85%+ |
| 003 | Scanned image | Low-res OCR handling | 70%+ |
| 004 | PDF form | Form field detection | 80%+ |
| 005 | Multi-column | Column layout preservation | 80%+ |
| 006 | Images+captions | Alt text quality | 85%+ |
| 007 | Nested lists | List nesting (5+ levels) | 85%+ |
| 008 | Mixed content | Tables + images + text | 80%+ |
| 009 | Edge cases | No h1, duplicate IDs, etc. | 75%+ |

## Prompt Variants

- **v1-current.js** — Current production prompts (baseline)
- **v2-improved-clarity.js** — More explicit constraints
- **v3-step-by-step.js** — Decomposed extraction steps
- **v4-examples-based.js** — Good/bad examples included
- **v5-chain-of-thought.js** — Reasoning before output

## Benchmark Scoring

**Extraction Accuracy (100 points):**
- Heading hierarchy (10)
- Table fidelity (15)
- Image descriptions (10)
- List preservation (8)
- Content completeness (12)
- No hallucination (20)
- Markdown validity (15)
- WCAG compliance (10)

**Healing Accuracy (100 points):**
- Violations fixed (20)
- False positives (-15)
- Content preservation (30)
- Performance: heal time (10)

See `benchmark/scoring-rubric.md` for full details.

## Execution Checklist (Week 1)

- [x] Create directory structure
- [ ] Populate 9 fixtures (PDFs + expected outputs)
- [ ] Implement benchmark-scoring.js
- [ ] Run baseline scores for v1-current
- [ ] Document violations in results/

## References

- Core engine: `../../app/api/ocr/route.js`
- Full training plan: `../BRAIN_TRAINING.md`
- Test PDF: `../Exhibit_1_Test.pdf` (15MB)

