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
