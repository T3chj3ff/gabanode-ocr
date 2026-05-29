# Phase 2: Brain Training Analysis & 40+ Improvement Steps

**Date:** 2026-05-13  
**Status:** Fixture population complete, baseline established, all variants tested

---

## **BASELINE RESULTS (v1-v5 Summary)**

| Metric | v1-current | v2-clarity | v3-step | v4-examples | v5-cot | Avg |
|--------|-----------|-----------|---------|-------------|--------|-----|
| Extraction | 100% | 100% | 100% | 100% | 100% | **100%** |
| Healing | 22% | 22% | 22% | 22% | 22% | **22%** |
| Combined | 61% | 61% | 61% | 61% | 61% | **61%** |
| Target | 90% / 85% | → | → | → | → | **61% ✗ TARGET** |

### **Key Finding:**
All 5 prompt variants converge at identical scores. This indicates:
- ✅ **Extraction is solved** (100% accuracy across all prompts)
- ⚠️ **Healing is the critical bottleneck** (22% average, target 85%)
- 📊 **Current benchmark uses placeholder expected-html.html** (inflates healing scores)

**Real healing performance is likely LOWER when tested against actual WCAG-compliant ground truth.**

---

## **40+ ADVANCEMENT STEPS FOR BRAIN IMPROVEMENT**

### **PHASE 2A: Ground Truth Generation (Days 3-4)**

1. **Extract HTML from Tagged PDFs** — Convert PDFUA-compliant tagged PDFs to actual HTML using pdftohtml or similar. These become real ground truth for healing validation.

2. **Accessibility Audit Ground Truth** — Run axe-core on extracted HTML to generate baseline accessibility report (violations, violations fixed %, compliance score).

3. **Create Fixture Metadata Database** — Build JSON registry mapping each fixture to: PDF characteristics, extracted text word count, baseline a11y violations, target violation count.

4. **Compare Tagged vs Untagged PDFs** — Differential analysis: what changed between tagged (source) and untagged? This defines "correct healing" for each fixture.

5. **Validate Fixture Mapping Quality** — Verify each fixture (001-009) actually targets intended complexity (scanned doc should have OCR issues, form should have input fields, etc.).

6. **Document Expected Transformations** — For each fixture, write explicit rules: "Fixture 002 should detect 5 table columns, merge 3 header cells, convert to Markdown table with proper alignment"

7. **Create Visual Diff Tool** — Build side-by-side comparison: source PDF → current extraction → current healing → expected healing (makes failures obvious)

8. **Extract OCR Confidence Scores** — For scanned PDFs (003, 009), capture OCR confidence per word, use as weighting factor in accuracy scoring

9. **Analyze Healing Variance** — Run healing 5x on same fixture, check determinism. If healing varies, that's why scores are low (non-deterministic output)

10. **Implement Fuzzy Matching in Scoring** — Instead of exact HTML comparison, use ~80% match threshold for structure (handles minor formatting differences)

---

### **PHASE 2B: Healing Prompt Optimization (Days 5-7)**

11. **Separate Extract & Heal Prompts** — Currently they're bundled. Test them independently. Maybe extraction needs v1, healing needs v5.

12. **Healing-Focused Prompt (v6)** — New variant: skip extraction optimization, focus 100% on WCAG violation fixing. Assume extract is good, fix it to AA+.

13. **Violation-Specific Prompts** — Instead of one heal prompt, create 5 specialized versions:
    - v6-alt-text (images)
    - v6-form-labels (forms)
    - v6-heading-hierarchy (structure)
    - v6-color-contrast (colors)
    - v6-landmarks (layout)

14. **Add Axe-Core Feedback Loop** — Run axe-core on healed output, feed violations back into prompt: "Your output had 7 violations: [list]. Fix these."

15. **Iterative Healing Pipeline** — Instead of single heal pass:
    - Pass 1: Structural (headings, landmarks, lists)
    - Pass 2: Attributes (alt, labels, titles)
    - Pass 3: Semantic (ARIA, roles)
    - Pass 4: Validation (axe-core compliance check)

16. **Content Preservation Constraint** — Add explicit prompt rule: "Do NOT remove, truncate, or summarize text. Every word in input must appear in output."

17. **HTML Bloat Detection** — Flag unnecessary wrappers/divs post-healing. Prompt should simplify structure, not add divs.

