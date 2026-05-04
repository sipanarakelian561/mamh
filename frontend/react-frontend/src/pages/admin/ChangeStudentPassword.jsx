import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

export default function AdminChangeStudentPassword() {
  const { token, user } = useAuth();
  const [students, setStudents] = useState([]);
  const [studentId, setStudentId] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.role !== "admin") {
      return;
    }

    async function loadStudents() {
      try {
        const data = await apiFetch("/admin/users?role=student", {
          method: "GET",
          token,
        });
        setStudents(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message || "Failed to load students.");
      }
    }

    loadStudents();
  }, [token, user?.role]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (user?.role !== "admin") {
      setError("Only school admins can change student passwords.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await apiFetch(`/admin/students/${studentId}/password`, {
        method: "POST",
        token,
        body: JSON.stringify({ new_password: newPassword }),
      });
      setSuccess("Student password updated.");
      setStudentId("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message || "Failed to update student password.");
    } finally {
      setLoading(false);
    }
  }

  if (user?.role !== "admin") {
    return (
      <div className="max-w-xl rounded-2xl border p-6">
        <h2 className="text-2xl font-bold">Change Student Password</h2>
        <p className="mt-2 text-gray-600">Only school admins can access this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-xl rounded-2xl border p-6">
      <h2 className="text-2xl font-bold">Change Student Password</h2>
      <p className="mt-2 text-gray-600">Reset a student password for your school only.</p>

      {error ? (
        <div className="mt-4 w-full rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {success ? (
        <div className="mt-4 w-full rounded-xl border border-green-300 bg-green-50 p-3 text-sm text-green-800">
          {success}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-4">
        <select
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          required
          className="w-full rounded-xl border border-blue-300 bg-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select student</option>
          {students.map((student) => (
            <option key={student.id} value={student.id}>
              {student.email} {student.grade_level ? `(Grade ${student.grade_level})` : ""}
            </option>
          ))}
        </select>

        <input
          type="password"
          placeholder="New password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          minLength={8}
          className="w-full rounded-xl border border-blue-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          type="password"
          placeholder="Confirm new password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          minLength={8}
          className="w-full rounded-xl border border-blue-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl border border-blue-300 px-6 py-3 text-lg font-semibold transition hover:bg-blue-500 hover:text-white disabled:opacity-60"
        >
          {loading ? "Updating..." : "Update Student Password"}
        </button>
      </form>
    </div>
  );
}
