"use client";

import { getScoreColor, getScoreLevel, getScoreLabel } from "@/types";

interface TrustMeterProps {
  score: number;
}

export default function TrustMeter({ score }: TrustMeterProps) {
  const level = getScoreLevel(1 - score); // Invert for trust display
  const color = getScoreColor(level);
  const percentage = Math.round((1 - score) * 100);
  const label = getScoreLabel(score);

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-slate-400">Trust Level</span>
        <span className="text-sm font-medium" style={{ color }}>
          {label} ({percentage}%)
        </span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-3">
        <div
          className="h-3 rounded-full transition-all duration-1000 ease-in-out"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}
