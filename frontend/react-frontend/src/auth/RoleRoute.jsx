import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./UseAuth";

export default function RoleRoute({ role }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-6 text-lg">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to="/" replace />;
  return <Outlet />;
}