import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthProvider } from "./auth/AuthContext.jsx";
import { useAuth } from "./auth/UseAuth.jsx";
import Home from "./pages/home.jsx";
import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import StudentPage from "./pages/student.jsx";
import TeacherPage from "./pages/teacher.jsx";

function ProtectedRoleRoute({ role, children }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== role) {
    return <Navigate to={user.role === "teacher" ? "/teacher" : "/student"} replace />;
  }

  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={user ? <Navigate to={user.role === "teacher" ? "/teacher" : "/student"} replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to={user.role === "teacher" ? "/teacher" : "/student"} replace /> : <Register />} />
      <Route
        path="/student"
        element={
          <ProtectedRoleRoute role="student">
            <StudentPage />
          </ProtectedRoleRoute>
        }
      />
      <Route
        path="/teacher"
        element={
          <ProtectedRoleRoute role="teacher">
            <TeacherPage />
          </ProtectedRoleRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
