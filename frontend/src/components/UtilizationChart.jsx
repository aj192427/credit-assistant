import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#f2554b", "#262b38"]; // used vs. available

export default function UtilizationChart({ utilizationRatio }) {
  const used = Math.min(utilizationRatio, 100);
  const available = Math.max(100 - used, 0);
  const data = [
    { name: "Used", value: used },
    { name: "Available", value: available },
  ];

  return (
    <div style={{ position: "relative" }}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            innerRadius={65}
            outerRadius={90}
            startAngle={90}
            endAngle={-270}
            stroke="none"
          >
            {data.map((entry, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: "#171a23", border: "1px solid #262b38" }} />
        </PieChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -55%)",
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 26, fontWeight: 700 }}>{utilizationRatio.toFixed(1)}%</div>
        <div style={{ fontSize: 12, color: "var(--text-dim)" }}>Utilization</div>
      </div>
    </div>
  );
}
