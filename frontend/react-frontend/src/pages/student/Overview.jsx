import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";
import { useNavigate } from "react-router-dom";

function Card({ title, children }) {
  return (
    <div className="rounded-2xl border p-5">
      <div className="text-xl font-bold mb-3">{title}</div>
      {children}
    </div>
  );
}

export default function Overview() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [assignments, setAssignments] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    // Replace endpoints once you confirm them
    async function load() {
      try {
        setErr("");
        // mock fallback if endpoints not ready
        const a = await apiFetch("/student/assignments", { token, method: "GET" });
        const q = await apiFetch("/student/quizzes", { token, method: "GET" });
        setAssignments(Array.isArray(a) ? a : []);
        setQuizzes(Array.isArray(q) ? q : []);
      } catch (e) {
        // fallback mock data so UI still works
        setErr(e.message);
        setAssignments([
          { id: 1, title: "Addition Practice", dueDate: "2026-02-20", status: "due" },
          { id: 2, title: "Subtraction Drill", dueDate: "2026-02-22", status: "due" },
        ]);
        setQuizzes([{ id: 11, title: "Week 3 Quiz", topic: "Math", status: "assigned" }]);
      }
    }
    load();
  }, [token]);

  return (
    <div className="flex flex-col gap-6">
      <button
        onClick={() => navigate("/student/play")}
        className="text-white rounded-2xl px-8 py-6 text-2xl font-extrabold border border-blue-300 hover:bg-blue-500 hover:text-white transition w-full sm:w-fit"
      >
        Play Game
      </button>

      {err ? (
        <div className="text-white rounded-xl border p-4 text-sm">
          Backend not connected yet: <span className="font-semibold">{err}</span>
          <div className="text-xs mt-1">Showing sample data for now.</div>
        </div>
      ) : null}

      <div className="text-white grid md:grid-cols-2 gap-6">
        <Card title="My Assignments">
          <ul className="flex flex-col gap-3">
            {assignments.slice(0, 5).map((a) => (
              <li key={a.id} className="rounded-xl border p-3">
                <div className="text-lg font-semibold">{a.title}</div>
                {a.dueDate ? <div className="text-sm">Due: {a.dueDate}</div> : null}
              </li>
            ))}
          </ul>
          <button
            onClick={() => navigate("/student/assignments")}
            className="mt-4 rounded-xl px-4 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            View all
          </button>
        </Card>

        <Card title="My Quizzes">
          <ul className="flex flex-col gap-3">
            {quizzes.slice(0, 5).map((q) => (
              <li key={q.id} className="rounded-xl border p-3">
                <div className="text-lg font-semibold">{q.title}</div>
                {q.topic ? <div className="text-sm">Topic: {q.topic}</div> : null}
              </li>
            ))}
          </ul>
          <button
            onClick={() => navigate("/student/quizzes")}
            className="mt-4 rounded-xl px-4 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            View all
          </button>
        </Card>
      </div>
    </div>
  );
}