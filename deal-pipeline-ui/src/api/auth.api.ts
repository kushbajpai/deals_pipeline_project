import { api } from "./axios";
import type { AuthToken, User, LoginRequest, RegisterRequest } from "../types";

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthToken> => {
    const response = await api.post("/auth/login", credentials);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthToken> => {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<AuthToken> => {
    const response = await api.post("/auth/refresh", { refresh_token: refreshToken });
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post("/auth/change-password", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
