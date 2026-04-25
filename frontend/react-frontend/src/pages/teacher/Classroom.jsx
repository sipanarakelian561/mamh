import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/UseAuth";

export default function TeacherClassrooms() {
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [name, setName] = useState("");
  const [grade, setGrade] = useState(3);
  const [subject, setSubject] = useState("math");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadClassrooms() {
    setError("");
    try {
      const data = await apiFetch("/teacher/classrooms", { token });
      setClassrooms(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load classrooms.");
    }
  }

  useEffect(() => {
    loadClassrooms();
    
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const created = await apiFetch("/teacher/classrooms", {
        method: "POST",
        token,
        body: JSON.stringify({
          name,
          grade: Number(grade),
          subject,
        }),
      });
      setClassrooms((prev) => [created, ...prev]);
      setName("");
    } catch (err) {
      setError(err.message || "Failed to create classroom.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Classrooms</div>

      {error ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-4">Create Classroom</div>
        <form onSubmit={handleCreate} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Classroom name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              type="number"
              min={1}
              max={12}
              value={grade}
              onChange={(e) => setGrade(e.target.value)}
              className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="math">Math</option>
              <option value="science">Science</option>
              <option value="reading">Reading</option>
              <option value="writing">Writing</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-fit rounded-xl px-6 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create Classroom"}
          </button>
        </form>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-4">My Classrooms</div>
        {classrooms.length === 0 ? (
          <div className="text-sm text-gray-600">No classrooms yet.</div>
        ) : (
          <ul className="flex flex-col gap-3">
            {classrooms.map((room) => (
              <li key={room.id} className="rounded-xl border p-4 flex flex-col gap-3">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <span className="text-lg font-semibold">{room.name}</span>
                  <span className="text-sm text-gray-600">
                    Grade {room.grade} • {room.subject}
                  </span>
                </div>
                <div className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-800">
                  Join code: <span className="font-mono font-bold">{room.join_code}</span>
                </div>
                <div className="text-sm text-gray-600">
                  Students: {room.members?.length ?? 0}
                </div>
                {room.members && room.members.length > 0 ? (
                  <div className="rounded-xl border bg-gray-50 p-3">
                    <div className="text-sm font-semibold text-gray-700 mb-2">
                      Student Progress
                    </div>
                    <div className="flex flex-col gap-2">
                      {room.members.map((member) => (
                        <div
                          key={member.student_id}
                          className="rounded-lg border bg-white p-3 text-sm"
                        >
                          <div className="font-semibold">
                            {member.first_name} {member.last_name}
                          </div>
                          <div className="text-gray-600">{member.email}</div>
                          <div className="text-gray-600">
                            Quizzes completed: {member.completed_quizzes_count ?? 0}
                          </div>
                          {member.completed_quizzes && member.completed_quizzes.length > 0 ? (
                            <div className="text-gray-600">
                              Latest quizzes:{" "}
                              {member.completed_quizzes
                                .slice(0, 3)
                                .map((quiz) => quiz.title)
                                .join(", ")}
                            </div>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
