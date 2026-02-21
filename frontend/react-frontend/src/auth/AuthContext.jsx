import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { AuthContext } from "./context";

export function AuthProvider({ children }) {
  const DEV_MODE = true; // set false when backend is ready

  // Mock test accounts for dev mode
  const MOCK_ACCOUNTS = {
    "teacher@test.com": {
      password: "password",
      user: {
        id: 1,
        first_name: "Dev",
        last_name: "Teacher",
        email: "teacher@test.com",
        role: "teacher",
      },
    },
    "student@test.com": {
      password: "password",
      user: {
        id: 2,
        first_name: "Dev",
        last_name: "Student",
        email: "student@test.com",
        role: "student",
      },
    },
  };

  const [token, setToken] = useState(() =>
    localStorage.getItem("token") || ""
  );

  const [user, setUser] = useState(() => null);

  const [loading, setLoading] = useState(false);

  async function loadMe(tkn) {
    if (!tkn) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await apiFetch("/me", { token: tkn, method: "GET" });
      setUser(me);
    } catch {
      setUser(null);
      setToken("");
      localStorage.removeItem("token");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!DEV_MODE) loadMe(token);
  }, []); // only on mount

  async function login(email, password) {
    if (DEV_MODE) {
      // Dev mode: check against mock accounts
      const account = MOCK_ACCOUNTS[email.toLowerCase()];
      
      if (!account || account.password !== password) {
        throw new Error("Invalid email or password. Use teacher@test.com or student@test.com with password 'password'");
      }

      setToken("dev-token");
      setUser(account.user);
      localStorage.setItem("token", "dev-token");
      return "dev-token";
    }

    // Production mode: use actual API
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    const access = data.access_token || data.token || data;

    setToken(access);
    localStorage.setItem("token", access);

    await loadMe(access);
    return access;
  }

  async function register({ email, password, role }) {
    if (DEV_MODE) {
      // Dev mode: registration not needed, use mock accounts instead
      throw new Error("Registration disabled in dev mode. Please use: teacher@test.com or student@test.com with password 'password'");
    }

    // Production mode: use actual API
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, role }),
    });
    return login(email, password);
  }

  function logout() {
    setToken("");
    setUser(null);
    localStorage.removeItem("token");
  }

  const value = { token, user, loading, login, register, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}