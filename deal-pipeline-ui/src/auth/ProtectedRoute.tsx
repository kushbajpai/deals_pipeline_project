import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export const ProtectedRoute = ({ roles, children }: any) => {
  const { token, user } = useAuth();

  if (!token) return <Navigate to="/login" />;

  if (roles && user) {
    const userRole = user.role?.toLowerCase() || "";
    const hasRole = roles.some((role: string) => role.toLowerCase() === userRole);
    if (!hasRole) {
      return <Navigate to="/unauthorized" />;
    }
  }

  return children;
};
