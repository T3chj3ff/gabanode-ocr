# Phase 2C-3: Council-Powered Multi-Model Testing

**Date:** 2026-05-14  
**Status:** Ready for implementation  
**Integration:** claude-council for parallel multi-model healing

---

## Architecture Overview

Instead of sequential testing (Claude → GPT-4V → Gemini), use claude-council to:
1. Query all three models **in parallel** for healing strategies
2. Compare results **side-by-side** with vendor-colored responses
3. Run each model's approach through the WCAG validator
4. Generate ensemble consensus with per-model strengths/weaknesses
5. Select optimal approach or hybrid strategy

---

## Phase 2C-3 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2C-3: COUNCIL-POWERED MULTI-MODEL TESTING            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. PREPARE COUNCIL                                          │
│    ├─ Copy council plugin to brain-training/council/       │
│    ├─ Configure API keys (OPENAI, GEMINI, XAI, etc.)      │
│    └─ Verify all three providers available                │
│         ├─ Claude 3.5 Sonnet (OpenAI API)                 │
│         ├─ GPT-4V (OpenAI API)                            │
│         └─ Gemini 1.5 Pro (Gemini API)                    │
│         ↓                                                   │
│ 2. GENERATE HEALING STRATEGY PROMPTS                        │
│    ├─ Per-fixture analysis (9 fixtures, 346 violations)    │
│    ├─ Model-specific constraints:                          │
│    │  - Claude: "Hierarchy & structure expertise"          │
│    │  - GPT-4V: "Vision + OCR for scanned images"         │
│    │  - Gemini: "Multi-page reasoning & context"          │
│    └─ Query council for strategies                        │
│         ↓                                                   │
│ 3. RUN COUNCIL QUERIES (Parallel)                          │
│    └─ council-heal-query.sh per fixture:                   │
│         ├─ Claude strategy ────┐                           │
│         ├─ GPT-4V strategy    ─┼─→ Side-by-side output    │
│         └─ Gemini strategy ────┘                           │
│         ↓                                                   │
│ 4. IMPLEMENT MODEL-SPECIFIC HEALERS                        │
│    ├─ claude-healer.py (uses v9 optimized Sonnet prompt)  │
│    ├─ gpt4v-healer.py (vision + healing strategy)         │
│    └─ gemini-healer.py (multi-page + healing strategy)    │
│         ↓                                                   │
│ 5. VALIDATE WITH WCAG                                      │
│    ├─ Run each model's healing output through validator    │
│    ├─ Generate per-fixture metrics:                        │
│    │  ├─ Claude: {violations_fixed_pct, per_type}         │
│    │  ├─ GPT-4V: {violations_fixed_pct, per_type}         │
│    │  └─ Gemini: {violations_fixed_pct, per_type}         │
│    └─ Aggregate to council-analysis-results.json           │
│         ↓                                                   │
│ 6. ENSEMBLE ANALYSIS                                       │
│    ├─ Consensus: Models agree on fixture X approach       │
│    ├─ Divergence: Model Y excels at fixture type Z        │
│    ├─ Hybrid: Best combo = Claude + GPT-4V for fixtures   │
│    └─ Recommendation: Select or blend top approach         │
│         ↓                                                   │
│ 7. GENERATE ENSEMBLE REPORT                                │
│    ├─ council-healing-report.json                          │
│    │  └─ {fixture, model, violations_fixed%, strategy}    │
│    ├─ PHASE_2C3_RESULTS.md                                 │
│    │  └─ Narrative: which model won, why, recommendations  │
│    └─ Update PHASE_2_STATUS.md                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Fixture-Model Mapping (Strengths)

| Fixture | Violations | Claude | GPT-4V | Gemini | Target |
|---------|-----------|--------|--------|--------|--------|
| 001-simple-text | 5 | ✅ structure | ✅ all | ✅ quick | 80%+ |
| 002-complex-table | 5 | ✅ hierarchy | ✅ headers | ⚠️ scope | 70%+ |
| 003-scanned-image | 94 | ⚠️ OCR | **✅ vision** | ⚠️ OCR | 40%+ |
| 004-form-with-fields | 3 | ✅ labels | ✅ all | ✅ all | 100% |
| 005-multi-column | 7 | ✅ layout | ✅ all | ✅ all | 80%+ |
| 006-images-with-captions | 12 | ⚠️ captions | **✅ alt-text** | ⚠️ captions | 60%+ |
| 007-nested-lists | 56 | **✅ hierarchy** | ✅ roles | ✅ roles | 50%+ |
| 008-mixed-content | 139 | ✅ structure | ✅ all | **✅ multi-page** | 40%+ |
| 009-edge-cases | 25 | ✅ ARIA | ✅ all | ✅ all | 60%+ |

---

## Expected Results

