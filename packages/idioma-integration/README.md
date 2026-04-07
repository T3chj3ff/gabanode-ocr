# Idioma Chat Integration Protocol

This directory contains the necessary components to inject the Document Accessibility Engine directly into your **Idioma Chat** application on your Desktop (`/Users/foxtrot1/Desktop/languagetranslator`).

## The Strategy
To get Idioma Chat reading giant PDFs natively, you just need to:
1. Copy our stabilized backend API route to Idioma.
2. Drop in the `DocumentReader.js` hook into your main chat interface.

### Step 1: Backend Route
Take the exact `app/api/ocr/route.js` file from this project and copy it directly into your Idioma Chat Next.js routing folder (e.g., `app/api/document-reader/route.js`). Ensure Idioma's Vercel environment has the `GOOGLE_API_KEY`.

### Step 2: The Chat Integration
Use the provided `DocumentReader.js` (in this folder) as a React component inside your Idioma input bar. When a user drags a foreign-language PDF into Idioma:
1. It passes it to the `route.js`.
2. It extracts the raw Markdown.
3. You automatically pipe that raw Markdown into the existing `Translation Context` window of Idioma perfectly formatted!
