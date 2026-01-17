import { api } from "./axios";
import type { User } from "../types";

export interface UserWithRole extends User {
  role: "admin" | "analyst" | "partner";
}

export const usersAPI = {
  // Get all users
  getAll: async (): Promise<UserWithRole[]> => {
    const response = await api.get("/users");
    return response.data;
  },

  // Get a specific user by ID
  getById: async (id: number): Promise<UserWithRole> => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  // Update user role
  updateRole: async (userId: number, newRole: "admin" | "analyst" | "partner"): Promise<UserWithRole> => {
    const response = await api.put(`/users/${userId}/role`, { role: newRole });
    return response.data;
  },

  // Delete a user (admin only)
  deleteUser: async (userId: number): Promise<void> => {
    await api.delete(`/users/${userId}`);
  },

  // Activate/deactivate user
  toggleActive: async (userId: number, isActive: boolean): Promise<UserWithRole> => {
    const response = await api.put(`/users/${userId}`, { is_active: isActive });
    return response.data;
  },
};
