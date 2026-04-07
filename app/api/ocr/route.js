import { NextResponse } from 'next/server';

// Max limits for Vercel Hobby/Pro. Ensure the function doesn't timeout while the AI is analyzing dense PDFs.
export const maxDuration = 60; 

// Note: Vercel standard serverless payload constraints apply to App Router endpoints (4.5MB).
// For files larger than 4.5MB on production Vercel, client-side pre-signed URLs should be implemented.

export async function POST(req) {
  try {
    const { fileContent } = await req.json();

    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: 'System Configuration Error: GOOGLE_API_KEY is not defined.' }, { status: 500 });
    }

    const match = fileContent.match(/^data:(.+);base64,(.*)$/);
    if (!match) {
      return NextResponse.json({ error: 'Invalid document format. Please upload a standard PDF or Image.' }, { status: 400 });
    }

    const mimeType = match[1];
    const base64Data = match[2];

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: "Extract all text, structure, tables, and formulas from this document. Output the result in pure Markdown format. If you see tables, format them as markdown tables. Do not wrap everything in a master markdown code block, just return the raw text." },
              {
                inlineData: {
                 mimeType: mimeType,
                 data: base64Data
                }
              }
            ]
          }
        ]
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
        return NextResponse.json({ error: data.error?.message || 'Cognitive Engine request failed' }, { status: response.status });
    }

    // Handle Safety/Block restrictions built into the model
    if (data.promptFeedback?.blockReason) {
         return NextResponse.json({ error: `Document blocked by safety filters: ${data.promptFeedback.blockReason}` }, { status: 403 });
    }

    const extractedText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!extractedText) {
        return NextResponse.json({ error: 'The AI model could not extract any legible content from this document.' }, { status: 422 });
    }

    return NextResponse.json({ md_results: extractedText });
  } catch (error) {
    if (error.message.includes('body size')) {
         return NextResponse.json({ error: 'The document is too large for the current serverless environment payload limits.' }, { status: 413 });
    }
    return NextResponse.json({ error: `Internal Engine Error: ${error.message}` }, { status: 500 });
  }
}
