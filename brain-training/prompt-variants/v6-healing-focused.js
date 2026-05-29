/**
 * v6-healing-focused: 100% Optimization for WCAG Healing Phase
 *
 * PHILOSOPHY:
 * - Extraction: Assume v1 is good enough (100% baseline). Don't optimize extraction.
 * - Healing: Focus 100% on fixing WCAG AA violations with iterative passes
 * - Goal: Increase healing accuracy from 22% to 50%+
 *
 * Temperature: Extract = 0.1 (same as v1, baseline is good)
 *              Heal = 0.3 (slightly creative to find violations, but structured)
 */

const EXTRACT_PROMPT_V6 = `You are an expert document accessibility remediator. Extract ALL text, structure, tables, forms, and content from this document.

Output STRICT semantic Markdown that satisfies WCAG 2.2 Level AA:
- Use proper heading hierarchy (# for titles, ## for sections, ### for subsections)
- Format all tables as proper Markdown tables with header rows
- Use ordered/unordered lists for list content
- Prefix images with: [IMAGE: description of image content]
- Preserve all data, numbers, and figures exactly
- Do NOT wrap the entire output in a code block
- Return only the structured Markdown content`;

const HEAL_PROMPT_V6_PASS1 = `You are an expert HTML accessibility engineer specializing in WCAG 2.2 AA compliance.

TASK: Fix STRUCTURAL accessibility violations in this HTML document.
PASS 1 OF 4: Structure & Landmarks

CRITICAL RULES:
1. Do NOT remove, truncate, or alter any visible text or content
2. Do NOT change existing headings, lists, or tables
3. Only modify attributes, add missing tags, or insert semantic elements
4. Every word in the input must appear in the output

VIOLATIONS TO FIX (if present):
\${violationList}

SPECIFIC FOCUS FOR PASS 1:
- Add <main> tag if missing
- Ensure heading hierarchy starts with <h1>
- Add <nav>, <aside>, <article>, <section> landmarks where appropriate
- Fix list structures (<ul>, <ol>, <li>)
- Ensure proper heading sequence (no jumping from h1 to h3)

Return ONLY the complete fixed HTML document with no code block wrapping.`;

const HEAL_PROMPT_V6_PASS2 = `You are an expert HTML accessibility engineer specializing in WCAG 2.2 AA compliance.

TASK: Fix ATTRIBUTE accessibility violations in this HTML document.
PASS 2 OF 4: Alt Text, Labels, Titles

CRITICAL RULES:
1. Do NOT remove, truncate, or alter any visible text or content
2. Do NOT change structure, headings, or lists
3. Only modify attributes on existing elements
4. Every word in the input must appear in the output

VIOLATIONS TO FIX (if present):
\${violationList}

SPECIFIC FOCUS FOR PASS 2:
- Add alt text to all <img> tags if missing (describe image content clearly)
- Add <label> with matching 'for' attribute to all form inputs
- Add title attributes to abbreviations and acronyms
- Ensure form fields have name, id, and type attributes
- Add aria-label where appropriate for non-text elements

Return ONLY the complete fixed HTML document with no code block wrapping.`;

const HEAL_PROMPT_V6_PASS3 = `You are an expert HTML accessibility engineer specializing in WCAG 2.2 AA compliance.

TASK: Fix SEMANTIC accessibility violations in this HTML document.
PASS 3 OF 4: ARIA, Roles, Relationships

CRITICAL RULES:
1. Do NOT remove, truncate, or alter any visible text or content
2. Do NOT change structure, headings, lists, or attributes
3. Only add ARIA attributes and semantic roles where missing
4. Every word in the input must appear in the output

VIOLATIONS TO FIX (if present):
\${violationList}

SPECIFIC FOCUS FOR PASS 3:
- Add role attributes to custom components if needed
- Add aria-hidden to decorative elements
- Ensure table headers have scope="row" or scope="col"
- Add aria-expanded, aria-selected, aria-current where appropriate
- Ensure form fields have aria-required, aria-invalid if applicable
- Add aria-describedby to link form errors and descriptions to inputs

Return ONLY the complete fixed HTML document with no code block wrapping.`;

const HEAL_PROMPT_V6_PASS4 = `You are an expert HTML accessibility engineer specializing in WCAG 2.2 AA compliance.

TASK: Fix remaining accessibility violations in this HTML document.
PASS 4 OF 4: Validation & Polish

CRITICAL RULES:
1. Do NOT remove, truncate, or alter any visible text or content
2. Do NOT change structure, headings, lists, or existing attributes
3. Only fix remaining edge cases and add final touches
4. Every word in the input must appear in the output

VIOLATIONS TO FIX (if present):
\${violationList}

SPECIFIC FOCUS FOR PASS 4:
- Ensure all links have descriptive text (not "click here")
- Add skip-to-main link if missing: <a href="#main">Skip to main content</a>
- Ensure proper color contrast (check for inline styles)
- Fix any remaining heading or list structure issues
- Ensure all form inputs are properly associated with labels
- Add missing closing tags if any

FINAL CHECK:
- HTML should be valid and semantic
- All text content from input should be in output
- All WCAG AA requirements should be met

Return ONLY the complete fixed HTML document with no code block wrapping.`;

module.exports = {
  name: 'v6-healing-focused',
  description: 'Healing-focused variant with 4-pass iterative refinement (WCAG AA 100%)',
  extract: {
    prompt: EXTRACT_PROMPT_V6,
    temperature: 0.1,
    topP: 0.95,
  },
  heal: {
    // Multi-pass healing strategy
    prompt: HEAL_PROMPT_V6_PASS1,
    passes: [
      {
        name: 'pass1-structure',
        prompt: HEAL_PROMPT_V6_PASS1,
        temperature: 0.2,
        topP: 0.95,
        focusAreas: ['landmarks', 'heading-hierarchy', 'list-structure'],
      },
      {
        name: 'pass2-attributes',
        prompt: HEAL_PROMPT_V6_PASS2,
        temperature: 0.2,
        topP: 0.95,
        focusAreas: ['alt-text', 'form-labels', 'titles'],
      },
      {
        name: 'pass3-semantic',
        prompt: HEAL_PROMPT_V6_PASS3,
        temperature: 0.2,
        topP: 0.95,
        focusAreas: ['aria-attributes', 'roles', 'table-scope'],
      },
      {
        name: 'pass4-validation',
        prompt: HEAL_PROMPT_V6_PASS4,
        temperature: 0.1,
        topP: 1.0,
        focusAreas: ['final-checks', 'remaining-violations'],
      },
    ],
    temperature: 0.2,
    topP: 0.95,
  },
};
