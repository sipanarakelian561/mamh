import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

const emptyQuestion = () => ({
  prompt: "",
  answers: ["", "", "", ""],
  correct_index: 0,
});

export default function TeacherQuizzes() {
  const { token } = useAuth();
  const [classrooms, setClassrooms] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [classroomId, setClassroomId] = useState("");
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState([emptyQuestion()]);
  const [editingQuizId, setEditingQuizId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [deleteQuizId, setDeleteQuizId] = useState(null);

  const completionStats = useMemo(() => {
    const completionByQuiz = new Map();
    const completersByQuiz = new Map();
    const classroomStudentCounts = new Map();
    classrooms.forEach((room) => {
      const members = Array.isArray(room.members) ? room.members : [];
      classroomStudentCounts.set(room.id, members.length);
      members.forEach((member) => {
        const completed = Array.isArray(member.completed_quizzes) ? member.completed_quizzes : [];
        completed.forEach((quiz) => {
          completionByQuiz.set(quiz.id, (completionByQuiz.get(quiz.id) || 0) + 1);
          const list = completersByQuiz.get(quiz.id) || [];
          list.push({
            student_id: member.student_id,
            first_name: member.first_name,
            last_name: member.last_name,
            email: member.email,
          });
          completersByQuiz.set(quiz.id, list);
        });
      });
    });
    return { completionByQuiz, completersByQuiz, classroomStudentCounts };
  }, [classrooms]);

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
  }, []);

  function resetForm() {
    setEditingQuizId(null);
    setClassroomId("");
    setTitle("");
    setQuestions([emptyQuestion()]);
  }

  function updateQuestion(index, field, value) {
    setQuestions((prev) =>
      prev.map((question, i) => (i === index ? { ...question, [field]: value } : question)),
    );
  }

  function updateAnswer(questionIndex, answerIndex, value) {
    setQuestions((prev) =>
      prev.map((question, i) =>
        i === questionIndex
          ? {
              ...question,
              answers: question.answers.map((answer, j) => (j === answerIndex ? value : answer)),
            }
          : question,
      ),
    );
  }

  function addQuestion() {
    setQuestions((prev) => [...prev, emptyQuestion()]);
  }

  function removeQuestion(index) {
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  }

  function beginEdit(quiz) {
    setEditingQuizId(quiz.id);
    setClassroomId(String(quiz.classroom_id));
    setTitle(quiz.title);
    setQuestions(
      Array.isArray(quiz.questions) && quiz.questions.length > 0
        ? quiz.questions.map((question) => ({
            prompt: question.prompt,
            answers: Array.isArray(question.answers)
              ? question.answers.map((answer) => answer ?? "")
              : ["", "", "", ""],
            correct_index: question.correct_index ?? 0,
          }))
        : [emptyQuestion()],
    );
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        classroom_id: Number(classroomId),
        title,
        questions: questions
          .filter((question) => question.prompt.trim())
          .map((question) => ({
            prompt: question.prompt.trim(),
            answers: question.answers.map((answer) => answer.trim()),
            correct_index: Number(question.correct_index),
          })),
      };

      const method = editingQuizId ? "PATCH" : "POST";
      const path = editingQuizId ? `/teacher/quizzes/${editingQuizId}` : "/teacher/quizzes";
      const saved = await apiFetch(path, {
        method,
        token,
        body: JSON.stringify(payload),
      });

      if (editingQuizId) {
        setQuizzes((prev) => prev.map((quiz) => (quiz.id === editingQuizId ? saved : quiz)));
      } else {
        setQuizzes((prev) => [saved, ...prev]);
      }
      resetForm();
    } catch (err) {
      setError(err.message || "Failed to save quiz.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteQuiz(quizId) {
    setError("");
    setDeleteQuizId(quizId);
    try {
      await apiFetch(`/teacher/quizzes/${quizId}`, {
        method: "DELETE",
        token,
      });
      setQuizzes((prev) => prev.filter((quiz) => quiz.id !== quizId));
      if (editingQuizId === quizId) {
        resetForm();
      }
    } catch (err) {
      setError(err.message || "Failed to delete quiz.");
    } finally {
      setDeleteQuizId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Quizzes / Problem Sets</div>

      <div className="rounded-2xl border p-5">
        <div className="mb-2 text-xl font-bold">{editingQuizId ? "Update Quiz" : "Create Quiz"}</div>

        {error ? (
          <div className="mb-4 w-full rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <select
            value={classroomId}
            onChange={(e) => setClassroomId(e.target.value)}
            required
            className="w-full rounded-xl border border-blue-300 bg-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select classroom</option>
            {classrooms.map((classroom) => (
              <option key={classroom.id} value={classroom.id}>
                {classroom.name} (Grade {classroom.grade} {classroom.subject})
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Quiz title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full rounded-xl border border-blue-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="flex flex-col gap-3">
            {questions.map((question, index) => (
              <div key={index} className="rounded-xl border p-3">
                <div className="mb-3 flex items-center justify-between">
                  <div className="font-semibold">Question {index + 1}</div>
                  {questions.length > 1 ? (
                    <button
                      type="button"
                      onClick={() => removeQuestion(index)}
                      className="text-sm font-semibold text-red-600 hover:underline"
                    >
                      Remove
                    </button>
                  ) : null}
                </div>

                <div className="flex flex-col gap-3">
                  <input
                    type="text"
                    placeholder="Question prompt"
                    value={question.prompt}
                    onChange={(e) => updateQuestion(index, "prompt", e.target.value)}
                    required
                    className="w-full rounded-xl border border-blue-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />

                  <div className="grid gap-3 md:grid-cols-2">
                    {question.answers.map((answer, answerIndex) => (
                      <input
                        key={answerIndex}
                        type="text"
                        placeholder={`Answer ${answerIndex + 1}`}
                        value={answer}
                        onChange={(e) => updateAnswer(index, answerIndex, e.target.value)}
                        required
                        className="w-full rounded-xl border border-blue-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    ))}
                  </div>

                  <select
                    value={question.correct_index}
                    onChange={(e) => updateQuestion(index, "correct_index", Number(e.target.value))}
                    className="w-full rounded-xl border border-blue-300 bg-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {[0, 1, 2, 3].map((answerIndex) => (
                      <option key={answerIndex} value={answerIndex}>
                        Correct answer #{answerIndex + 1}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={addQuestion}
              className="w-full rounded-xl border border-blue-300 px-4 py-2 text-sm font-semibold transition hover:bg-blue-500 hover:text-white sm:w-fit"
            >
              Add Question
            </button>
            {editingQuizId ? (
              <button
                type="button"
                onClick={resetForm}
                className="w-full rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold transition hover:bg-slate-100 sm:w-fit"
              >
                Cancel
              </button>
            ) : null}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl border border-blue-300 px-6 py-3 text-lg font-semibold transition hover:bg-blue-500 hover:text-white disabled:opacity-60 sm:w-fit"
          >
            {loading ? "Saving..." : editingQuizId ? "Update Quiz" : "Create Quiz"}
          </button>
        </form>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="mb-2 text-xl font-bold">My Quizzes</div>
        {quizzes.length === 0 ? (
          <div className="text-sm text-gray-600">No quizzes yet.</div>
        ) : (
          <ul className="flex flex-col gap-3">
            {quizzes.map((quiz) => {
              const completedCount = completionStats.completionByQuiz.get(quiz.id) ?? 0;
              const totalStudents = completionStats.classroomStudentCounts.get(quiz.classroom_id) ?? 0;
              const completers = completionStats.completersByQuiz.get(quiz.id) ?? [];
              return (
                <li key={quiz.id} className="rounded-xl border p-3 text-sm">
                  <div className="mb-2 flex items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-semibold">{quiz.title}</div>
                      <div className="text-gray-600">
                        {quiz.classroom_name} • Grade {quiz.grade} {quiz.subject} •{" "}
                        {quiz.questions?.length ?? quiz.question_count} questions
                      </div>
                      <div className="text-gray-600">
                        {totalStudents > 0
                          ? `Completed by ${completedCount}/${totalStudents} students`
                          : "No students yet"}
                      </div>
                      {completers.length > 0 ? (
                        <div className="mt-1 text-gray-500">
                          Completed by:{" "}
                          {completers
                            .map((student) =>
                              [student.first_name, student.last_name].filter(Boolean).join(" ").trim() || student.email,
                            )
                            .join(", ")}
                        </div>
                      ) : null}
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => beginEdit(quiz)}
                        className="rounded-lg border border-blue-300 px-3 py-2 text-sm font-semibold transition hover:bg-blue-500 hover:text-white"
                      >
                        Update
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteQuiz(quiz.id)}
                        disabled={deleteQuizId === quiz.id}
                        className="rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-60"
                      >
                        {deleteQuizId === quiz.id ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
