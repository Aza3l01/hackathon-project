"use client";

import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [csvFile, setCsvFile] = useState(null);
  const [stats, setStats] = useState(null);
  const [chartDataUrl, setChartDataUrl] = useState(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  async function handleAsk() {
    setAnswer("…thinking");
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer || data.error || "No answer");
  }

  async function handleAnalyze() {
    if (!csvFile) return alert("Choose a CSV file first");
    const fd = new FormData();
    fd.append("file", csvFile);
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: fd,
    });
    const data = await res.json();
    setStats(data.stats || null);
    setChartDataUrl(data.chart || null);
  }

  return (
    <div style={{ padding: 24 }}>
      <h1>Demo</h1>

      <section style={{ marginTop: 20 }}>
        <h2>LLM: Ask</h2>
        <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} cols={60} placeholder="Ask a question..." />
        <br />
        <button onClick={handleAsk} style={{ marginTop: 8 }}>Ask LLM</button>
        <div style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>
          <strong>Answer:</strong>
          <div>{answer}</div>
        </div>
      </section>

      <hr style={{ margin: "24px 0" }} />

      <section>
        <h2>Automation: Upload CSV</h2>
        <input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files?.[0] || null)} />
        <button onClick={handleAnalyze} style={{ marginLeft: 8 }}>Analyze CSV</button>
        <div style={{ marginTop: 12 }}>
          {stats && (
            <div>
              <h3>Stats</h3>
              <pre style={{ maxHeight: 200, overflow: "auto" }}>{JSON.stringify(stats, null, 2)}</pre>
            </div>
          )}
          {chartDataUrl && (
            <div>
              <h3>Chart</h3>
              <img src={chartDataUrl} alt="generated chart" style={{ maxWidth: "100%", border: "1px solid #ccc" }} />
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
