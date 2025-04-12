'use client';

import React, { useState, useMemo } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log("📤 Uploading file:", file.name);

      const res = await fetch('http://localhost:8000/analyze/file', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      console.log("✅ Analysis result:", data);

      setResult(data.issues || []);
    } catch (err) {
      alert('❌ Error analyzing file');
      console.error("🚨 Upload error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Deduplicate issues by (line, issue_type)
  const dedupedResults = useMemo(() => {
    const seen = new Set();
    const filtered: any[] = [];

    for (const item of result) {
      const key = `${item.line}-${item.issue_type || item.issue}`; // fallback if tag is missing
      if (!seen.has(key)) {
        seen.add(key);
        filtered.push(item);
      }
    }

    return filtered;
  }, [result]);

  return (
    <main className="min-h-screen p-10 bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">AI Code Reviewer</h1>

      <input
        type="file"
        accept=".py"
        className="mb-4 border p-2 text-white"
        onClick={() => console.log("📂 File input clicked")}
        onChange={(e) => {
          const selectedFile = e.target.files?.[0] || null;
          console.log("📄 File selected:", selectedFile);
          setFile(selectedFile);
        }}
      />

      <button
        onClick={handleUpload}
        className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        disabled={loading || !file}
      >
        {loading ? 'Analyzing...' : 'Upload & Analyze'}
      </button>

      <div className="mt-10 space-y-4">
        {dedupedResults.map((item, idx) => (
          <div key={idx} className="border border-gray-700 p-4 rounded bg-gray-800">
            <p>
              <strong>Line {item.line}</strong>: {item.issue}
              {item.issue_type && (
                <span className="ml-2 text-sm text-gray-400">[{item.issue_type}]</span>
              )}
            </p>
            {item.fix && (
              <pre className="mt-2 bg-black text-green-400 p-2 rounded overflow-x-auto">
                {item.fix}
              </pre>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
