import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/UseAuth";

function BigNav({ to, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-xl px-4 py-4 text-lg font-semibold border transition
         ${isActive ? "bg-blue-500 text-white border-blue-500" : "border-blue-300 hover:bg-blue-500 hover:text-white text-black"}`
      }
    >
      {label}
    </NavLink>
  );
}

export default function TeacherLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const name =
    user?.first_name
      ? `${user.first_name}${user.last_name ? " " + user.last_name : ""}`
      : user?.email || "Teacher";

  return (
    <div className="min-h-screen flex bg-white">
      {/* Sidebar */}
      <aside className="w-72 p-4 border-r flex flex-col gap-4">
        <div className="text-2xl font-extrabold px-2">Teacher</div>
        <BigNav to="/teacher/overview" label="Overview" />
        <BigNav to="/teacher/assignments" label="Assignments" />
        <BigNav to="/teacher/quizzes" label="Quizzes" />
        <BigNav to="/teacher/classrooms" label="Classrooms" />
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {/* Top bar */}
        <header className="h-16 border-b flex items-center justify-between px-6">
          <div className="text-xl font-semibold">Hi, {name}</div>
          <button
            onClick={() => {
              logout();
              navigate("/");
            }}
            className="rounded-xl px-4 py-2 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Logout
          </button>
        </header>

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}