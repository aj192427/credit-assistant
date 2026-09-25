import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { creditApi } from "../api/client.js";

const initialForm = {
  credit_score: "",
  monthly_income: "",
  monthly_expenses: "",
  total_debt: "",
  total_credit_limit: "",
  credit_used: "",
  missed_payments_last_year: "0",
};

export default function Onboarding() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        credit_score: Number(form.credit_score),
        monthly_income: Number(form.monthly_income),
        monthly_expenses: Number(form.monthly_expenses),
        total_debt: Number(form.total_debt || 0),
        total_credit_limit: Number(form.total_credit_limit || 0),
        credit_used: Number(form.credit_used || 0),
        missed_payments_last_year: Number(form.missed_payments_last_year || 0),
      };
      await creditApi.submitProfile(payload);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save your financial data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 640, margin: "0 auto" }}>
      <h2>Your Financial Snapshot</h2>
      <p style={{ color: "var(--text-dim)", fontSize: 14 }}>
        Enter your current numbers (in INR). We'll calculate your debt-to-income ratio and
        credit utilization automatically, and save this as a new point on your progress chart.
      </p>
      <form onSubmit={handleSubmit}>
        <div className="grid-2">
          <div>
            <label>Credit Score (300–900)</label>
            <input type="number" min="300" max="900" value={form.credit_score} onChange={update("credit_score")} required />
          </div>
          <div>
            <label>Missed payments (last 12 months)</label>
            <input type="number" min="0" value={form.missed_payments_last_year} onChange={update("missed_payments_last_year")} />
          </div>
          <div>
            <label>Monthly Income (₹)</label>
            <input type="number" min="0" value={form.monthly_income} onChange={update("monthly_income")} required />
          </div>
          <div>
            <label>Monthly Expenses (₹)</label>
            <input type="number" min="0" value={form.monthly_expenses} onChange={update("monthly_expenses")} required />
          </div>
          <div>
            <label>Total Outstanding Debt (₹)</label>
            <input type="number" min="0" value={form.total_debt} onChange={update("total_debt")} />
          </div>
          <div>
            <label>Total Credit Limit (₹)</label>
            <input type="number" min="0" value={form.total_credit_limit} onChange={update("total_credit_limit")} />
          </div>
          <div>
            <label>Current Credit Used / Revolving Balance (₹)</label>
            <input type="number" min="0" value={form.credit_used} onChange={update("credit_used")} />
          </div>
        </div>

        {error && <div className="error-text">{error}</div>}

        <button className="primary" type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save & View Dashboard"}
        </button>
      </form>
    </div>
  );
}
