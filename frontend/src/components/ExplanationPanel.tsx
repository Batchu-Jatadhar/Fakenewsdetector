"use client";

import { Explanation } from "@/types";

interface ExplanationPanelProps {
  explanation: Explanation;
  contentText: string;
}

export default function ExplanationPanel({ explanation, contentText }: ExplanationPanelProps) {
  const highlightText = () => {
    if (!explanation.suspicious_phrases?.length) {
      return <p className="text-slate-300 whitespace-pre-wrap">{contentText}</p>;
    }

    const sortedPhrases = [...explanation.suspicious_phrases].sort((a, b) => a.start - b.start);
    const parts: React.ReactNode[] = [];
    let lastEnd = 0;

    sortedPhrases.forEach((phrase, i) => {
      // Text before this phrase
      if (phrase.start > lastEnd) {
        parts.push(
          <span key={`text-${i}`} className="text-slate-300">
            {contentText.slice(lastEnd, phrase.start)}
          </span>
        );
      }

      // Highlighted phrase
      parts.push(
        <span
          key={`highlight-${i}`}
          className="bg-red-500/20 text-red-300 border-b-2 border-red-500 cursor-help"
          title={phrase.reason}
        >
          {contentText.slice(phrase.start, phrase.end)}
        </span>
      );

      lastEnd = phrase.end;
    });

    // Remaining text
    if (lastEnd < contentText.length) {
      parts.push(
        <span key="text-end" className="text-slate-300">
          {contentText.slice(lastEnd)}
        </span>
      );
    }

    return <p className="whitespace-pre-wrap leading-relaxed">{parts}</p>;
  };

  return (
    <div className="space-y-6">
      {/* AI Reasoning */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center space-x-2">
          <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>AI Reasoning</span>
        </h3>
        <p className="text-slate-300 leading-relaxed">{explanation.reasoning}</p>
      </div>

      {/* Highlighted Content */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center space-x-2">
          <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Content Analysis</span>
        </h3>
        <div className="bg-surface-dark rounded-lg p-4 max-h-96 overflow-y-auto text-sm">
          {highlightText()}
        </div>

        {explanation.suspicious_phrases?.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-slate-400 mb-2">Suspicious Elements Found:</h4>
            <div className="space-y-2">
              {explanation.suspicious_phrases.map((phrase, i) => (
                <div key={i} className="flex items-start space-x-2 text-sm">
                  <span className="text-red-400 mt-0.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </span>
                  <div>
                    <span className="text-red-300 font-medium">&quot;{phrase.text}&quot;</span>
                    <span className="text-slate-500 mx-1">-</span>
                    <span className="text-slate-400">{phrase.reason}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