### Conservative Estimate
- **Claude:** 30-40% healing (hierarchy + structure strength)
- **GPT-4V:** 35-45% healing (vision + OCR specialty)
- **Gemini:** 25-35% healing (multi-page reasoning)
- **Ensemble:** 40-50% healing (hybrid best-of-breed)

### Optimistic (If Council Consensus Strong)
- All three aligned on approach → 45-55% healing
- Model-specific fixture assignment → 55%+ healing
- Best single model reaches 45%+ → Ship that

---

## Files to Generate

### Council Queries
```
brain-training/
├── council-queries/
│   ├── 001-simple-text-strategy.md      # Council response
│   ├── 002-complex-table-strategy.md    # Side-by-side comparison
│   ├── 003-scanned-image-strategy.md    # Vision specialty
│   └── ...9 total
```

### Healing Output (Per Model)
```
├── healed-claude-3.5-sonnet/
│   ├── 001-simple-text.html
│   ├── 002-complex-table.html
│   └── ... 9 fixtures
├── healed-gpt4v/
│   └── ... 9 fixtures
└── healed-gemini-1.5-pro/
    └── ... 9 fixtures
```

### Results
```
├── council-analysis-results.json        # Raw metrics per model/fixture
├── council-healing-report.json          # Structured results
├── PHASE_2C3_RESULTS.md                 # Narrative analysis
└── council-ensemble-recommendation.md   # Final recommendation
```

---

## API Keys Required

```bash
export OPENAI_API_KEY="..."         # Claude 3.5 Sonnet (via OpenAI)
export GEMINI_API_KEY="..."         # Gemini 1.5 Pro
# Optional: GPT-4V is accessible via OPENAI_API_KEY with gpt-4-vision
```

---

## Implementation Steps

### Step 1: Setup Council Infrastructure
```bash
# Copy council to brain-training directory
cp -r /sessions/zen-eloquent-fermat/mnt/council \
      ~/GABAnode-Portfolio/.../brain-training/council

# Verify providers
cd brain-training/council
bash scripts/query-council.sh --list-default
```

### Step 2: Create Fixture-Specific Prompts
For each fixture, create a council query that asks:
- "Given this fixture with X violations, what's your healing strategy?"
- Model-specific guidance (e.g., "you're strong at vision tasks" for GPT-4V)

### Step 3: Run Council Queries
```bash
# For each fixture, query council for healing strategies
for fixture in 001 002 003 004 005 006 007 008 009; do
    bash scripts/council-query-fixture.sh $fixture
done
```

### Step 4: Generate Model-Specific Healers
Create three healing scripts that implement each model's council-recommended strategy:
- `claude-healer.py` — Uses Claude's recommended approach
- `gpt4v-healer.py` — Uses GPT-4V's vision-based approach
- `gemini-healer.py` — Uses Gemini's multi-page approach

### Step 5: Run All Models
```bash
# Execute healing with each model
python3 claude-healer.py
python3 gpt4v-healer.py
python3 gemini-healer.py
```

### Step 6: WCAG Validation & Comparison
```bash
python3 council-validate-all-models.py
# Outputs: council-analysis-results.json
```

### Step 7: Generate Report
```bash
python3 council-generate-report.py
# Outputs: council-healing-report.json + PHASE_2C3_RESULTS.md
```

---

## Success Criteria

- ✅ All three models respond with strategies (council queries succeed)
- ✅ Healing runs execute for all 3 models × 9 fixtures (27 API calls)
- ✅ WCAG validation completes with real metrics
- ✅ At least one model reaches 40%+ healing target
- ✅ Ensemble approach identified (best hybrid strategy)
- ✅ Recommendation report generated

---

## Integration with Self-Training Loop

Once Phase 2C-3 completes:
1. Update self-training loop to use optimal Phase 2C-3 variant
2. If ensemble hybrid wins, create `v10-council-optimized.js` healing prompt
3. Feed back into Phase 2C-1 loop for further refinement
4. Continue iterating until plateau or target reached

---

## Timeline

- **Step 1-2:** Setup + prompt creation (30 min)
- **Step 3:** Council queries (10 min, parallel)
- **Step 4:** Implement model-specific healers (1 hour)
- **Step 5-6:** Run models + validation (15-20 min per model × 3 = 45-60 min)
- **Step 7:** Report generation (10 min)

**Total estimated runtime:** 2.5-3 hours

---

## Risk Mitigation

- **API rate limits:** Stagger requests, implement retry logic
- **Vision model cost:** GPT-4V is more expensive; validate early on subset
- **Council availability:** Fallback to sequential if council fails
- **WCAG validation:** Have backup validator ready

---

**Status:** Ready to implement  
**Owner:** Jeff / Brain Training Team  
**Next:** Copy council, create prompts, run Phase 2C-3

