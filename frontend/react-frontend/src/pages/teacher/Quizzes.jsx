import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

export default function TeacherQuizzes() {
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [classroomId, setClassroomId] = useState("");
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState([{ prompt: "", answer: "" }]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadData() {
    setError("");
    try {
      const cls = await apiFetch("/teacher/classrooms", { token });
      setClassrooms(Array.isArray(cls) ? cls : []);
      const qz = await apiFetch("/teacher/quizzes", { token });
      setQuizzes(Array.isArray(qz) ? qz : []);
    } catch (err) {
      setError(err.message || "Failed to load quizzes.");
    }
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updateQuestion(idx, field, value) {
    setQuestions((prev) =>
      prev.map((q, i) => (i === idx ? { ...q, [field]: value } : q))
    );
  }

  function addQuestion() {
    setQuestions((prev) => [...prev, { prompt: "", answer: "" }]);
  }

  function removeQuestion(idx) {
    setQuestions((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        classroom_id: Number(classroomId),
        title,
        questions: questions
          .filter((q) => q.prompt.trim())
          .map((q) => ({ prompt: q.prompt, answer: q.answer })),
      };
      const created = await apiFetch("/teacher/quizzes", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      });
      setQuizzes((prev) => [created, ...prev]);
      setTitle("");
      setQuestions([{ prompt: "", answer: "" }]);
    } catch (err) {
      setError(err.message || "Failed to create quiz.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Quizzes / Problem Sets</div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Create Quiz</div>

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
            placeholder="Quiz title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="flex flex-col gap-3">
            {questions.map((q, idx) => (
              <div key={idx} className="rounded-xl border p-3">
                <div className="flex flex-col gap-2">
                  <input
                    type="text"
                    placeholder={`Question ${idx + 1}`}
                    value={q.prompt}
                    onChange={(e) => updateQuestion(idx, "prompt", e.target.value)}
                    required
                    className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    placeholder="Answer (optional)"
                    value={q.answer}
                    onChange={(e) => updateQuestion(idx, "answer", e.target.value)}
                    className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {questions.length > 1 ? (
                  <button
                    type="button"
                    onClick={() => removeQuestion(idx)}
                    className="mt-3 text-sm font-semibold text-red-600 hover:underline"
                  >
                    Remove question
                  </button>
                ) : null}
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addQuestion}
            className="w-full sm:w-fit rounded-xl px-4 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Add Question
          </button>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-fit rounded-xl px-6 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create Quiz"}
          </button>
        </form>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">My Quizzes</div>
        {quizzes.length === 0 ? (
          <div className="text-gray-600 text-sm">No quizzes yet.</div>
        ) : (
          <ul className="flex flex-col gap-3">
            {quizzes.map((q) => (
              <li key={q.id} className="rounded-xl border p-3 text-sm">
                <div className="text-lg font-semibold">{q.title}</div>
                <div className="text-gray-600">
                  {q.classroom_name} • Grade {q.grade} {q.subject} • {q.questions?.length ?? q.question_count}{" "}
                  questions
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
