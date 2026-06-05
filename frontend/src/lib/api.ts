import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/api/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
};

// Analysis
export const analysisAPI = {
  analyze: (data: { input_type: string; content: string }) =>
    api.post("/api/analyze", data),
  get: (id: string) => api.get(`/api/analysis/${id}`),
};

// History
export const historyAPI = {
  list: (page = 1, limit = 20) =>
    api.get("/api/history", { params: { page, limit } }),
};

// Dashboard
export const dashboardAPI = {
  stats: () => api.get("/api/dashboard/stats"),
  metrics: () => api.get("/api/dashboard/metrics"),
  topDomains: (limit = 10) =>
    api.get("/api/dashboard/domains/top", { params: { limit } }),
  domainStats: (domain: string) =>
    api.get(`/api/dashboard/domain/${encodeURIComponent(domain)}`),
};

// Feedback (regular users)
export const feedbackAPI = {
  submit: (data: { analysis_id: string; label: "real" | "fake"; notes?: string }) =>
    api.post("/api/feedback", data),
};

// Admin
export const adminAPI = {
  analyses: (page = 1, limit = 20) =>
    api.get("/api/admin/analyses", { params: { page, limit } }),
  submitFeedback: (data: { analysis_id: string; label: string; notes?: string }) =>
    api.post("/api/admin/feedback", data),
  users: () => api.get("/api/admin/users"),
};

export default api;
