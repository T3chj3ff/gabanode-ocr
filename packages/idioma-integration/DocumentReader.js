"use client";
import { useState } from 'react';

// Drop this component directly into your Idioma Chat input bar area
export default function DocumentTranslationUploader({ onDocumentParsed }) {
  const [loading, setLoading] = useState(false);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 15 * 1024 * 1024) {
      alert("File is too large for serverless translation. Max 15MB.");
      return;
    }

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const fileContent = e.target.result;
        
        // Calls the new backend route you copied into Idioma
        const response = await fetch('/api/document-reader', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fileContent }),
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        // Pass the deeply structured Markdown up to Idioma's chat context!
        onDocumentParsed(data.md_results);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error("Translation upload failed:", err);
      alert("Document read failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="idioma-document-upload">
      <label style={{ cursor: loading ? 'not-allowed' : 'pointer', color: '#58a6ff' }}>
        {loading ? "Reading Foreign Formatting..." : "📎 Upload Foreign Document (PDF)"}
        <input 
          type="file" 
          hidden 
          accept="application/pdf, image/*" 
          onChange={handleUpload}
          disabled={loading}
        />
      </label>
    </div>
  );
}
