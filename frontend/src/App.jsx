import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Onboarding from "./pages/Onboarding.jsx";
import Dashboard from "./pages/Dashboard.jsx";

function useAuth() {
  const [token, setToken] = useState(localStorage.getItem("ca_token"));

  useEffect(() => {
    const onStorage = () => setToken(localStorage.getItem("ca_token"));
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const login = (t) => {
    localStorage.setItem("ca_token", t);
    setToken(t);
  };
  const logout = () => {
    localStorage.removeItem("ca_token");
    setToken(null);
  };
  return { token, login, logout };
}

function RequireAuth({ token, children }) {
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function Navbar({ token, onLogout }) {
  const navigate = useNavigate();
  return (
    <div className="navbar">
      <h1>💳 Credit Assistant</h1>
      <div>
        {token ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/onboarding">Update Profile</Link>
            <button
              onClick={() => {
                onLogout();
                navigate("/login");
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const { token, login, logout } = useAuth();
  const [reduceMotion, setReduceMotion] = useState(() =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => setReduceMotion(preference.matches);
    preference.addEventListener("change", updatePreference);
    return () => preference.removeEventListener("change", updatePreference);
  }, []);

  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <>
        <div className="app-backdrop" aria-hidden="true">
          {!reduceMotion && (
            <video className="ambient-video" autoPlay loop muted playsInline preload="none">
              <source
                src="https://videos.pexels.com/video-files/7821606/7821606-hd_1920_1080_30fps.mp4"
                type="video/mp4"
              />
            </video>
          )}
        </div>
        <div className="app-shell">
          <Navbar token={token} onLogout={logout} />
          <Routes>
            <Route path="/login" element={<Login onLogin={login} />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/onboarding"
              element={
                <RequireAuth token={token}>
                  <Onboarding />
                </RequireAuth>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RequireAuth token={token}>
                  <Dashboard />
                </RequireAuth>
              }
            />
            <Route path="*" element={<Navigate to={token ? "/dashboard" : "/login"} replace />} />
          </Routes>
        </div>
      </>
    </BrowserRouter>
  );
}
