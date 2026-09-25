import React, { useState } from "react";
import { advisorApi } from "../api/client.js";

export default function AdvisorPanel() {
  const [goal, setGoal] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runConsultation = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await advisorApi.consult(goal);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not reach the AI advisor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>AI Financial Consultation</h3>
      <p style={{ color: "var(--text-dim)", fontSize: 14 }}>
        Get a personalized analysis and a 5-step plan based on your current numbers.
      </p>
      <label>Optional goal (e.g. "buy a car in 12 months")</label>
      <input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="What are you working toward?" />

      <button className="primary" onClick={runConsultation} disabled={loading}>
        {loading ? "Consulting Gemini AI..." : "Get AI Advice"}
      </button>

      {error && <div className="error-text">{error}</div>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <p>{result.analysis}</p>
          <h4>Your 5-Step Plan</h4>
          <ol className="action-plan">
            {result.action_plan.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
