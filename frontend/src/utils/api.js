/**
 * Axios API client for FinSense AI backend.
 * Automatically attaches the JWT token to every request.
 */
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("finsense_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redirect to login on 401 (except for login requests)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes("/auth/login")) {
      localStorage.removeItem("finsense_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Auth ─────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  updateMe: (data) => api.put("/auth/me", data),
};

// ── Expenses ──────────────────────────────────────────────────────────
export const expensesAPI = {
  list: (params) => api.get("/expenses", { params }),
  create: (data) => api.post("/expenses", data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
  uploadCSV: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/expenses/upload/csv", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ── Budgets ───────────────────────────────────────────────────────────
export const budgetsAPI = {
  list: (month) => api.get("/budgets", { params: { month } }),
  create: (data) => api.post("/budgets", data),
  delete: (id) => api.delete(`/budgets/${id}`),
};

// ── Analytics ─────────────────────────────────────────────────────────
export const analyticsAPI = {
  dashboard: () => api.get("/dashboard"),
  forecast: (params) => api.get("/forecast", { params }),
  healthScore: (month) => api.post(`/health-score?month=${month}`),
  chat: (message) => api.post("/chat", { message }),
};
