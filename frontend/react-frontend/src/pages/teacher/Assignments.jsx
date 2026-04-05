import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

export default function TeacherAssignments() {
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [classroomId, setClassroomId] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadData() {
    setError("");
    try {
      const cls = await apiFetch("/teacher/classrooms", { token });
      setClassrooms(Array.isArray(cls) ? cls : []);
      const asn = await apiFetch("/teacher/assignments", { token });
      setAssignments(Array.isArray(asn) ? asn : []);
    } catch (err) {
      setError(err.message || "Failed to load assignments.");
    }
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const created = await apiFetch("/teacher/assignments", {
        method: "POST",
        token,
        body: JSON.stringify({
          classroom_id: Number(classroomId),
          title,
          content,
        }),
      });
      setAssignments((prev) => [created, ...prev]);
      setTitle("");
      setContent("");
    } catch (err) {
      setError(err.message || "Failed to create assignment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Assignments</div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Create Assignment</div>

        {error ? (
          <div className="mb-4 w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        ) : null}

        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <select
            value={classroomId}
            onChange={(e) => setClassroomId(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">Select classroom</option>
            {classrooms.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} (Grade {c.grade} {c.subject})
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Assignment title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <textarea
            placeholder="Assignment content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows={4}
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-fit rounded-xl px-6 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create Assignment"}
          </button>
        </form>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Existing Assignments</div>
        {assignments.length === 0 ? (
          <div className="text-gray-600 text-sm">No assignments yet.</div>
        ) : (
          <ul className="flex flex-col gap-3">
            {assignments.map((a) => (
              <li key={a.id} className="rounded-xl border p-3 text-sm">
                <div className="text-lg font-semibold">{a.title}</div>
                <div className="text-gray-600">
                  {a.classroom_name} • Grade {a.grade} {a.subject}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
