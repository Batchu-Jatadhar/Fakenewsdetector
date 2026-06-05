"use client";

import { useEffect, useState } from "react";
import { adminAPI, analysisAPI } from "@/lib/api";
import { PaginatedAnalyses, Analysis } from "@/types";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function AdminPage() {
  const [analyses, setAnalyses] = useState<PaginatedAnalyses | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);
  const [feedbackLabel, setFeedbackLabel] = useState<"real" | "fake">("fake");
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [feedbackMsg, setFeedbackMsg] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalyses = async () => {
      setLoading(true);
      try {
        const response = await adminAPI.analyses(page, 20);
        setAnalyses(response.data);
      } catch (err) {
        console.error("Failed to load analyses:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyses();
  }, [page]);

  const handleViewDetails = async (id: string) => {
    try {
      const response = await analysisAPI.get(id);
      setSelectedAnalysis(response.data);
      setFeedbackMsg("");
    } catch (err) {
      console.error("Failed to load analysis:", err);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!selectedAnalysis) return;

    try {
      await adminAPI.submitFeedback({
        analysis_id: selectedAnalysis.id,
        label: feedbackLabel,
        notes: feedbackNotes || undefined,
      });
      setFeedbackMsg("Feedback submitted successfully!");
      setFeedbackNotes("");
    } catch (err: any) {
      setFeedbackMsg(err.response?.data?.detail || "Failed to submit feedback");
    }
  };

  return (
    <ProtectedRoute roles={["analyst", "admin"]}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
          <span className="badge bg-indigo-500/20 text-indigo-400">
            Analyst / Admin
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Analyses List */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">All Analyses</h2>

            {loading ? (
              <div className="flex justify-center py-10">
                <div className="animate-spin h-6 w-6 border-2 border-indigo-500 border-t-transparent rounded-full" />
              </div>
            ) : analyses && analyses.items.length > 0 ? (
              <>
                <div className="space-y-2">
                  {analyses.items.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => handleViewDetails(item.id)}
                      className={`card cursor-pointer hover:border-indigo-500 transition-colors ${
                        selectedAnalysis?.id === item.id ? "border-indigo-500" : ""
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0 mr-4">
                          <p className="text-sm text-slate-300 truncate">
                            {item.source_url || item.content_text.slice(0, 80)}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        {item.fake_probability !== null && (
                          <span className={`text-sm font-bold ${
                            item.fake_probability < 0.3 ? "text-emerald-400" :
                            item.fake_probability < 0.6 ? "text-amber-400" : "text-red-400"
                          }`}>
                            {Math.round(item.fake_probability * 100)}%
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {analyses.pages > 1 && (
                  <div className="flex justify-center space-x-2">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="btn-secondary text-sm !py-1 !px-3 disabled:opacity-30"
                    >
                      Prev
                    </button>
                    <span className="text-sm text-slate-400 py-1">
                      {page}/{analyses.pages}
                    </span>
                    <button
                      onClick={() => setPage(Math.min(analyses.pages, page + 1))}
                      disabled={page >= analyses.pages}
                      className="btn-secondary text-sm !py-1 !px-3 disabled:opacity-30"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            ) : (
              <p className="text-slate-500 text-center py-10">No analyses found</p>
            )}
          </div>

          {/* Detail + Feedback Panel */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">Review & Label</h2>

            {selectedAnalysis ? (
              <div className="card space-y-4">
                <div>
                  <p className="text-xs text-slate-500 uppercase mb-1">Content Preview</p>
                  <p className="text-sm text-slate-300 max-h-32 overflow-y-auto">
                    {selectedAnalysis.content_text.slice(0, 500)}
                  </p>
                </div>

                {selectedAnalysis.fake_probability !== null && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-500">Fake Probability</p>
                      <p className="text-lg font-bold text-white">
                        {(selectedAnalysis.fake_probability * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Confidence</p>
                      <p className="text-lg font-bold text-white">
                        {selectedAnalysis.confidence
                          ? `${(selectedAnalysis.confidence * 100).toFixed(1)}%`
                          : "N/A"}
                      </p>
                    </div>
                  </div>
                )}

                {selectedAnalysis.explanation && (
                  <div>
                    <p className="text-xs text-slate-500 uppercase mb-1">AI Reasoning</p>
                    <p className="text-sm text-slate-400">
                      {selectedAnalysis.explanation.reasoning}
                    </p>
                  </div>
                )}

                <hr className="border-slate-700" />

                {/* Feedback Form */}
                <div className="space-y-3">
                  <p className="text-sm font-medium text-white">Manual Verification Label</p>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setFeedbackLabel("real")}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                        feedbackLabel === "real"
                          ? "bg-emerald-500 text-white"
                          : "bg-surface-light text-slate-400 hover:text-white"
                      }`}
                    >
                      Real News
                    </button>
                    <button
                      onClick={() => setFeedbackLabel("fake")}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                        feedbackLabel === "fake"
                          ? "bg-red-500 text-white"
                          : "bg-surface-light text-slate-400 hover:text-white"
                      }`}
                    >
                      Fake News
                    </button>
                  </div>
                  <textarea
                    value={feedbackNotes}
                    onChange={(e) => setFeedbackNotes(e.target.value)}
                    placeholder="Optional notes..."
                    className="input-field h-20 resize-none text-sm"
                  />
                  <button
                    onClick={handleSubmitFeedback}
                    className="btn-primary w-full text-sm"
                  >
                    Submit Label
                  </button>

                  {feedbackMsg && (
                    <p className={`text-sm ${
                      feedbackMsg.includes("success") ? "text-emerald-400" : "text-red-400"
                    }`}>
                      {feedbackMsg}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="card text-center py-16 text-slate-500">
                <p>Select an analysis to review</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
