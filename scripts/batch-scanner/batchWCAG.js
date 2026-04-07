const fs = require('fs/promises');
const path = require('path');

const INPUT_DIR = path.join(__dirname, 'input_pdfs');
const OUTPUT_DIR = path.join(__dirname, 'output_md');

async function getApiKey() {
  try {
    const env = await fs.readFile(path.join(__dirname, '.env.local'), 'utf-8');
    const match = env.match(/GOOGLE_API_KEY=(.+)/);
    return match ? match[1].trim() : null;
  } catch (e) {
    return null;
  }
}

async function processDocument(filePath, apiKey) {
  const ext = path.extname(filePath).toLowerCase();
  let mimeType = 'application/pdf';
  if (ext === '.png') mimeType = 'image/png';
  if (ext === '.jpg' || ext === '.jpeg') mimeType = 'image/jpeg';
  
  const fileData = await fs.readFile(filePath);
  const base64Data = fileData.toString('base64');
  
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{
          parts: [
            { text: "Extract all text, structure, tables, and formulas from this document. Format them natively to strictly comply with WCAG 2.2 AA standards (semantic headers, proper lists, and markdown tables). Output the result in pure Markdown." },
            { inlineData: { mimeType: mimeType, data: base64Data } }
          ]
      }]
    }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || 'Cognitive Engine request failed');
  if (data.promptFeedback?.blockReason) throw new Error(`Blocked by safety filters: ${data.promptFeedback.blockReason}`);
  
  return data.candidates?.[0]?.content?.parts?.[0]?.text;
}

async function startBatch() {
  console.log("🛡️ Starting GABAnode Labs Batch WCAG Scanning...");
  
  await fs.mkdir(INPUT_DIR, { recursive: true });
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const apiKey = await getApiKey();
  if (!apiKey) {
    console.error("❌ Error: GOOGLE_API_KEY not found in .env.local");
    process.exit(1);
  }

  const files = await fs.readdir(INPUT_DIR);
  const targetFiles = files.filter(f => ['.pdf', '.png', '.jpg', '.jpeg'].includes(path.extname(f).toLowerCase()));

  if (targetFiles.length === 0) {
    console.log(`\n⚠️ No files found! Please drop your raw PDFs into: ${INPUT_DIR}`);
    return;
  }

  console.log(`\nFound ${targetFiles.length} files. Initiating OCR Processing...\n`);

  for (const file of targetFiles) {
    console.log(`Processing [${file}]...`);
    const filePath = path.join(INPUT_DIR, file);
    try {
      const extractedText = await processDocument(filePath, apiKey);
      if (extractedText) {
        const outName = file.replace(path.extname(file), '_remediated.md');
        await fs.writeFile(path.join(OUTPUT_DIR, outName), extractedText);
        console.log(`✅ Success! Wrote output to -> output_md/${outName}`);
      } else {
        console.log(`❌ Failed: AI could not extract content.`);
      }
    } catch (err) {
      console.log(`❌ Error processing [${file}]: ${err.message}`);
    }
  }
  
  console.log("\n🏁 Batch Processing Complete!");
}

startBatch().catch(console.error);
