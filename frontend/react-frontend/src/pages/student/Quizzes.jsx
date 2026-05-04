import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/UseAuth";

export default function StudentQuizzes() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await apiFetch("/student/quizzes", { method: "GET", token });
        if (!cancelled) setQuizzes(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load quizzes.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="rounded-2xl border p-6">
      <h2 className="text-2xl font-bold">My Quizzes</h2>
      {error ? (
        <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      {quizzes.length === 0 ? (
        <p className="mt-2 text-gray-600">No quizzes assigned yet.</p>
      ) : (
        <ul className="mt-4 flex flex-col gap-3">
          {quizzes.map((q) => (
            <li key={q.id} className="rounded-xl border p-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="text-lg font-semibold">{q.title}</div>
                    {q.completed ? (
                      <span className="rounded-full border border-green-300 bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">
                        Completed
                      </span>
                    ) : null}
                  </div>
                  <div className="text-sm text-gray-600">
                    {q.classroom_name} • Grade {q.grade} {q.subject} • {q.question_count} questions
                  </div>
                  {q.completed_at ? (
                    <div className="text-xs text-green-700">
                      Completed on {new Date(q.completed_at).toLocaleString()}
                    </div>
                  ) : null}
                </div>
                <button
                  onClick={() => navigate(`/student/play?mode=quiz&quizId=${q.id}`)}
                  className="rounded-lg border border-blue-400 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-500 hover:text-white transition"
                >
                  {q.completed ? "Review Quiz" : "Start Quiz"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
