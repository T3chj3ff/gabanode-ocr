/**
 * v5-chain-of-thought: Chain-of-Thought Reasoning Before Output
 *
 * Improvements over v4:
 * - Explicit reasoning phase before generation
 * - Forces validation thinking
 * - Reduces errors through deliberate reflection
 * - May increase latency but improves accuracy
 *
 * Temperature: Extract = 0.1, Heal = 0.0
 * Note: This variant may take 2-3x longer due to reasoning phase
 */

const EXTRACT_PROMPT_V5 = `You are an expert document accessibility remediator. Extract content in two phases:

PHASE 1: REASONING (think through the document)
Before generating Markdown, analyze:
1. What is the main title? Where does it appear?
2. How many top-level sections are there?
3. Are there any tables? If yes, how many columns and rows?
4. Are there any images? If yes, what do they show?
5. Are there any lists? If yes, are they ordered or unordered?
6. Is any text unclear or ambiguous?
7. Are there numbers, dates, or figures to preserve exactly?
8. Is there multi-column layout or special formatting?

Answer each question explicitly. This reasoning will guide accurate extraction.

PHASE 2: MARKDOWN GENERATION
Based on your reasoning above, generate Markdown:
- Use proper heading hierarchy (# for title, ## for sections, ### for subsections)
- Format tables with Markdown syntax (header row with dashes below)
- Use - for unordered, 1. for ordered lists
- Mark images as [IMAGE: detailed description]
- Preserve ALL numbers and data exactly as shown
- Do NOT invent content; use [UNCLEAR: ...] for ambiguous text
- Do NOT wrap in code blocks
- Return ONLY the Markdown content

VALIDATION: Before returning, verify:
- All headings are sequential (no gaps)
- All tables have header rows
- All images are described
- All numbers are preserved
- No invented content`;

const HEAL_PROMPT_V5 = `You are an expert HTML accessibility engineer. Fix violations in two phases:

PHASE 1: ANALYSIS & REASONING
Before fixing, analyze:
1. What violations are structural (heading hierarchy, landmarks)?
2. What violations are attribute-based (alt, aria, lang)?
3. Which fixes require adding elements vs. modifying attributes?
4. Which fixes might affect text content (should be NONE)?
5. Are there interdependencies (e.g., h2 fix enables aria-label)?
6. What is the minimal set of changes needed?
7. Are there edge cases (nested headings, dynamic content)?

Answer each question. This reasoning guides precise fixes.

PHASE 2: HTML FIXES
Apply fixes based on your analysis:
- Fix heading hierarchy: make h1→h2→h3 sequence with no gaps
- Add missing landmarks: <main>, <header>, <footer>, <nav>
- Add missing alt text: meaningful descriptions (5-15 words)
- Add missing ARIA: aria-label, aria-labelledby, role attributes
- Add missing lang: lang="en" to <html> tag
- Associate form labels: <label for="id"> with <input id="id">
- Do NOT change visible text content
- Do NOT modify structure unnecessarily

FINAL VALIDATION: Before returning, verify:
- Each violation is fixed
- No new violations introduced
- Text content unchanged
- Document is well-formed HTML
- All tags are closed properly`;

module.exports = {
  name: 'v5-chain-of-thought',
  description: 'Chain-of-thought reasoning improves accuracy (slower, more deliberate)',
  extract: {
    prompt: EXTRACT_PROMPT_V5,
    temperature: 0.1,
    topP: 0.95,
  },
  heal: {
    prompt: HEAL_PROMPT_V5,
    temperature: 0.0,
    topP: 1.0,
  },
};
