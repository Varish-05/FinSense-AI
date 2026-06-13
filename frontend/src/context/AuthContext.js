/**
 * AuthContext – provides user state and auth helpers app-wide.
 */
import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../utils/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from token on mount
  useEffect(() => {
    const token = localStorage.getItem("finsense_token");
    if (token) {
      authAPI.me()
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem("finsense_token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    localStorage.setItem("finsense_token", res.data.access_token);
    const me = await authAPI.me();
    setUser(me.data);
    return me.data;
  };

  const register = async (data) => {
    await authAPI.register(data);
    return login(data.email, data.password);
  };

  const logout = () => {
    localStorage.removeItem("finsense_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
