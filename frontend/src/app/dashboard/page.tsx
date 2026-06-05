"use client";

import { useEffect, useState } from "react";
import { dashboardAPI } from "@/lib/api";
import { DashboardStats, DomainStats, ModelMetrics, TopDomain } from "@/types";
import ProtectedRoute from "@/components/ProtectedRoute";
import StatsCard from "@/components/StatsCard";
import AccuracyChart from "@/components/charts/AccuracyChart";
import MetricsChart from "@/components/charts/MetricsChart";
import MisinfoRateChart from "@/components/charts/MisinfoRateChart";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [topDomains, setTopDomains] = useState<TopDomain[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, metricsRes, topDomainsRes] = await Promise.all([
          dashboardAPI.stats(),
          dashboardAPI.metrics(),
          dashboardAPI.topDomains(5),
        ]);
        setStats(statsRes.data as DashboardStats);
        setMetrics(metricsRes.data as ModelMetrics);
        setTopDomains(topDomainsRes.data as TopDomain[]);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <ProtectedRoute>
      <div className="space-y-8">
        <h1 className="text-2xl font-bold text-white">Analytics Dashboard</h1>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin h-8 w-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                title="Total Analyses"
                value={stats?.total_analyses || 0}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                }
                color="#6366F1"
              />
              <StatsCard
                title="Likely Fake"
                value={stats?.total_fake || 0}
                subtitle={`${stats?.misinformation_rate || 0}% rate`}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                }
                color="#EF4444"
              />
              <StatsCard
                title="Likely Real"
                value={stats?.total_real || 0}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
                color="#10B981"
              />
              <StatsCard
                title="Avg Confidence"
                value={stats?.avg_confidence ? `${(stats.avg_confidence * 100).toFixed(1)}%` : "N/A"}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                }
                color="#F59E0B"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">Classification Distribution</h2>
                <AccuracyChart
                  totalFake={stats?.total_fake || 0}
                  totalReal={stats?.total_real || 0}
                  totalUncertain={stats?.total_uncertain || 0}
                />
              </div>

              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">Misinformation Rate</h2>
                <MisinfoRateChart rate={stats?.misinformation_rate || 0} />
              </div>
            </div>

            {/* High-Risk Domains */}
            {topDomains.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">
                  High-Risk Domains
                </h2>
                <div className="space-y-2">
                  {topDomains.map((d) => (
                    <div
                      key={d.domain}
                      className="flex items-center justify-between text-sm text-slate-300"
                    >
                      <span className="font-mono break-all">{d.domain}</span>
                      <span className="text-slate-400">
                        {d.misinformation_rate.toFixed(1)}% fake &middot; {d.total_analyses} articles
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Model Metrics */}
            <div className="card">
              <h2 className="text-lg font-semibold text-white mb-4">
                Model Performance Metrics
                {metrics && metrics.total_evaluated > 0 && (
                  <span className="text-sm text-slate-400 font-normal ml-2">
                    ({metrics.total_evaluated} evaluated samples)
                  </span>
                )}
              </h2>
              {metrics && metrics.total_evaluated > 0 ? (
                <MetricsChart
                  accuracy={metrics.accuracy}
                  f1Score={metrics.f1_score}
                  precision={metrics.precision}
                  recall={metrics.recall}
                />
              ) : (
                <div className="text-center py-12 text-slate-500">
                  <p>No evaluation data available yet.</p>
                  <p className="text-sm mt-1">Analysts need to provide manual labels for model evaluation.</p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}
