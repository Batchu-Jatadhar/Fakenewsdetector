export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "user" | "analyst" | "admin";
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SuspiciousPhrase {
  text: string;
  start: number;
  end: number;
  reason: string;
}

export interface Explanation {
  reasoning: string;
  suspicious_phrases: SuspiciousPhrase[];
}

export interface FactCheck {
  id: string;
  source: string;
  claim_text: string | null;
  verdict: string | null;
  publisher: string | null;
  url: string | null;
}

export interface Analysis {
  id: string;
  user_id: string;
  input_type: "text" | "url";
  source_url: string | null;
  content_text: string;
  fake_probability: number | null;
  trust_score: number | null;
  roberta_score: number | null;
  sbert_score: number | null;
  confidence: number | null;
  explanation: Explanation | null;
  source_credibility?: {
    domain: string;
    credibility_score: number;
    category?: string | null;
    country?: string | null;
    description?: string | null;
  } | null;
  status: "pending" | "completed" | "error";
  created_at: string;
  fact_checks: FactCheck[];
}

export interface AnalysisListItem {
  id: string;
  input_type: string;
  source_url: string | null;
  content_text: string;
  fake_probability: number | null;
  trust_score: number | null;
  status: string;
  created_at: string;
}

export interface PaginatedAnalyses {
  items: AnalysisListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface DashboardStats {
  total_analyses: number;
  total_fake: number;
  total_real: number;
  total_uncertain: number;
  misinformation_rate: number;
  avg_confidence: number;
}

export interface ModelMetrics {
  accuracy: number | null;
  f1_score: number | null;
  precision: number | null;
  recall: number | null;
  total_evaluated: number;
}

export interface FeedbackRequest {
  analysis_id: string;
  label: "real" | "fake";
  notes?: string;
}

export interface DomainStats {
  domain: string;
  total_analyses: number;
  total_fake: number;
  total_real: number;
  total_uncertain: number;
  misinformation_rate: number;
  avg_confidence: number | null;
}

export interface TopDomain {
  domain: string;
  total_analyses: number;
  misinformation_rate: number;
}

export type ScoreLevel = "safe" | "uncertain" | "danger";

export function getScoreLevel(score: number): ScoreLevel {
  if (score < 0.3) return "safe";
  if (score < 0.6) return "uncertain";
  return "danger";
}

export function getScoreColor(level: ScoreLevel): string {
  switch (level) {
    case "safe": return "#10B981";
    case "uncertain": return "#F59E0B";
    case "danger": return "#EF4444";
  }
}

export function getScoreLabel(score: number): string {
  if (score < 0.3) return "Likely Real";
  if (score < 0.6) return "Uncertain";
  return "Likely Fake";
}
