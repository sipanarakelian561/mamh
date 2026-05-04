import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

const GRADE_OPTIONS = [1, 2, 3, 4, 5, 6];
const SUBJECT_OPTIONS = ["math", "english"];
const DEFAULT_FORM = {
  grade: 1,
  subject: "math",
  difficulty: "easy",
  prompt: "",
  answers: ["", "", "", ""],
  correct_index: 0,
  active: true,
};

export default function TeacherQuestionBank() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [filterGrade, setFilterGrade] = useState("");
  const [filterSubject, setFilterSubject] = useState("");
  const [form, setForm] = useState(DEFAULT_FORM);
  const [editingId, setEditingId] = useState(null);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      if (filterGrade && item.grade !== Number(filterGrade)) return false;
      if (filterSubject && item.subject !== filterSubject) return false;
      return true;
    });
  }, [items, filterGrade, filterSubject]);

  async function loadItems() {
    setError("");
    try {
      const data = await apiFetch("/teacher/question-bank", { token });
      setItems(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load question bank.");
    }
  }

  useEffect(() => {
    loadItems();
  }, []);

  function updateAnswer(index, value) {
    setForm((prev) => ({
      ...prev,
      answers: prev.answers.map((answer, i) => (i === index ? value : answer)),
    }));
  }

  function resetForm() {
    setForm(DEFAULT_FORM);
    setEditingId(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        grade: Number(form.grade),
        correct_index: Number(form.correct_index),
        subject: form.subject.toLowerCase(),
        answers: form.answers.map((answer) => answer.trim()),
      };
      if (editingId) {
        const updated = await apiFetch(`/teacher/question-bank/${editingId}`, {
          method: "PATCH",
          token,
          body: JSON.stringify(payload),
        });
        setItems((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await apiFetch("/teacher/question-bank", {
          method: "POST",
          token,
          body: JSON.stringify(payload),
        });
        setItems((prev) => [created, ...prev]);
      }
      resetForm();
    } catch (err) {
      setError(err.message || "Failed to save question.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    try {
      await apiFetch(`/teacher/question-bank/${id}`, {
        method: "DELETE",
        token,
      });
      setItems((prev) => prev.filter((item) => item.id !== id));
      if (editingId === id) resetForm();
    } catch (err) {
      setError(err.message || "Failed to delete question.");
    }
  }

  function beginEdit(item) {
    setEditingId(item.id);
    setForm({
      grade: item.grade,
      subject: item.subject,
      difficulty: item.difficulty,
      prompt: item.prompt,
      answers: [...item.answers],
      correct_index: item.correct_index,
      active: item.active,
    });
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Question Bank</div>

      {error ? (
        <div className="rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="rounded-2xl border p-5">
        <div className="mb-4 text-xl font-bold">
          {editingId ? "Update Question" : "Add Question"}
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid gap-4 md:grid-cols-4">
            <select
              value={form.grade}
              onChange={(e) => setForm((prev) => ({ ...prev, grade: Number(e.target.value) }))}
              className="rounded-xl border border-blue-300 p-3"
            >
              {GRADE_OPTIONS.map((grade) => (
                <option key={grade} value={grade}>
                  Grade {grade}
                </option>
              ))}
            </select>
            <select
              value={form.subject}
              onChange={(e) => setForm((prev) => ({ ...prev, subject: e.target.value }))}
              className="rounded-xl border border-blue-300 p-3"
            >
              {SUBJECT_OPTIONS.map((subject) => (
                <option key={subject} value={subject}>
                  {subject.charAt(0).toUpperCase() + subject.slice(1)}
                </option>
              ))}
            </select>
            <input
              value={form.difficulty}
              onChange={(e) => setForm((prev) => ({ ...prev, difficulty: e.target.value }))}
              className="rounded-xl border border-blue-300 p-3"
              placeholder="Difficulty"
            />
            <select
              value={form.correct_index}
              onChange={(e) => setForm((prev) => ({ ...prev, correct_index: Number(e.target.value) }))}
              className="rounded-xl border border-blue-300 p-3"
            >
              {[0, 1, 2, 3].map((idx) => (
                <option key={idx} value={idx}>
                  Correct answer #{idx + 1}
                </option>
              ))}
            </select>
          </div>

          <textarea
            value={form.prompt}
            onChange={(e) => setForm((prev) => ({ ...prev, prompt: e.target.value }))}
            className="min-h-28 rounded-xl border border-blue-300 p-3"
            placeholder="Question prompt"
            required
          />

          <div className="grid gap-4 md:grid-cols-2">
            {form.answers.map((answer, index) => (
              <input
                key={index}
                value={answer}
                onChange={(e) => updateAnswer(index, e.target.value)}
                className="rounded-xl border border-blue-300 p-3"
                placeholder={`Answer ${index + 1}`}
                required
              />
            ))}
          </div>

          <label className="flex items-center gap-2 text-sm font-medium">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm((prev) => ({ ...prev, active: e.target.checked }))}
            />
            Active
          </label>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl border border-blue-300 px-6 py-3 text-lg font-semibold transition hover:bg-blue-500 hover:text-white disabled:opacity-60"
            >
              {loading ? "Saving..." : editingId ? "Update Question" : "Create Question"}
            </button>
            {editingId ? (
              <button
                type="button"
                onClick={resetForm}
                className="rounded-xl border border-slate-300 px-6 py-3 text-lg font-semibold transition hover:bg-slate-100"
              >
                Cancel
              </button>
            ) : null}
          </div>
        </form>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="text-xl font-bold">My Questions</div>
          <div className="flex gap-3">
            <select
              value={filterGrade}
              onChange={(e) => setFilterGrade(e.target.value)}
              className="rounded-xl border border-blue-300 p-3"
            >
              <option value="">All grades</option>
              {GRADE_OPTIONS.map((grade) => (
                <option key={grade} value={grade}>
                  Grade {grade}
                </option>
              ))}
            </select>
            <select
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              className="rounded-xl border border-blue-300 p-3"
            >
              <option value="">All subjects</option>
              {SUBJECT_OPTIONS.map((subject) => (
                <option key={subject} value={subject}>
                  {subject.charAt(0).toUpperCase() + subject.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          {filteredItems.length === 0 ? (
            <div className="text-sm text-slate-600">No questions found.</div>
          ) : (
            filteredItems.map((item) => (
              <div key={item.id} className="rounded-xl border p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-lg font-semibold">{item.prompt}</div>
                    <div className="text-sm text-slate-600">
                      Grade {item.grade} • {item.subject} • {item.difficulty} •{" "}
                      {item.active ? "Active" : "Inactive"}
                    </div>
                    <ol className="mt-2 list-decimal pl-5 text-sm text-slate-700">
                      {item.answers.map((answer, index) => (
                        <li key={index}>
                          {answer}
                          {index === item.correct_index ? " (correct)" : ""}
                        </li>
                      ))}
                    </ol>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => beginEdit(item)}
                      className="rounded-lg border border-blue-300 px-3 py-2 text-sm font-semibold transition hover:bg-blue-500 hover:text-white"
                    >
                      Update
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(item.id)}
                      className="rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
