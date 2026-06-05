"use client";

import { getScoreColor, getScoreLevel } from "@/types";

interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: number;
}

export default function ScoreGauge({ score, label, size = 160 }: ScoreGaugeProps) {
  const level = getScoreLevel(score);
  const color = getScoreColor(level);
  const percentage = Math.round(score * 100);

  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#334155"
            strokeWidth="10"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color }}>
            {percentage}%
          </span>
        </div>
      </div>
      <span className="mt-2 text-sm text-slate-400 font-medium">{label}</span>
    </div>
  );
}
