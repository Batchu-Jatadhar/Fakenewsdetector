"use client";

import { useEffect, useState } from "react";
import { historyAPI } from "@/lib/api";
import { PaginatedAnalyses } from "@/types";
import ProtectedRoute from "@/components/ProtectedRoute";
import AnalysisCard from "@/components/AnalysisCard";

export default function HistoryPage() {
  const [data, setData] = useState<PaginatedAnalyses | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response = await historyAPI.list(page, 20);
        setData(response.data);
      } catch (err) {
        console.error("Failed to load history:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [page]);

  return (
    <ProtectedRoute>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-6">Analysis History</h1>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin h-8 w-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
          </div>
        ) : data && data.items.length > 0 ? (
          <>
            <div className="space-y-3">
              {data.items.map((analysis) => (
                <AnalysisCard key={analysis.id} analysis={analysis} />
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex justify-center space-x-2 mt-8">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn-secondary text-sm !py-2 !px-4 disabled:opacity-30"
                >
                  Previous
                </button>
                <span className="flex items-center text-sm text-slate-400 px-4">
                  Page {data.page} of {data.pages}
                </span>
                <button
                  onClick={() => setPage(Math.min(data.pages, page + 1))}
                  disabled={page >= data.pages}
                  className="btn-secondary text-sm !py-2 !px-4 disabled:opacity-30"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="card text-center py-16">
            <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p className="text-slate-400 text-lg">No analyses yet</p>
            <p className="text-slate-500 text-sm mt-1">Submit your first article for analysis</p>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
