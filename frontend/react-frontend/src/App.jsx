import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import Home from "./pages/home.jsx";
import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import { AuthProvider } from "./auth/AuthContext.jsx";
import ProtectedRoute from "./auth/ProtectedRoute.jsx";
import RoleRoute from "./auth/RoleRoute.jsx";

import StudentPage from "./pages/student.jsx";
import TeacherPage from "./pages/teacher.jsx";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            {/* Student routes */}
            <Route element={<RoleRoute role="student" />}>
              <Route path="/student" element={<StudentPage />} />
            </Route>

            {/* Teacher routes */}
            <Route element={<RoleRoute role="teacher" />}>
              <Route path="/teacher" element={<TeacherPage />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
