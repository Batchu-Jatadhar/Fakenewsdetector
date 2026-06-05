"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface AccuracyChartProps {
  totalFake: number;
  totalReal: number;
  totalUncertain: number;
}

const COLORS = ["#10B981", "#EF4444", "#F59E0B"];

export default function AccuracyChart({ totalFake, totalReal, totalUncertain }: AccuracyChartProps) {
  const data = [
    { name: "Real", value: totalReal },
    { name: "Fake", value: totalFake },
    { name: "Uncertain", value: totalUncertain },
  ].filter(d => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={5}
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1E293B",
            border: "1px solid #334155",
            borderRadius: "8px",
            color: "#F8FAFC",
          }}
        />
        <Legend
          wrapperStyle={{ color: "#94A3B8" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
