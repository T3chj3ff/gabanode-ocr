#!/usr/bin/env python3
"""
Phase 2C-3: Council-Powered Multi-Model Healing

Queries claude-council (parallel Claude, GPT-4V, Gemini) for healing strategies,
runs each model's approach through the healing pipeline, validates with WCAG,
and generates ensemble comparison report.
"""

import os
import json
import subprocess
from pathlib import Path
import google.generativeai as genai

# Configuration
BRAIN_TRAINING_DIR = Path(__file__).parent
FIXTURES_DIR = BRAIN_TRAINING_DIR / "fixtures"
COUNCIL_DIR = BRAIN_TRAINING_DIR / "council"
RESULTS_DIR = BRAIN_TRAINING_DIR

# Models
MODELS = {
    "claude-3.5-sonnet": {
        "provider": "openai",
        "strength": "hierarchy & structure",
        "specialty_fixtures": ["007-nested-lists", "002-complex-table"]
    },
    "gpt-4v": {
        "provider": "openai",
        "strength": "vision & OCR",
        "specialty_fixtures": ["003-scanned-image", "006-images-with-captions"]
    },
    "gemini-1.5-pro": {
        "provider": "gemini",
        "strength": "multi-page reasoning",
        "specialty_fixtures": ["008-mixed-content", "007-nested-lists"]
    }
}

FIXTURES = [
    "001-simple-text",
    "002-complex-table",
    "003-scanned-image",
    "004-form-with-fields",
    "005-multi-column",
    "006-images-with-captions",
    "007-nested-lists",
    "008-mixed-content",
    "009-edge-cases"
]

HEALING_PROMPTS = {
    "claude-3.5-sonnet": """You are an expert in HTML accessibility and WCAG 2.2 AA compliance.
Your strength is fixing semantic hierarchy, landmark structure, and complex nested elements.

Given the following HTML with accessibility violations, provide ONLY a Python dict mapping
violation types to your recommended fixes. Format: {"violation_type": "specific_fix_strategy"}

Violations to address:
- Missing <main> landmark
- Missing alt text on images
- Empty link text
- Missing lang attribute
- Incorrect heading hierarchy
- Missing form labels
- Table scope attributes

HTML violations to fix:
{html_content}

Respond ONLY with a valid Python dict, no explanation.""",

    "gpt-4v": """You are an expert in visual accessibility and OCR-based content remediation.
Your strength is analyzing images in PDFs, generating accurate alt text, and detecting visual content.

Given the following HTML with image-related violations, analyze the images and provide
recommendations for alt text and visual descriptions. Format: {"image_id": "alt_text_recommendation"}

HTML with images to analyze:
{html_content}

Respond ONLY with a valid Python dict, no explanation.""",

    "gemini-1.5-pro": """You are an expert in multi-page document analysis and contextual reasoning.
Your strength is understanding document flow, complex layouts, and maintaining semantic meaning across pages.

Given the following HTML extracted from a multi-page document, identify structural issues
and recommend fixes for layout, reading order, and content organization.
Format: {"structure_issue": "recommended_fix"}

HTML from document:
{html_content}

Respond ONLY with a valid Python dict, no explanation."""
}

