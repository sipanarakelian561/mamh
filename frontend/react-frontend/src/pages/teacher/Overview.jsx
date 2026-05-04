import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

function Card({ title, children }) {
  return (
    <div className="rounded-2xl border border-blue-100 p-5">
      <div className="text-xl font-bold mb-3 text-slate-900">{title}</div>
      {children}
    </div>
  );
}

export default function TeacherOverview() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadClassrooms() {
      try {
        const data = await apiFetch("/teacher/classrooms", { token });
        if (active) {
          setClassrooms(Array.isArray(data) ? data : []);
          setError("");
        }
      } catch (err) {
        if (active) {
          setError(err.message || "Failed to load classrooms.");
        }
      }
    }

    loadClassrooms();
    const intervalId = window.setInterval(loadClassrooms, 15000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, [token]);

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold text-slate-900">Teacher Dashboard</div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Quick Actions">
          <div className="flex flex-col gap-4">
            <button
              onClick={() => navigate("/teacher/question-bank")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Question Bank
            </button>
            <button
              onClick={() => navigate("/teacher/quizzes")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Quizzes
            </button>
            <button
              onClick={() => navigate("/teacher/classrooms")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Classrooms
            </button>
          </div>
        </Card>

        <Card title="Classrooms">
          {error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}
          <div className="mb-3 rounded-xl border border-blue-100 p-3 text-lg text-slate-800">
            Active Classrooms: {classrooms.length}
          </div>
          {classrooms.length === 0 ? (
            <div className="rounded-xl border border-blue-100 p-3 text-sm text-slate-600">
              No classrooms yet.
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {classrooms.map((room) => (
                <li key={room.id} className="rounded-xl border border-blue-100 p-3 text-slate-800">
                  <div className="font-semibold">{room.name}</div>
                  <div className="text-sm text-slate-600">
                    Grade {room.grade} • {room.subject} • Students: {room.members?.length ?? 0}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
