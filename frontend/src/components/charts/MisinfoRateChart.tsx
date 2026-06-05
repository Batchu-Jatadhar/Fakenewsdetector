"use client";

interface MisinfoRateChartProps {
  rate: number;
}

export default function MisinfoRateChart({ rate }: MisinfoRateChartProps) {
  const clampedRate = Math.min(Math.max(rate, 0), 100);
  const color = clampedRate < 20 ? "#10B981" : clampedRate < 50 ? "#F59E0B" : "#EF4444";

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-4xl font-bold" style={{ color }}>
            {clampedRate.toFixed(1)}%
          </p>
          <p className="text-sm text-slate-400 mt-1">Misinformation Rate</p>
        </div>
        <div className="text-right text-sm text-slate-500">
          {clampedRate < 20 ? "Low" : clampedRate < 50 ? "Moderate" : "High"} risk environment
        </div>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-4">
        <div
          className="h-4 rounded-full transition-all duration-1000 ease-in-out"
          style={{
            width: `${clampedRate}%`,
            backgroundColor: color,
          }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-500">
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  );
}
