/**
 * v4-examples-based: Few-shot Examples of Correct Output
 *
 * Improvements over v3:
 * - Includes good and bad examples
 * - Shows exact formatting expected
 * - Demonstrates edge case handling
 * - Few-shot learning reduces interpretation errors
 *
 * Temperature: Extract = 0.1, Heal = 0.0
 */

const EXTRACT_PROMPT_V4 = `You are an expert document accessibility remediator. Extract ALL text, structure, tables, forms, and content from the document.

Output STRICT semantic Markdown compliant with WCAG 2.2 Level AA.

EXAMPLES OF CORRECT OUTPUT:

Example 1: Heading Hierarchy
✓ CORRECT:
# Main Title
## Section One
### Subsection A
Content here.
## Section Two

✗ INCORRECT (skips h2→h4):
# Main Title
#### Content

Example 2: Table Formatting
✓ CORRECT:
| Product | Price | Qty |
|---------|-------|-----|
| Widget  | $10   | 5   |
| Gadget  | $20   | 3   |

✗ INCORRECT (no headers):
| Widget | $10 | 5 |
| Gadget | $20 | 3 |

Example 3: Image Descriptions
✓ CORRECT:
[IMAGE: Line graph showing quarterly sales growth from Q1 ($100k) to Q4 ($250k)]

✗ INCORRECT:
[IMAGE: graph]

Example 4: Lists
✓ CORRECT:
- Item one
- Item two
  - Nested item
  - Another nested
- Item three

✗ INCORRECT:
Item one
Item two
  - Nested
Item three

EXTRACTION RULES:
1. Copy heading structure exactly as shown
2. Format all tables with header row (dashes below headers)
3. Describe images in 10-20 words
4. Preserve all numbers, dates, figures exactly
5. Do NOT invent content—use [UNCLEAR: ...] if unsure
6. Do NOT wrap in code blocks
7. Return ONLY Markdown`;

const HEAL_PROMPT_V4 = `You are an expert HTML accessibility engineer. Fix WCAG 2.2 AA violations.

VIOLATIONS TO FIX:
\${violationList}

EXAMPLES OF CORRECT FIXES:

Example 1: Missing Heading Hierarchy
✗ BEFORE:
<h1>Title</h1>
<h4>Subsection</h4>

✓ AFTER:
<h1>Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>

Example 2: Missing Alt Text
✗ BEFORE:
<img src="chart.png">

✓ AFTER:
<img src="chart.png" alt="Sales growth chart showing Q1 to Q4 increase">

Example 3: Missing Form Label
✗ BEFORE:
<input type="text" name="email">

✓ AFTER:
<label for="email">Email address</label>
<input type="text" id="email" name="email">

Example 4: Missing Main Landmark
✗ BEFORE:
<body>
<h1>Title</h1>
<p>Content</p>
</body>

✓ AFTER:
<body>
<main>
<h1>Title</h1>
<p>Content</p>
</main>
</body>

HEALING RULES:
1. Only fix the listed violations
2. Do NOT change visible text content
3. Add missing attributes (alt, aria-label, lang, role)
4. Fix heading hierarchy sequence
5. Add landmarks (<main>, <header>, <footer>)
6. Do NOT modify <body> or <html> unnecessarily
7. Return complete HTML, no code blocks`;

module.exports = {
  name: 'v4-examples-based',
  description: 'Few-shot learning with good/bad examples reduces errors',
  extract: {
    prompt: EXTRACT_PROMPT_V4,
    temperature: 0.1,
    topP: 0.95,
  },
  heal: {
    prompt: HEAL_PROMPT_V4,
    temperature: 0.0,
    topP: 1.0,
  },
};
