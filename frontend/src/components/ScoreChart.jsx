import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

export default function ScoreChart({ history }) {
  const data = history.map((h) => ({
    date: new Date(h.recorded_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    score: h.credit_score,
  }));

  if (data.length < 2) {
    return (
      <p style={{ color: "var(--text-dim)", fontSize: 14 }}>
        Update your profile at least twice to see your progress trend here.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#262b38" />
        <XAxis dataKey="date" stroke="#9aa2b4" fontSize={12} />
        <YAxis domain={[300, 900]} stroke="#9aa2b4" fontSize={12} />
        <Tooltip contentStyle={{ background: "#171a23", border: "1px solid #262b38" }} />
        <Line type="monotone" dataKey="score" stroke="#4f8cff" strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
