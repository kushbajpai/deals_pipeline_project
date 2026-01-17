import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { User } from "../types";
import { authAPI } from "../api/auth.api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [refreshToken, setRefreshToken] = useState<string | null>(() =>
    localStorage.getItem("refreshToken")
  );
  const [isLoading, setIsLoading] = useState(true);

  // Initialize user on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          console.error("Failed to load user", error);
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          setToken(null);
          setRefreshToken(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const data = await authAPI.login({ email, password });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refreshToken", data.refresh_token);
      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setUser(data.user);
    } catch (error) {
      console.error("Login failed", error);
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      const data = await authAPI.register({ email, password, full_name: fullName });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refreshToken", data.refresh_token);
      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setUser(data.user);
    } catch (error) {
      console.error("Registration failed", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setToken(null);
    setRefreshToken(null);
    setUser(null);
  };

  const hasRole = (role: string): boolean => {
    return user?.role === role || user?.role === "admin";
  };

  const value: AuthContextType = {
    user,
    token,
    refreshToken,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
