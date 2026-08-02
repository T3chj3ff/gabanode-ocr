> [!WARNING]
> **Migration and security remediation complete; this repository is retired.**
> [`T3chj3ff/project-euclid`](https://github.com/T3chj3ff/project-euclid) is the
> canonical destination. No code, corpus, prompt, generated result, benchmark,
> or compliance claim from this repository was migrated. PR #1 removed the
> committed Gemini credential from the current tree. On 2026-08-02, Google
> rejected the historical key as reported leaked, and every advertised branch
> and tag was rewritten to replace the key material. Old clones must be
> discarded rather than pushed. Do not deploy this repository or treat
> historical claims below as accessibility or conformance evidence.

# 🛡️ GABAnode Labs: Core Document Accessibility Engine

Welcome to the internal source for the GABAnode Labs Document Accessibility Engine. This repository dictates the processing of intractable documents (PDFs, images) into strict WCAG 2.2 Level AA semantic Markdown structures.

## 🗂️ Lab Repository Structure

This repository is organized as a unified engineering lab, containing the standalone Vercel portal, integration packages, and batch-processing scripts:

```text
gabanode-document-engine/
├── app/                     # 🌐 The Core Web Engine
│                            # Next.js App Router for the drag-drop portal
│                            # /api/ocr/route.js handles Vercel Serverless cognitive routing.
├── packages/                # 📦 External Consumer Integrations
│   └── idioma-integration/  # Drop-in hooks & React components to link Idioma Chat to this Engine.
├── scripts/                 # ⚙️ Automation & Tooling
│   └── batch-scanner/       # Node.js processor for massive, headless directory sweeps.
└── .env.local               # (Git Ignored) Stores Google Gemini cognitive keys.
```

## 🚀 1. The Core Web Engine (Next.js)
The root of this project is a robust, production-ready Vercel application.
* **To run locally:** `npm run dev`
* **To deploy:** Push to Vercel (zero-config). Ensure `GOOGLE_API_KEY` is present in your environment parameters.

## 🧩 2. Implementing into Idioma Chat
If you are moving this technology into your primary desktop application (Idioma Chat), see the documentation inside `packages/idioma-integration/README.md`. It provides the exact backend modifications and frontend React hooks needed for seamless integration.

## 🛡️ 3. Running Batch CI/CD Scans
For automated processing of existing un-remediated PDFs, use our batch script:
```bash
cd scripts/batch-scanner
node batchWCAG.js
```
*Drop input PDFs into `input_pdfs/` and retrieve structured markdown in `output_md/`.*