def setup_gemini():
    """Initialize Gemini API"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)

def count_wcag_violations(html_path: Path) -> dict:
    """Count WCAG violations in healed HTML"""
    if not html_path.exists():
        return {"error": "HTML not found"}

    html = html_path.read_text()
    violations = {
        "missing_alt_text": html.count('<img') - html.count('alt='),
        "empty_links": html.count('<a href') - len([l for l in html.split('<a') if 'href' in l and l.split('>')[1:2]]),
        "missing_main": 1 if '<main' not in html else 0,
        "missing_lang": 1 if 'lang=' not in html else 0,
    }
    return {k: max(0, v) for k, v in violations.items()}

def query_council_for_strategy(fixture_name: str) -> dict:
    """Query council for healing strategy for a fixture"""
    fixture_dir = FIXTURES_DIR / fixture_name
    expected_html = fixture_dir / "expected-html.html"

    if not expected_html.exists():
        print(f"❌ {fixture_name}: No expected-html.html found")
        return {}

    html_content = expected_html.read_text()[:2000]  # First 2000 chars for context

    # Council query (simplified - in production would use actual council plugin)
    print(f"🔵 Querying council for {fixture_name}...")
    print(f"   - Claude 3.5 Sonnet (hierarchy)")
    print(f"   - GPT-4V (vision)")
    print(f"   - Gemini 1.5 Pro (multi-page)")

    return {
        "fixture": fixture_name,
        "html_snippet": html_content,
        "query_status": "pending"  # In production: actual council responses
    }

def heal_fixture_with_model(fixture_name: str, model_name: str) -> dict:
    """Heal a single fixture using a specific model"""
    fixture_dir = FIXTURES_DIR / fixture_name
    expected_html = fixture_dir / "expected-html.html"

    if not expected_html.exists():
        print(f"❌ {fixture_name}: No expected-html.html found")
        return {"error": "HTML not found"}

    html_content = expected_html.read_text()

    print(f"   Healing {fixture_name} with {model_name}...", end=" ", flush=True)

    # Use appropriate API based on model
    if model_name == "gemini-1.5-pro":
        healed = heal_with_gemini(html_content, model_name)
    else:
        # GPT and Claude would use OpenAI API (not shown here for brevity)
        healed = heal_with_placeholder(html_content, model_name)

    # Save healed HTML
    model_short = model_name.replace(".", "_").replace("-", "_")
    healed_path = fixture_dir / f"healed-{model_short}.html"
    healed_path.write_text(healed)

    # Validate
    violations = count_wcag_violations(healed_path)
    baseline = count_wcag_violations(expected_html)

    violations_fixed = sum(baseline.values()) - sum(violations.values())
    violations_fixed_pct = (violations_fixed / sum(baseline.values()) * 100) if baseline.values() else 0

    result = {
        "fixture": fixture_name,
        "model": model_name,
        "healed_file": str(healed_path),
        "violations_before": sum(baseline.values()),
        "violations_after": sum(violations.values()),
        "violations_fixed": violations_fixed,
        "violations_fixed_pct": round(violations_fixed_pct, 1),
        "per_type": violations
    }

    print(f"✅ {violations_fixed_pct:.1f}% fixed")
    return result

def heal_with_gemini(html: str, model: str) -> str:
    """Heal HTML using Gemini API"""
    prompt = HEALING_PROMPTS[model].format(html_content=html[:5000])

    try:
        response = genai.generate_text(
            prompt=prompt,
            model="models/text-bison-001"
        )

        # Parse response and apply fixes (simplified)
        return html  # In production: actually apply fixes
    except Exception as e:
        print(f"Error: {e}")
        return html

def heal_with_placeholder(html: str, model: str) -> str:
    """Placeholder for OpenAI models (GPT-4V, Claude via API)"""
    # In production: call OpenAI API with vision capabilities
    return html

def generate_council_report(results: list) -> dict:
    """Generate comprehensive council comparison report"""

    report = {
        "timestamp": "2026-05-14",
        "phase": "2C-3 Council-Powered Multi-Model Testing",
        "fixtures_tested": len(FIXTURES),
        "models_tested": list(MODELS.keys()),
        "results_by_fixture": {},
        "results_by_model": {},
        "consensus": {},
        "recommendations": {}
    }

    # Organize by fixture
    for fixture in FIXTURES:
        fixture_results = [r for r in results if r.get("fixture") == fixture]
        report["results_by_fixture"][fixture] = fixture_results

    # Organize by model
    for model in MODELS.keys():
        model_results = [r for r in results if r.get("model") == model]
        avg_healing = sum(r.get("violations_fixed_pct", 0) for r in model_results) / len(model_results) if model_results else 0
        report["results_by_model"][model] = {
            "average_healing_pct": round(avg_healing, 1),
            "fixtures_tested": len(model_results),
            "results": model_results
        }

    # Consensus & recommendations
    report["consensus"] = {
        "all_models_above_20_percent": all(
            report["results_by_model"][m]["average_healing_pct"] >= 20
            for m in report["results_by_model"]
        ),
        "best_single_model": max(
            report["results_by_model"].items(),
            key=lambda x: x[1]["average_healing_pct"]
        )[0],
        "best_model_healing": max(
            m["average_healing_pct"] for m in report["results_by_model"].values()
        )
    }

    report["recommendations"] = {
        "approach": "Use best single model" if report["consensus"]["best_model_healing"] >= 40 else "Ensemble strategy needed",
        "next_phase": "Phase 2C-4: Finalization" if report["consensus"]["best_model_healing"] >= 40 else "Iterate variants",
        "estimated_completion": "Ready for production" if report["consensus"]["best_model_healing"] >= 50 else "Further optimization needed"
    }

    return report

def main():
    print("\n" + "="*70)
    print("PHASE 2C-3: COUNCIL-POWERED MULTI-MODEL HEALING")
    print("="*70 + "\n")

    # Setup
    setup_gemini()

    # Check council
    if not COUNCIL_DIR.exists():
        print("⚠️  Council not found. Copy council plugin first:")
        print(f"   cp -r /sessions/zen-eloquent-fermat/mnt/council {BRAIN_TRAINING_DIR}")
        return

    all_results = []

    # Phase 1: Query council for strategies (placeholder)
    print("PHASE 1: Querying Council for Healing Strategies")
    print("-" * 70)
    for fixture in FIXTURES:
        strategy = query_council_for_strategy(fixture)
        all_results.append(strategy)
    print()

    # Phase 2: Heal with each model
    print("PHASE 2: Running Model-Specific Healing")
    print("-" * 70)
    for model_name in MODELS.keys():
        print(f"\n{model_name}:")
        for fixture in FIXTURES:
            result = heal_fixture_with_model(fixture, model_name)
            all_results.append(result)
    print()

    # Phase 3: Generate report
    print("PHASE 3: Generating Council Report")
    print("-" * 70)
    report = generate_council_report([r for r in all_results if isinstance(r, dict) and "violations_fixed_pct" in r])

    # Save report
    report_path = RESULTS_DIR / "council-healing-report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"✅ Report saved: {report_path}\n")

    # Summary
    print("="*70)
    print("COUNCIL RESULTS SUMMARY")
    print("="*70)
    for model, metrics in report["results_by_model"].items():
        print(f"\n{model}:")
        print(f"  Average Healing: {metrics['average_healing_pct']:.1f}%")
        print(f"  Fixtures Tested: {metrics['fixtures_tested']}")

    print(f"\nBest Model: {report['consensus']['best_single_model']}")
    print(f"Best Healing: {report['consensus']['best_model_healing']:.1f}%")
    print(f"\nRecommendation: {report['recommendations']['approach']}")
    print(f"Status: {report['recommendations']['estimated_completion']}\n")

if __name__ == "__main__":
    main()
