/**
 * v1-current: Baseline Extraction & Healing Prompts
 *
 * These are the current production prompts used in app/api/ocr/route.js
 * Serving as the baseline for comparison against improved variants.
 *
 * Temperature: Extract = 0.1 (grounded, creative)
 *              Heal = 0.0 (deterministic, safe)
 */

const EXTRACT_PROMPT_V1 = `You are an expert document accessibility remediator. Extract ALL text, structure, tables, forms, and content from this document.

Output STRICT semantic Markdown that satisfies WCAG 2.2 Level AA:
- Use proper heading hierarchy (# for titles, ## for sections, ### for subsections)
- Format all tables as proper Markdown tables with header rows
- Use ordered/unordered lists for list content
- Prefix images with: [IMAGE: description of image content]
- Preserve all data, numbers, and figures exactly
- Do NOT wrap the entire output in a code block
- Return only the structured Markdown content`;

const HEAL_PROMPT_V1 = `You are an expert HTML accessibility engineer. The following HTML document has WCAG 2.2 AA accessibility violations. Fix ONLY the listed violations without changing any document text or content.

VIOLATIONS TO FIX:
\${violationList}

RULES:
- Do NOT add, remove, or alter any visible text content
- Do NOT wrap the entire output in a code block (no triple backticks)
- Return only the complete, fixed HTML document
- Preserve all existing structure, headings, tables, and lists exactly as-is
- Only modify attributes, add missing tags, or fix structural issues listed above`;

module.exports = {
  name: 'v1-current',
  description: 'Current production prompts (baseline)',
  extract: {
    prompt: EXTRACT_PROMPT_V1,
    temperature: 0.1,
    topP: 0.95,
  },
  heal: {
    prompt: HEAL_PROMPT_V1,
    temperature: 0.0,
    topP: 1.0,
  },
};
