import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";
import { useNavigate } from "react-router-dom";

function Card({ title, children }) {
  return (
    <div className="rounded-2xl border p-5">
      <div className="mb-3 text-xl font-bold">{title}</div>
      {children}
    </div>
  );
}

export default function Overview() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setErr("");
        const q = await apiFetch("/student/quizzes", { token, method: "GET" });
        setQuizzes(Array.isArray(q) ? q : []);
      } catch (e) {
        setErr(e.message || "Could not load quizzes.");
        setQuizzes([]);
      }
    }
    load();
  }, [token]);

  return (
    <div className="flex flex-col gap-6">
      <button
        onClick={() => navigate("/student/play")}
        className="w-full rounded-2xl border border-blue-300 px-8 py-6 text-2xl font-extrabold transition hover:bg-blue-500 hover:text-white sm:w-fit"
      >
        Play Game
      </button>

      {err ? (
        <div className="rounded-xl border p-4 text-sm text-slate-800">
          {err}
        </div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        <Card title="My Quizzes">
          {quizzes.length === 0 ? (
            <div className="text-sm text-slate-600">No quizzes assigned yet.</div>
          ) : (
            <ul className="flex flex-col gap-3">
              {quizzes.slice(0, 5).map((quiz) => (
                <li key={quiz.id} className="rounded-xl border p-3">
                  <div className="text-lg font-semibold">{quiz.title}</div>
                  <div className="text-sm text-slate-600">
                    {quiz.classroom_name} • Grade {quiz.grade} {quiz.subject}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <button
            onClick={() => navigate("/student/quizzes")}
            className="mt-4 rounded-xl border border-blue-300 px-4 py-3 text-lg font-semibold transition hover:bg-blue-500 hover:text-white"
          >
            View all
          </button>
        </Card>

        <Card title="Game Flow">
          <div className="space-y-3 text-slate-700">
            <p>Use Play Game for grade-based practice from your classroom question bank.</p>
            <p>Use Quizzes to launch teacher-assigned quizzes directly in the game.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
