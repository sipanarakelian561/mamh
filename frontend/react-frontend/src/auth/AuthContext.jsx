import { useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import { AuthContext } from "./context";

function decodeTokenPayload(jwtToken) {
  try {
    const payload = jwtToken.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(
      normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=")
    );
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

function userFromToken(jwtToken) {
  const payload = decodeTokenPayload(jwtToken);
  if (!payload?.sub || !payload?.role) return null;
  return {
    id: Number(payload.sub),
    role: payload.role,
    is_admin: Boolean(payload.adm),
    must_change_password: Boolean(payload.pwd),
  };
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() =>
    localStorage.getItem("token") || ""
  );

  const [loading, setLoading] = useState(false);
  const user = useMemo(() => userFromToken(token), [token]);

  async function login(email, password) {
    setLoading(true);
    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      const access = data.access_token || data.token || data;
      setToken(access);
      localStorage.setItem("token", access);
      return access;
    } finally {
      setLoading(false);
    }
  }

  async function register({ email, password, role }) {
    setLoading(true);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, role }),
      });
      return await login(email, password);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setToken("");
    localStorage.removeItem("token");
  }

  const value = { token, user, loading, login, register, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
