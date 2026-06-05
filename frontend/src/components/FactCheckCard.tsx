"use client";

import { FactCheck } from "@/types";

interface FactCheckCardProps {
  factCheck: FactCheck;
}

export default function FactCheckCard({ factCheck }: FactCheckCardProps) {
  const getVerdictColor = (verdict: string | null) => {
    if (!verdict) return "text-slate-400";
    const v = verdict.toLowerCase();
    if (v.includes("true") || v.includes("correct")) return "text-emerald-400";
    if (v.includes("false") || v.includes("pants") || v.includes("wrong")) return "text-red-400";
    if (v.includes("mixture") || v.includes("half")) return "text-amber-400";
    return "text-slate-400";
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case "google_factcheck":
        return "G";
      case "newsapi":
        return "N";
      default:
        return "F";
    }
  };

  return (
    <div className="card hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm font-bold flex-shrink-0">
            {getSourceIcon(factCheck.source)}
          </div>
          <div className="flex-1 min-w-0">
            {factCheck.claim_text && (
              <p className="text-sm text-slate-300 mb-1">{factCheck.claim_text}</p>
            )}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              {factCheck.verdict && (
                <span className={`font-semibold ${getVerdictColor(factCheck.verdict)}`}>
                  Verdict: {factCheck.verdict}
                </span>
              )}
              {factCheck.publisher && (
                <span className="text-slate-500">by {factCheck.publisher}</span>
              )}
            </div>
          </div>
        </div>
        {factCheck.url && factCheck.url !== "" && (
          <a
            href={factCheck.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 hover:text-indigo-300 ml-2 flex-shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}
