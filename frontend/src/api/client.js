import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") || "/";
const api = axios.create({ baseURL: apiBaseUrl });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ca_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  register: (payload) => api.post("/auth/register", payload),
  login: (email, password) => {
    // FastAPI's OAuth2PasswordRequestForm expects form-encoded "username"/"password"
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
};

export const creditApi = {
  submitProfile: (payload) => api.post("/credit/profile", payload),
  getDashboard: () => api.get("/credit/dashboard"),
};

export const advisorApi = {
  consult: (goal) => api.post("/advisor/consult", { goal: goal || null }),
  chat: (messages) => api.post("/advisor/chat", { messages }),
};

export default api;
