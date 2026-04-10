import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/UseAuth";

export default function StudentAssignments() {
  const { token } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await apiFetch("/student/assignments", { method: "GET", token });
        if (!cancelled) setAssignments(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load assignments.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="rounded-2xl border p-6">
      <h2 className="text-2xl font-bold">My Assignments</h2>
      {error ? (
        <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      {assignments.length === 0 ? (
        <p className="mt-2 text-gray-600">No assignments assigned yet.</p>
      ) : (
        <ul className="mt-4 flex flex-col gap-3">
          {assignments.map((a) => (
            <li key={a.id} className="rounded-xl border p-3">
              <div className="text-lg font-semibold">{a.title}</div>
              <div className="text-sm text-gray-600">
                {a.classroom_name} • Grade {a.grade} {a.subject}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
