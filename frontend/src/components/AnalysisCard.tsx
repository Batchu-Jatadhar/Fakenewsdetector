"use client";

import Link from "next/link";
import { AnalysisListItem, getScoreLevel } from "@/types";

interface AnalysisCardProps {
  analysis: AnalysisListItem;
}

export default function AnalysisCard({ analysis }: AnalysisCardProps) {
  const getBadgeClass = () => {
    if (analysis.status !== "completed" || analysis.fake_probability === null) return "badge-pending";
    const level = getScoreLevel(analysis.fake_probability);
    switch (level) {
      case "safe": return "badge-safe";
      case "uncertain": return "badge-uncertain";
      case "danger": return "badge-danger";
    }
  };

  const getStatusLabel = () => {
    if (analysis.status === "pending") return "Pending";
    if (analysis.status === "error") return "Error";
    if (analysis.fake_probability === null) return "N/A";
    if (analysis.fake_probability < 0.3) return "Likely Real";
    if (analysis.fake_probability < 0.6) return "Uncertain";
    return "Likely Fake";
  };

  return (
    <Link href={`/results/${analysis.id}`}>
      <div className="card hover:border-slate-600 transition-colors cursor-pointer">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0 mr-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs text-slate-500 uppercase font-medium">
                {analysis.input_type}
              </span>
              <span className={getBadgeClass()}>
                {getStatusLabel()}
              </span>
            </div>
            <p className="text-sm text-slate-300 line-clamp-2">
              {analysis.source_url || analysis.content_text.slice(0, 150)}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              {new Date(analysis.created_at).toLocaleDateString("en-US", {
                month: "short", day: "numeric", year: "numeric",
                hour: "2-digit", minute: "2-digit",
              })}
            </p>
          </div>
          {analysis.fake_probability !== null && (
            <div className="text-right flex-shrink-0">
              <div className="text-2xl font-bold" style={{
                color: analysis.fake_probability < 0.3 ? "#10B981" :
                       analysis.fake_probability < 0.6 ? "#F59E0B" : "#EF4444"
              }}>
                {Math.round(analysis.fake_probability * 100)}%
              </div>
              <div className="text-xs text-slate-500">Fake Prob.</div>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
