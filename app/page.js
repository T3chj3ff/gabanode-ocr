"use client";

import { useState, useRef } from 'react';
import './globals.css';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const processFile = async (file) => {
    // 1. Reset state
    setLoading(true);
    setResult(null);
    setError(null);

    // 2. Client-Side Security/Validation (File Size limits - max 15MB)
    const MAX_FILE_SIZE = 15 * 1024 * 1024; // 15MB
    if (file.size > MAX_FILE_SIZE) {
      setError(`File is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Vercel limits Serverless uploads to 15MB max.`);
      setLoading(false);
      return;
    }

    // 3. Format Validation
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg'];
    if (!validTypes.includes(file.type)) {
      setError(`Unsupported file format (${file.type}). Please use PDF, PNG, or JPG.`);
      setLoading(false);
      return;
    }

    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const fileContent = e.target.result;
        
        try {
          const response = await fetch('/api/ocr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileContent }),
          });
          
          const data = await response.json();
          if (!response.ok) throw new Error(data.error || 'Failed to process document');
          
          setResult(data);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      
      reader.onerror = () => {
        setError("Failed to read the file locally. Please try a different file.");
        setLoading(false);
      };

      reader.readAsDataURL(file);
    } catch (err) {
      setError("An unexpected error occurred during processing.");
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (loading) return;
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!loading) setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const triggerFileInput = () => {
    if (!loading && fileInputRef.current) {
        fileInputRef.current.click();
    }
  };

  const downloadMarkdown = () => {
    if (!result || !result.md_results) return;
    const blob = new Blob([result.md_results], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'gabanode-lab-remediated.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <main role="main" aria-labelledby="main-heading">
      <header className="header">
        <div className="badge">GABAnode Labs • v2.4.1 Production</div>
        <h1 id="main-heading">Document Accessibility Engine</h1>
        <p>Enterprise AI Remediation Targeting WCAG 2.2 AA Compliance</p>
      </header>

      <section aria-label="Document Upload Section">
        <div 
          className={`dropzone ${dragActive ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerFileInput}
          onKeyDown={(e) => { if ((e.key === 'Enter' || e.key === ' ') && !loading) triggerFileInput(); }}
          role="button"
          tabIndex={loading ? -1 : 0}
          aria-disabled={loading}
          aria-label="Drag and drop a PDF or Image here, or press enter to browse files for accessibility remediation."
          style={{ opacity: loading ? 0.6 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          <div className="dropzone-label">
            <svg aria-hidden="true" className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            <div>
              <h2 style={{fontSize: '1.2rem', marginBottom: '0.5rem', color: '#ffffff'}}>Secure Air-Gapped Upload</h2>
              <p>Drag and drop or click to browse (PDF, PNG, JPG up to 15MB)</p>
              <p className="sub-text">Encrypted edge processing ensures full data sovereignty.</p>
            </div>
            <input 
              ref={fileInputRef}
              type="file" 
              className="file-input" 
              accept="image/png, image/jpeg, application/pdf"
              onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) processFile(file);
                  e.target.value = null; 
              }}
              aria-hidden="true"
              tabIndex={-1}
              disabled={loading}
            />
          </div>
        </div>
      </section>

      {loading && (
        <div className="loader" role="status" aria-live="polite">
          <div className="spinner" aria-hidden="true"></div>
          <p>Running cognitive multi-modal document parsing... This may take up to 30 seconds for dense PDFs.</p>
        </div>
      )}

      {error && (
        <div className="results" role="alert" aria-live="assertive">
          <h2 style={{ color: '#ff7b72' }}>System Alert</h2>
          <div className="result-card" style={{ borderColor: '#ff7b72', color: '#ff7b72' }}>
            {error}
          </div>
        </div>
      )}

      {result && (
        <section className="results" aria-label="Extraction Results" style={{ animation: 'fadeIn 0.5s ease' }}>
          <div className="results-header">
            <h2>Remediated Output (Semantic Structure)</h2>
            <button 
              className="download-btn" 
              onClick={downloadMarkdown}
              aria-label="Download the remediated accessible Markdown file"
            >
              <svg aria-hidden="true" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
              Download Markdown
            </button>
          </div>
          <div className="result-card" tabIndex={0} aria-label="Document Content Viewer">
            <div className="json-output">
              {result.md_results || "No text could be extracted from the document."}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
