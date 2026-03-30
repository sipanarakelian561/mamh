import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./UseAuth";

export default function ProtectedRoute() {
  const { token, loading } = useAuth();
  if (loading) return <div className="p-6 text-lg">Loading...</div>;
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}