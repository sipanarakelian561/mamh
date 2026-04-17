import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import Home from "./pages/home.jsx";
import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import { AuthProvider } from "./auth/AuthContext.jsx";
import ProtectedRoute from "./auth/ProtectedRoute.jsx";
import RoleRoute from "./auth/RoleRoute.jsx";

import StudentLayout from "./layouts/Studentlayout.jsx";
import TeacherLayout from "./layouts/Teacherlayout.jsx";
import AdminLayout from "./layouts/AdminLayout.jsx";
import StudentOverview from "./pages/student/Overview.jsx";
import StudentAssignments from "./pages/student/Assignments.jsx";
import StudentQuizzes from "./pages/student/Quizzes.jsx";
import StudentPlay from "./pages/student/Play.jsx";
import StudentJoin from "./pages/student/Join.jsx";
import TeacherOverview from "./pages/teacher/Overview.jsx";
import TeacherAssignments from "./pages/teacher/Assignments.jsx";
import TeacherQuizzes from "./pages/teacher/Quizzes.jsx";
import TeacherClassroom from "./pages/teacher/Classroom.jsx";
import TeacherChangePassword from "./pages/teacher/ChangePassword.jsx";
import AdminOverview from "./pages/admin/Overview.jsx";
import AdminChangePassword from "./pages/admin/ChangePassword.jsx";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<RoleRoute role="student" />}>
                <Route path="/student" element={<StudentLayout />}>
                  <Route index element={<Navigate to="overview" replace />} />
                  <Route path="overview" element={<StudentOverview />} />
                  <Route path="assignments" element={<StudentAssignments />} />
                  <Route path="quizzes" element={<StudentQuizzes />} />
                  <Route path="play" element={<StudentPlay />} />
                  <Route path="join" element={<StudentJoin />} />
                </Route>
              </Route>

              <Route element={<RoleRoute role="teacher" />}>
                <Route path="/teacher" element={<TeacherLayout />}>
                  <Route index element={<Navigate to="overview" replace />} />
                  <Route path="overview" element={<TeacherOverview />} />
                  <Route path="assignments" element={<TeacherAssignments />} />
                  <Route path="quizzes" element={<TeacherQuizzes />} />
                  <Route path="classrooms" element={<TeacherClassroom />} />
                  <Route path="password" element={<TeacherChangePassword />} />
                </Route>
              </Route>

              {/* Admin routes */}
              <Route element={<RoleRoute roles={["admin", "super_admin"]} />}>
                <Route path="/admin" element={<AdminLayout />}>
                  <Route index element={<Navigate to="overview" replace />} />
                  <Route path="overview" element={<AdminOverview />} />
                  <Route path="password" element={<AdminChangePassword />} />
                </Route>
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}