import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/UseAuth";

export default function TeacherClassrooms() {
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [name, setName] = useState("");
  const [grade, setGrade] = useState(3);
  const [subject, setSubject] = useState("math");
  const [editingRoomId, setEditingRoomId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editGrade, setEditGrade] = useState(3);
  const [editSubject, setEditSubject] = useState("math");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

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

  function startEditing(room) {
    setEditingRoomId(room.id);
    setEditName(room.name);
    setEditGrade(room.grade);
    setEditSubject(room.subject);
  }

  function cancelEditing() {
    setEditingRoomId(null);
    setEditName("");
    setEditGrade(3);
    setEditSubject("math");
  }

  async function handleUpdate(roomId) {
    setError("");
    setActionLoading(true);
    try {
      const updated = await apiFetch(`/teacher/classrooms/${roomId}`, {
        method: "PATCH",
        token,
        body: JSON.stringify({
          name: editName,
          grade: Number(editGrade),
          subject: editSubject,
        }),
      });
      setClassrooms((prev) =>
        prev.map((room) => (room.id === roomId ? { ...room, ...updated } : room))
      );
      cancelEditing();
    } catch (err) {
      setError(err.message || "Failed to update classroom.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDelete(roomId) {
    setError("");
    setActionLoading(true);
    try {
      await apiFetch(`/teacher/classrooms/${roomId}`, {
        method: "DELETE",
        token,
      });
      setClassrooms((prev) => prev.filter((room) => room.id !== roomId));
      if (editingRoomId === roomId) {
        cancelEditing();
      }
    } catch (err) {
      setError(err.message || "Failed to delete classroom.");
    } finally {
      setActionLoading(false);
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
              <option value="english">English</option>
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
                  {editingRoomId === room.id ? (
                    <div className="grid w-full gap-3 sm:grid-cols-3">
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="number"
                        min={1}
                        max={12}
                        value={editGrade}
                        onChange={(e) => setEditGrade(e.target.value)}
                        className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <select
                        value={editSubject}
                        onChange={(e) => setEditSubject(e.target.value)}
                        className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                      >
                        <option value="math">Math</option>
                        <option value="english">English</option>
                      </select>
                    </div>
                  ) : (
                    <>
                      <span className="text-lg font-semibold">{room.name}</span>
                      <span className="text-sm text-gray-600">
                        Grade {room.grade} • {room.subject}
                      </span>
                    </>
                  )}
                </div>
                <div className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-800">
                  Join code: <span className="font-mono font-bold">{room.join_code}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {editingRoomId === room.id ? (
                    <>
                      <button
                        type="button"
                        onClick={() => handleUpdate(room.id)}
                        disabled={actionLoading}
                        className="rounded-xl px-4 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
                      >
                        {actionLoading ? "Saving..." : "Save"}
                      </button>
                      <button
                        type="button"
                        onClick={cancelEditing}
                        disabled={actionLoading}
                        className="rounded-xl px-4 py-2 text-sm font-semibold border border-gray-300 hover:bg-gray-100 transition disabled:opacity-60"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={() => startEditing(room)}
                        disabled={actionLoading}
                        className="rounded-xl px-4 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
                      >
                        Update
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(room.id)}
                        disabled={actionLoading}
                        className="rounded-xl px-4 py-2 text-sm font-semibold border border-red-300 text-red-600 hover:bg-red-500 hover:text-white transition disabled:opacity-60"
                      >
                        Delete
                      </button>
                    </>
                  )}
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
