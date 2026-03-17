import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import { useAuth } from "../auth/UseAuth";

const SUBJECTS = ["math", "science", "reading", "writing"];
const GRADES = Array.from({ length: 12 }, (_, idx) => idx + 1);

function SubjectBadge({ subject }) {
  return (
    <span className="inline-flex rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-800">
      {subject}
    </span>
  );
}

export default function TeacherPage() {
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const [activeTab, setActiveTab] = useState("assignments");
  const [assignments, setAssignments] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  const [assignmentForm, setAssignmentForm] = useState({
    classroom_id: "",
    title: "",
    content: "",
  });
  const [quizForm, setQuizForm] = useState({
    classroom_id: "",
    title: "",
    questions: [{ prompt: "", answer: "" }],
  });
  const [classroomForm, setClassroomForm] = useState({
    name: "",
    grade: 3,
    subject: "math",
  });

  const tabs = useMemo(
    () => [
      { id: "assignments", label: "Assignments" },
      { id: "quizzes", label: "Quizzes" },
      { id: "classrooms", label: "Classrooms" },
    ],
    []
  );

  async function fetchDashboardData() {
    return Promise.all([
      apiFetch("/teacher/assignments", { method: "GET", token }),
      apiFetch("/teacher/quizzes", { method: "GET", token }),
      apiFetch("/teacher/classrooms", { method: "GET", token }),
    ]);
  }

  async function loadDashboardData() {
    const [assignmentRows, quizRows, classroomRows] = await fetchDashboardData();
    const classroomList = classroomRows || [];

    setAssignments(assignmentRows || []);
    setQuizzes(quizRows || []);
    setClassrooms(classroomList);

    if (!assignmentForm.classroom_id && classroomList[0]) {
      setAssignmentForm((prev) => ({ ...prev, classroom_id: String(classroomList[0].id) }));
    }
    if (!quizForm.classroom_id && classroomList[0]) {
      setQuizForm((prev) => ({ ...prev, classroom_id: String(classroomList[0].id) }));
    }
  }

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const [assignmentRows, quizRows, classroomRows] = await fetchDashboardData();
        if (cancelled) return;

        const classroomList = classroomRows || [];
        setAssignments(assignmentRows || []);
        setQuizzes(quizRows || []);
        setClassrooms(classroomList);

        if (classroomList[0]) {
          setAssignmentForm((prev) =>
            prev.classroom_id ? prev : { ...prev, classroom_id: String(classroomList[0].id) }
          );
          setQuizForm((prev) =>
            prev.classroom_id ? prev : { ...prev, classroom_id: String(classroomList[0].id) }
          );
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load teacher dashboard.");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function createAssignment(e) {
    e.preventDefault();
    setError("");
    setStatus("");

    try {
      await apiFetch("/teacher/assignments", {
        method: "POST",
        token,
        body: JSON.stringify({
          classroom_id: Number(assignmentForm.classroom_id),
          title: assignmentForm.title,
          content: assignmentForm.content,
        }),
      });
      setAssignmentForm((prev) => ({ ...prev, title: "", content: "" }));
      setStatus("Assignment created and assigned to classroom.");
      await loadDashboardData();
    } catch (err) {
      setError(err.message || "Could not create assignment.");
    }
  }

  async function createQuiz(e) {
    e.preventDefault();
    setError("");
    setStatus("");

    const cleanQuestions = quizForm.questions
      .map((q) => ({ prompt: q.prompt.trim(), answer: q.answer.trim() }))
      .filter((q) => q.prompt && q.answer);

    if (cleanQuestions.length === 0) {
      setError("Add at least one question with both prompt and correct answer.");
      return;
    }

    try {
      await apiFetch("/teacher/quizzes", {
        method: "POST",
        token,
        body: JSON.stringify({
          classroom_id: Number(quizForm.classroom_id),
          title: quizForm.title,
          questions: cleanQuestions,
        }),
      });
      setQuizForm((prev) => ({ ...prev, title: "", questions: [{ prompt: "", answer: "" }] }));
      setStatus("Quiz created and assigned to classroom.");
      await loadDashboardData();
    } catch (err) {
      setError(err.message || "Could not create quiz.");
    }
  }

  async function createClassroom(e) {
    e.preventDefault();
    setError("");
    setStatus("");

    try {
      const created = await apiFetch("/teacher/classrooms", {
        method: "POST",
        token,
        body: JSON.stringify(classroomForm),
      });
      setClassroomForm((prev) => ({ ...prev, name: "" }));
      setStatus(`Classroom created. Join code: ${created.join_code}`);
      await loadDashboardData();
      setAssignmentForm((prev) => ({ ...prev, classroom_id: String(created.id) }));
      setQuizForm((prev) => ({ ...prev, classroom_id: String(created.id) }));
    } catch (err) {
      setError(err.message || "Could not create classroom.");
    }
  }

  return (
    <div className="min-h-screen w-full bg-slate-50 p-3 md:p-6">
      <div className="flex min-h-[calc(100vh-1.5rem)] w-full flex-col gap-4 md:min-h-[calc(100vh-3rem)] md:flex-row">
        <aside className="w-full rounded-2xl border border-blue-200 bg-white p-4 md:w-72 md:shrink-0">
          <div className="mb-4 text-xl font-extrabold text-slate-900">Teacher Dashboard</div>
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Navigation</div>
          <div className="flex flex-row gap-2 md:flex-col">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`rounded-xl border px-3 py-2 text-left text-sm font-semibold transition ${
                  activeTab === tab.id
                    ? "border-blue-500 bg-blue-500 text-white"
                    : "border-blue-200 bg-white text-slate-800 hover:bg-blue-50"
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <button className="mt-6 w-full rounded-xl border border-blue-200 px-3 py-2 text-sm font-semibold text-slate-800 hover:bg-blue-50" onClick={() => navigate("/")}>Return</button>
          <button
            className="mt-2 w-full rounded-xl border border-blue-200 px-3 py-2 text-sm font-semibold text-slate-800 hover:bg-blue-50"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Log Out
          </button>
        </aside>

        <main className="flex-1 rounded-2xl border border-blue-200 bg-white p-4 md:p-6 md:overflow-auto">
          {error && <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          {status && <div className="mb-4 rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-800">{status}</div>}

          {activeTab === "assignments" && (
            <section>
              <h2 className="mb-4 text-2xl font-bold text-slate-900">Create Assignment</h2>
              <form onSubmit={createAssignment} className="mb-6 grid gap-3 rounded-xl border border-blue-100 bg-slate-50 p-4">
                {classrooms.length === 0 && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">Create a classroom first before assigning work.</div>
                )}
                <label className="text-sm font-semibold text-slate-700">
                  Classroom
                  <select
                    value={assignmentForm.classroom_id}
                    onChange={(e) => setAssignmentForm((prev) => ({ ...prev, classroom_id: e.target.value }))}
                    className="mt-1 w-full rounded-xl border border-blue-200 p-3"
                    disabled={classrooms.length === 0}
                  >
                    {classrooms.map((c) => (
                      <option key={c.id} value={c.id}>{c.name} | Grade {c.grade} | {c.subject}</option>
                    ))}
                  </select>
                </label>
                <input type="text" placeholder="Assignment title" value={assignmentForm.title} onChange={(e) => setAssignmentForm((prev) => ({ ...prev, title: e.target.value }))} required className="w-full rounded-xl border border-blue-200 p-3" />
                <textarea placeholder="Assignment instructions" value={assignmentForm.content} onChange={(e) => setAssignmentForm((prev) => ({ ...prev, content: e.target.value }))} required rows={4} className="w-full rounded-xl border border-blue-200 p-3" />
                <button type="submit" disabled={classrooms.length === 0} className="rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white disabled:opacity-50">Create Assignment</button>
              </form>

              <h3 className="mb-3 text-lg font-bold text-slate-900">Created Assignments</h3>
              <div className="space-y-2">
                {assignments.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">No assignments yet.</div>}
                {assignments.map((assignment) => (
                  <article key={assignment.id} className="rounded-xl border border-blue-100 p-3">
                    <div className="mb-2 flex flex-wrap items-center gap-2 text-sm"><span className="font-semibold text-slate-900">{assignment.classroom_name}</span><span className="text-slate-600">Grade {assignment.grade}</span><SubjectBadge subject={assignment.subject} /></div>
                    <div className="font-semibold text-slate-900">{assignment.title}</div>
                    <p className="mt-1 text-sm text-slate-700">{assignment.content}</p>
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === "quizzes" && (
            <section>
              <h2 className="mb-4 text-2xl font-bold text-slate-900">Create Quiz</h2>
              <form onSubmit={createQuiz} className="mb-6 grid gap-3 rounded-xl border border-blue-100 bg-slate-50 p-4">
                {classrooms.length === 0 && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">Create a classroom first before assigning quizzes.</div>
                )}
                <label className="text-sm font-semibold text-slate-700">
                  Classroom
                  <select
                    value={quizForm.classroom_id}
                    onChange={(e) => setQuizForm((prev) => ({ ...prev, classroom_id: e.target.value }))}
                    className="mt-1 w-full rounded-xl border border-blue-200 p-3"
                    disabled={classrooms.length === 0}
                  >
                    {classrooms.map((c) => (
                      <option key={c.id} value={c.id}>{c.name} | Grade {c.grade} | {c.subject}</option>
                    ))}
                  </select>
                </label>
                <input type="text" placeholder="Quiz title" value={quizForm.title} onChange={(e) => setQuizForm((prev) => ({ ...prev, title: e.target.value }))} required className="w-full rounded-xl border border-blue-200 p-3" />
                <div className="space-y-2">
                  {quizForm.questions.map((question, idx) => (
                    <div key={`question-${idx}`} className="grid gap-2 rounded-xl border border-blue-100 bg-white p-3">
                      <textarea
                        rows={2}
                        placeholder={`Question ${idx + 1}`}
                        value={question.prompt}
                        onChange={(e) => {
                          const next = [...quizForm.questions];
                          next[idx] = { ...next[idx], prompt: e.target.value };
                          setQuizForm((prev) => ({ ...prev, questions: next }));
                        }}
                        className="w-full rounded-xl border border-blue-200 p-3"
                      />
                      <input
                        type="text"
                        placeholder="Correct answer"
                        value={question.answer}
                        onChange={(e) => {
                          const next = [...quizForm.questions];
                          next[idx] = { ...next[idx], answer: e.target.value };
                          setQuizForm((prev) => ({ ...prev, questions: next }));
                        }}
                        className="w-full rounded-xl border border-blue-200 p-3"
                      />
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button type="button" className="rounded-xl border border-blue-200 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={() => setQuizForm((prev) => ({ ...prev, questions: [...prev.questions, { prompt: "", answer: "" }] }))}>Add Question</button>
                  {quizForm.questions.length > 1 && <button type="button" className="rounded-xl border border-blue-200 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={() => setQuizForm((prev) => ({ ...prev, questions: prev.questions.slice(0, -1) }))}>Remove Last</button>}
                </div>
                <button type="submit" disabled={classrooms.length === 0} className="rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white disabled:opacity-50">Create Quiz</button>
              </form>

              <h3 className="mb-3 text-lg font-bold text-slate-900">Created Quizzes</h3>
              <div className="space-y-2">
                {quizzes.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">No quizzes yet.</div>}
                {quizzes.map((quiz) => (
                  <article key={quiz.id} className="rounded-xl border border-blue-100 p-3">
                    <div className="mb-2 flex flex-wrap items-center gap-2 text-sm"><span className="font-semibold text-slate-900">{quiz.classroom_name}</span><span className="text-slate-600">Grade {quiz.grade}</span><SubjectBadge subject={quiz.subject} /><span className="text-slate-500">{quiz.questions.length} questions</span></div>
                    <div className="font-semibold text-slate-900">{quiz.title}</div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === "classrooms" && (
            <section>
              <h2 className="mb-4 text-2xl font-bold text-slate-900">Classrooms</h2>
              <form onSubmit={createClassroom} className="mb-6 grid gap-3 rounded-xl border border-blue-100 bg-slate-50 p-4">
                <input type="text" placeholder="Classroom name" value={classroomForm.name} onChange={(e) => setClassroomForm((prev) => ({ ...prev, name: e.target.value }))} required className="w-full rounded-xl border border-blue-200 p-3" />
                <div className="grid gap-3 md:grid-cols-2">
                  <label className="text-sm font-semibold text-slate-700">Grade
                    <select value={classroomForm.grade} onChange={(e) => setClassroomForm((prev) => ({ ...prev, grade: Number(e.target.value) }))} className="mt-1 w-full rounded-xl border border-blue-200 p-3">
                      {GRADES.map((grade) => <option key={grade} value={grade}>Grade {grade}</option>)}
                    </select>
                  </label>
                  <label className="text-sm font-semibold text-slate-700">Subject
                    <select value={classroomForm.subject} onChange={(e) => setClassroomForm((prev) => ({ ...prev, subject: e.target.value }))} className="mt-1 w-full rounded-xl border border-blue-200 p-3">
                      {SUBJECTS.map((subject) => <option key={subject} value={subject}>{subject}</option>)}
                    </select>
                  </label>
                </div>
                <button type="submit" className="rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white">Create Classroom</button>
              </form>

              <h3 className="mb-3 text-lg font-bold text-slate-900">Your Classrooms</h3>
              <div className="space-y-3">
                {classrooms.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">No classrooms yet.</div>}
                {classrooms.map((classroom) => (
                  <article key={classroom.id} className="rounded-xl border border-blue-100 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="font-semibold text-slate-900">{classroom.name}</div>
                      <span className="text-sm text-slate-600">Grade {classroom.grade}</span>
                      <SubjectBadge subject={classroom.subject} />
                    </div>
                    <div className="mt-2 text-sm">Join code: <span className="rounded bg-blue-50 px-2 py-1 font-mono font-semibold text-blue-900">{classroom.join_code}</span></div>
                    <div className="mt-4">
                      <div className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Students</div>
                      {classroom.members.length === 0 && <div className="text-sm text-slate-500">No students joined yet.</div>}
                      <div className="space-y-2">
                        {classroom.members.map((member) => (
                          <div key={`${classroom.id}-${member.student_id}`} className="rounded-xl border border-blue-100 bg-slate-50 p-3 text-sm">
                            <div className="font-semibold text-slate-900">{member.first_name} {member.last_name}</div>
                            <div className="text-slate-700">{member.email}</div>
                            <div className="mt-1 text-slate-700">XP: {member.progress.xp} | Level: {member.progress.level} | Solved: {member.progress.problems_solved}</div>
                            <div className="mt-1 text-slate-700">Completed assignments: {member.completed_assignments_count}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
