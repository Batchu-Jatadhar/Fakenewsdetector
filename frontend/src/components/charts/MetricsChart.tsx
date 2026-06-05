"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface MetricsChartProps {
  accuracy: number | null;
  f1Score: number | null;
  precision: number | null;
  recall: number | null;
}

export default function MetricsChart({ accuracy, f1Score, precision, recall }: MetricsChartProps) {
  const data = [
    { name: "Accuracy", value: accuracy ? +(accuracy * 100).toFixed(1) : 0, fill: "#6366F1" },
    { name: "F1 Score", value: f1Score ? +(f1Score * 100).toFixed(1) : 0, fill: "#10B981" },
    { name: "Precision", value: precision ? +(precision * 100).toFixed(1) : 0, fill: "#F59E0B" },
    { name: "Recall", value: recall ? +(recall * 100).toFixed(1) : 0, fill: "#EF4444" },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis type="number" domain={[0, 100]} stroke="#94A3B8" tickFormatter={(v) => `${v}%`} />
        <YAxis type="category" dataKey="name" stroke="#94A3B8" width={80} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1E293B",
            border: "1px solid #334155",
            borderRadius: "8px",
            color: "#F8FAFC",
          }}
          formatter={(value: number) => [`${value}%`, "Score"]}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
