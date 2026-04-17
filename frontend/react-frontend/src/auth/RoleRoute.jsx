import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./UseAuth.jsx";

export default function RoleRoute({ role, roles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const allowedRoles = roles || (role ? [role] : null);
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