18. **Markdown→HTML Quality Check** — If input is Markdown, validate that HTML conversion preserves all semantics (lists, blockquotes, code blocks).

19. **Language Detection & Handling** — Some fixtures are in German (05, 07). Ensure healing respects lang attribute and doesn't "fix" non-English text.

20. **WCAG Level Enforcement** — Current target is AA. Test separate v6-wcag-aaa variant for Level AAA compliance (higher bar).

21. **PDF Metadata Preservation** — Extract title, author, keywords from source PDF, inject into healed HTML <head>.

22. **Cross-Reference Validation** — For docs with "See Figure 3" or "Table 2", verify cross-references still point to correct elements post-heal.

23. **Form Field Validation** — For fixture 004, validate: all <input> has matching <label>, proper input types (email, number, etc.), autocomplete attributes.

24. **Table Cell Scope Attributes** — Ensure all <th> has scope="row|col", all <td> in data tables has proper associations.

25. **Skip-Link Injection** — Add <a href="#main">Skip to main content</a> to all healed HTML, with corresponding #main anchor.

---

### **PHASE 2C: Multi-Model Testing (Days 8-10)**

26. **Claude 3.5 Sonnet Extraction** — Create v7-claude-sonnet variant, test extraction accuracy vs Gemini 2.0 Flash (may be slower but more accurate)

27. **GPT-4V Comparison** — Test OpenAI's vision model for scanned PDFs (003, 009) - it may excel at OCR-heavy fixtures

28. **Gemini 1.5 Pro Testing** — Test long-context model for large documents like magazine (008) - does it handle 12.9MB better?

29. **Model-Specific Fine-Tuning** — Each model has different strengths: tailor prompts per model (Claude likes step-by-step, GPT-4 likes examples)

30. **Fallback Model Strategy** — If primary model fails, automatically route to secondary model. Implement: Gemini 2.0 Flash → Claude 3.5 → GPT-4 fallback

31. **Latency Profile** — Measure extraction time per model per fixture. Trade accuracy vs speed (60s Vercel timeout constraint)

32. **Cost Analysis** — Compare API costs: Gemini ($/1M tokens) vs Claude vs GPT-4. Budget for 50 real-world PDFs batch processing

33. **Accuracy vs Cost Curve** — Plot accuracy gain vs additional cost. Find optimal point (maybe v2 + Gemini is 80% cheaper than v5 + Claude for same results)

34. **Model Ensemble** — For critical docs, run 3 models, vote on output. Majority wins. Trade latency for accuracy on CC01 docs.

---

### **PHASE 2D: Fixture-Specific Optimization (Days 11-12)**

35. **Simple Text Deep-Dive (001)** — Target is 95%, getting 100%. Can we maintain 100% while lowering healing latency?

36. **Complex Table Strategy (002)** — Currently 59%. Test table-specific extraction: detect merged cells, column alignment, header row. Use v6-table-specific.

37. **Scanned Image OCR (003)** — Currently 59%. Use Tesseract post-processing on low-confidence words. Or switch to Claude (better OCR) for this fixture.

38. **Form Detection Logic (004)** — Currently 59%. Add explicit form field detection (input, select, textarea, checkbox). Generate form accessibility checklist.

39. **Multi-Column Layout (005)** — Currently 59%. Detect column order using spatial analysis. Test: is Gemini 2.0 Flash confusing column reading order?

40. **Image Caption Linking (006)** — Currently 59%. Validate that captions are associated with images. Add aria-describedby links post-healing.

41. **Nested List Preservation (007)** — Currently 59%. Verify list nesting depth is maintained (max 6 levels). Test: Markdown nesting → HTML nesting conversion.

42. **Mixed Content Orchestration (008)** — Currently 60%. This fixture has everything. Test: sequential extraction (text → tables → images → lists) vs unified extraction.

43. **Edge Case Triage (009)** — Currently 60%. This fixture has intentional violations. Test: does heal prompt recognize violations, or does it "pass through" broken HTML?

---

### **PHASE 3: Real-World Validation (Days 13-18)**

44. **Exhibit_1_Test.pdf Full Run** — Process the 15MB real document. Measure: extraction time, healing time, final WCAG score, user satisfaction.

45. **cityofmaplewood Batch 50** — Run best variant on 50 real government PDFs. Collect metrics: avg time, failure rate, manual intervention needed.

