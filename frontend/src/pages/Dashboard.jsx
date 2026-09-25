import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { creditApi } from "../api/client.js";
import ScoreChart from "../components/ScoreChart.jsx";
import UtilizationChart from "../components/UtilizationChart.jsx";
import AdvisorPanel from "../components/AdvisorPanel.jsx";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    creditApi
      .getDashboard()
      .then((res) => setData(res.data))
      .catch((err) => {
        if (err.response?.status === 404) {
          setError("no-profile");
        } else {
          setError(err.response?.data?.detail || "Could not load your dashboard.");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading your dashboard...</p>;

  if (error === "no-profile") {
    return (
      <div className="card">
        <h2>Let's set up your credit profile</h2>
        <p style={{ color: "var(--text-dim)" }}>
          You haven't entered your financial details yet.
        </p>
        <Link to="/onboarding">
          <button className="primary">Enter my financial data</button>
        </Link>
      </div>
    );
  }

  if (error) return <div className="error-text">{error}</div>;

  const { profile, history, score_delta, utilization_delta } = data;
  const bandClass = `band-pill band-${profile.credit_band.replace(/\s+/g, "")}`;

  return (
    <div>
      <div className="grid-2">
        <div className="card">
          <div className="stat-label">Current Credit Score</div>
          <div className="score-big">{profile.credit_score}</div>
          <span className={bandClass}>{profile.credit_band}</span>
          {score_delta !== null && score_delta !== undefined && (
            <div style={{ marginTop: 10 }} className={score_delta >= 0 ? "delta-up" : "delta-down"}>
              {score_delta >= 0 ? "▲" : "▼"} {Math.abs(score_delta)} pts since last update
            </div>
          )}
        </div>

        <div className="card">
          <div className="stat-label">Debt-to-Income Ratio</div>
          <div className="stat-value">{profile.debt_to_income_ratio.toFixed(1)}%</div>
          <div className="stat-label" style={{ marginTop: 14 }}>Monthly Income vs Expenses</div>
          <div className="stat-value">
            ₹{profile.monthly_income.toLocaleString("en-IN")} / ₹{profile.monthly_expenses.toLocaleString("en-IN")}
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Score Progress</h3>
          <ScoreChart history={history} />
        </div>

        <div className="card">
          <h3>Credit Utilization</h3>
          <UtilizationChart utilizationRatio={profile.utilization_ratio} />
          {utilization_delta !== null && utilization_delta !== undefined && (
            <p className={utilization_delta <= 0 ? "delta-up" : "delta-down"} style={{ textAlign: "center" }}>
              {utilization_delta <= 0 ? "▼" : "▲"} {Math.abs(utilization_delta).toFixed(1)}% since last update
            </p>
          )}
        </div>
      </div>

      <AdvisorPanel />
    </div>
  );
}
