# Fixture 002: Complex Table

**Purpose:** Test table extraction with merged cells, headers, and financial data.

**Document Type:** Financial report with 1-2 pages, complex tables with merged cells, headers, footers, multiple data rows.

**Expected Complexity:** Medium (85%+ target)

**Files in this fixture:**
- `source.pdf` — Original PDF file with complex tables
- `source-metadata.json` — Document metadata
- `expected-md.md` — Ground-truth Markdown (table syntax)
- `expected-html.html` — Target healed HTML
- `expected-score.json` — Target accuracy scores

**Test Scenarios:**
1. Table with merged cells (Markdown doesn't support merged cells, so expect note)
2. Multi-row headers
3. Numeric precision (preserve all digits)
4. Column alignment
5. Table footnotes

**Challenges:**
- Markdown tables don't support merged cells—expect extraction to flatten or note limitation
- Healing may require adding ARIA for table headers

**Acceptance Criteria:**
- Extraction: ≥85% (tables are harder)
- Healing: ≥80%
- Combined: ≥82%

---

## Notes

Tables with merged cells are a known limitation. The brain should:
1. Flatten the merged cell into the cells it spans, OR
2. Add a note: [TABLE NOTE: Original had merged cells]

Either approach is acceptable as long as the data is preserved.