46. **Failure Root Cause Analysis** — For each failed fixture, categorize: OCR error, layout misunderstanding, ARIA incorrect, form field miss, etc. Build failure taxonomy.

47. **User Feedback Integration** — Have actual users correct healing output. Capture: what did they change? This becomes retraining data.

48. **Performance Under Load** — Simulate 10 concurrent PDF jobs. Do API rate limits kick in? Does batching improve throughput?

49. **Cost-Benefit Analysis** — Is spending 3x API cost on v5-cot worth 10% accuracy gain? Build ROI spreadsheet.

50. **Scaling Strategy** — If processing 1000s of PDFs, what's the optimal queue/batch size? Parallel processing vs sequential?

---

### **PHASE 4: Production Hardening (Days 19-22)**

51. **Prompt Version Control** — Tag final variant (e.g., v2.1-prod) with exact model version, temperature, token limits. Document in Git.

52. **Monitoring & Alerting** — Log: extraction time, healing time, WCAG score, user manual edits. Alert if avg accuracy drops >5%.

53. **Rollback Automation** — If production accuracy < baseline, auto-rollback to v1. Manual promotion required for new variants.

54. **A/B Testing Setup** — Route 20% to new variant, 80% to v1 baseline. Track user edits as implicit accuracy signal.

55. **Documentation Update** — Write runbook: how to test new prompt variants, how to measure accuracy, how to deploy to production.

56. **Edge Case Hardening** — Test: corrupted PDFs, PDFs with no pages, 500MB+ files, password-protected PDFs, image-only PDFs.

57. **Fallback Content** — If healing fails after 3 attempts, return raw extracted Markdown with confidence warning rather than broken HTML.

58. **Token Budgeting** — Each fixture has token budget. Monitor: are we exceeding budgets? Optimize prompts to reduce token count.

59. **Timeout Graceful Degradation** — If healing takes >20s, return extraction-only result (structured Markdown). Don't fail.

60. **Model Switching Logic** — If Gemini API is down, automatically switch to Claude. Transparent to application layer.

---

## **IMMEDIATE ACTION ITEMS (Next 48 Hours)**

### **Priority 1: Generate Real Ground Truth**
```bash
# For each fixture, extract actual HTML from tagged PDFs:
python3 extract_ground_truth.py

# Run axe-core on extracted HTML to get baseline violations:
for fixture in fixtures/00*; do
  axe $fixture/reference-tagged.pdf --rules wcag21aa > $fixture/baseline-violations.json
done
```

### **Priority 2: Test Healing-Focused Variant (v6)**
Create `prompt-variants/v6-healing-focused.js`:
- Skip extraction optimization (assume v1 extraction is good)
- Focus 100% on WCAG AA+ compliance
- Use iterative healing (4 passes: structure → attributes → semantic → validation)
- Add explicit "do not remove text" constraint

### **Priority 3: Rerun Benchmark Against Real Ground Truth**
```bash
node run-benchmark.js --fixtures=all --prompt=v1-current --compare-html=true
```
This uses actual extracted HTML as ground truth, will show real healing performance (expect 10-30% scores).

---

## **EXPECTED OUTCOMES (Phase 2)**

| Outcome | Timeline | Owner | Success Metric |
|---------|----------|-------|-----------------|
| Real ground truth generated | Day 4 | Script | 9/9 expected-html.html from PDFs |
| v6-healing variant created & tested | Day 7 | Development | >50% healing score on v6 |
| Multi-model comparison complete | Day 10 | Testing | Clear winner identified |
| Exhibit_1_Test processed | Day 14 | Validation | <30s end-to-end, >80% WCAG AA |
| Production variant selected | Day 18 | Approval | v2, v3, or v6 deployed |
| Monitoring in place | Day 22 | DevOps | Alerts firing, metrics tracked |

---

## **SUCCESS CRITERIA (Week 2 Complete)**

✅ Baseline: 61% combined accuracy (all variants)  
🎯 Target: 80% combined accuracy on real ground truth  
📈 Improvement: +19 percentage points through healing optimization

If v6-healing-focused hits >75%, we deploy to production immediately.  
If all variants plateau, escalate to Phase 3 (multi-model testing).

---

**Next Meeting:** After real ground truth is generated (Day 4)  
**Owner:** Brain Training Team  
**Status:** Ready to execute Phase 2A
