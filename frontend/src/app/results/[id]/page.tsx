"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { analysisAPI, feedbackAPI } from "@/lib/api";
import { Analysis } from "@/types";
import ProtectedRoute from "@/components/ProtectedRoute";
import ScoreGauge from "@/components/ScoreGauge";
import TrustMeter from "@/components/TrustMeter";
import ExplanationPanel from "@/components/ExplanationPanel";
import FactCheckCard from "@/components/FactCheckCard";

export default function ResultsPage() {
  const params = useParams();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await analysisAPI.get(params.id as string);
        setAnalysis(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load analysis");
      } finally {
        setLoading(false);
      }
    };
    if (params.id) fetchAnalysis();
  }, [params.id]);

  const handleFeedback = async (label: "real" | "fake") => {
    if (!analysis || feedbackSubmitting) return;
    setFeedbackSubmitting(true);
    setFeedbackMessage(null);
    try {
      await feedbackAPI.submit({
        analysis_id: analysis.id,
        label,
      });
      setFeedbackMessage("Thanks for your feedback. It helps improve the model.");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setFeedbackMessage(
        typeof detail === "string"
          ? detail
          : "Failed to submit feedback. Please try again."
      );
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="max-w-5xl mx-auto">
        {loading ? (
          <div className="flex items-center justify-center min-h-[50vh]">
            <div className="text-center">
              <div className="animate-spin h-10 w-10 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
              <p className="text-slate-400">Loading analysis results...</p>
            </div>
          </div>
        ) : error ? (
          <div className="card text-center py-12">
            <p className="text-red-400 text-lg">{error}</p>
          </div>
        ) : analysis ? (
          <div className="space-y-8">
            {/* Header */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-xs text-slate-500 uppercase font-medium">
                  {analysis.input_type === "url" ? "URL Analysis" : "Text Analysis"}
                </span>
                <span className={`badge ${
                  analysis.status === "completed" ? "badge-safe" :
                  analysis.status === "error" ? "badge-danger" : "badge-pending"
                }`}>
                  {analysis.status}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
              {analysis.source_url && (
                <p className="text-sm text-slate-400 mt-1 break-all">{analysis.source_url}</p>
              )}
              {analysis.source_credibility && (
                <p className="text-xs text-slate-400 mt-1">
                  Source credibility ({analysis.source_credibility.domain}):{" "}
                  <span className="font-semibold">
                    {(analysis.source_credibility.credibility_score * 100).toFixed(0)}% trusted
                  </span>
                  {analysis.source_credibility.category && (
                    <> · {analysis.source_credibility.category}</>
                  )}
                  {analysis.source_credibility.country && (
                    <> · {analysis.source_credibility.country.toUpperCase()}</>
                  )}
                </p>
              )}
              <p className="text-xs text-slate-500 mt-1">
                {new Date(analysis.created_at).toLocaleString()}
              </p>
            </div>

            {analysis.status === "completed" && analysis.fake_probability !== null && (
              <>
                {/* Score Section */}
                <div className="card">
                  <h2 className="text-lg font-semibold text-white mb-6">Detection Scores</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
                    <ScoreGauge
                      score={analysis.fake_probability}
                      label="Fake Probability"
                    />
                    <ScoreGauge
                      score={analysis.trust_score || 1 - analysis.fake_probability}
                      label="Trust Score"
                    />
                    <ScoreGauge
                      score={analysis.confidence || 0}
                      label="Confidence"
                      size={160}
                    />
                  </div>
                  <TrustMeter score={analysis.fake_probability} />

                  {/* Model Breakdown */}
                  <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-slate-700">
                    <div>
                      <p className="text-xs text-slate-500 uppercase">RoBERTa Score</p>
                      <p className="text-lg font-semibold text-white">
                        {analysis.roberta_score !== null
                          ? `${(analysis.roberta_score * 100).toFixed(1)}%`
                          : "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">SBERT Score</p>
                      <p className="text-lg font-semibold text-white">
                        {analysis.sbert_score !== null
                          ? `${(analysis.sbert_score * 100).toFixed(1)}%`
                          : "N/A"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Explanation */}
                {analysis.explanation && (
                  <ExplanationPanel
                    explanation={analysis.explanation}
                    contentText={analysis.content_text}
                  />
                )}

                {/* Fact Checks */}
                {analysis.fact_checks && analysis.fact_checks.length > 0 && (
                  <div>
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                      <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Fact-Check References</span>
                    </h2>
                    <div className="space-y-3">
                      {analysis.fact_checks.map((fc) => (
                        <FactCheckCard key={fc.id} factCheck={fc} />
                      ))}
                    </div>
                  </div>
                )}

                {/* User Feedback */}
                <div className="card">
                  <h2 className="text-lg font-semibold text-white mb-3">
                    Was this prediction accurate?
                  </h2>
                  <p className="text-sm text-slate-400 mb-4">
                    Your feedback helps us evaluate and improve the detection models.
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      disabled={feedbackSubmitting}
                      onClick={() => handleFeedback("real")}
                      className="btn-secondary text-sm disabled:opacity-50"
                    >
                      It was real
                    </button>
                    <button
                      type="button"
                      disabled={feedbackSubmitting}
                      onClick={() => handleFeedback("fake")}
                      className="btn-secondary text-sm disabled:opacity-50"
                    >
                      It was fake / misleading
                    </button>
                  </div>
                  {feedbackMessage && (
                    <p className="text-xs text-slate-400 mt-3">
                      {feedbackMessage}
                    </p>
                  )}
                </div>
              </>
            )}

            {analysis.status === "error" && analysis.explanation && (
              <div className="card bg-red-500/5 border-red-500/20">
                <h2 className="text-lg font-semibold text-red-400 mb-2">Analysis Error</h2>
                <p className="text-slate-400">{analysis.explanation.reasoning}</p>
              </div>
            )}
          </div>
        ) : null}
      </div>
    </ProtectedRoute>
  );
}
