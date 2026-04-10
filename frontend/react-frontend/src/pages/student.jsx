import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import { useAuth } from "../auth/UseAuth";

export default function StudentPage() {
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const [activeTab, setActiveTab] = useState("assignments");
  const [progress, setProgress] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [problems, setProblems] = useState([]);
  const [answer, setAnswer] = useState("");

  const [classrooms, setClassrooms] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);

  const [joinForm, setJoinForm] = useState({
    class_code: "",
    first_name: "",
    last_name: "",
    email: "",
  });

  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const tabs = useMemo(
    () => [
      { id: "assignments", label: "Assignments" },
      { id: "quizzes", label: "Quizzes" },
      { id: "join", label: "Join Class" },
      { id: "learning", label: "Learning" },
    ],
    []
  );

  async function loadLearningData() {
    const [p, inv] = await Promise.all([
      apiFetch("/student/progress", { method: "GET", token }),
      apiFetch("/student/inventory", { method: "GET", token }),
    ]);
    setProgress(p);
    setInventory(inv);
  }

  async function loadClassroomData() {
    const [joinedClassrooms, assignmentRows, quizRows] = await Promise.all([
      apiFetch("/student/classrooms", { method: "GET", token }),
      apiFetch("/student/assignments", { method: "GET", token }),
      apiFetch("/student/quizzes", { method: "GET", token }),
    ]);

    setClassrooms(joinedClassrooms || []);
    setAssignments(assignmentRows || []);
    setQuizzes(quizRows || []);
  }

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const [p, inv] = await Promise.all([
          apiFetch("/student/progress", { method: "GET", token }),
          apiFetch("/student/inventory", { method: "GET", token }),
        ]);
        const [joinedClassrooms, assignmentRows, quizRows] = await Promise.all([
          apiFetch("/student/classrooms", { method: "GET", token }),
          apiFetch("/student/assignments", { method: "GET", token }),
          apiFetch("/student/quizzes", { method: "GET", token }),
        ]);

        if (cancelled) return;
        setProgress(p);
        setInventory(inv);
        setClassrooms(joinedClassrooms || []);
        setAssignments(assignmentRows || []);
        setQuizzes(quizRows || []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load student dashboard.");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function joinClassroom(e) {
    e.preventDefault();
    setError("");
    setStatus("");

    try {
      await apiFetch("/student/classrooms/join", {
        method: "POST",
        token,
        body: JSON.stringify({
          ...joinForm,
          class_code: joinForm.class_code.trim().toUpperCase(),
          first_name: joinForm.first_name.trim(),
          last_name: joinForm.last_name.trim(),
          email: joinForm.email.trim().toLowerCase(),
        }),
      });

      setJoinForm((prev) => ({ ...prev, class_code: "" }));
      setStatus("Joined classroom successfully.");
      await loadClassroomData();
    } catch (err) {
      setError(err.message || "Could not join classroom.");
    }
  }

  async function viewAssignment(assignmentId) {
    setError("");
    setStatus("");
    try {
      const data = await apiFetch(`/student/assignments/${assignmentId}`, {
        method: "GET",
        token,
      });
      setSelectedAssignment(data);
    } catch (err) {
      setError(err.message || "Could not open assignment.");
    }
  }

  async function markAssignmentComplete(assignmentId) {
    setError("");
    setStatus("");
    try {
      await apiFetch(`/student/assignments/${assignmentId}/complete`, {
        method: "POST",
        token,
      });
      setStatus("Assignment marked complete.");
      await loadClassroomData();
      await viewAssignment(assignmentId);
    } catch (err) {
      setError(err.message || "Could not mark assignment complete.");
    }
  }

  async function viewQuiz(quizId) {
    setError("");
    setStatus("");
    setQuizResult(null);

    try {
      const data = await apiFetch(`/student/quizzes/${quizId}`, {
        method: "GET",
        token,
      });
      setSelectedQuiz(data);

      const answerSeed = {};
      (data.questions || []).forEach((q) => {
        answerSeed[q.id] = "";
      });
      setQuizAnswers(answerSeed);
    } catch (err) {
      setError(err.message || "Could not open quiz.");
    }
  }

  function startQuizInGame(quizId) {
    navigate(`/student/play?mode=quiz&quizId=${quizId}`);
  }

  async function submitQuiz() {
    if (!selectedQuiz) return;

    setError("");
    setStatus("");

    try {
      const answers = (selectedQuiz.questions || []).map((q) => ({
        question_id: q.id,
        answer: (quizAnswers[q.id] || "").trim(),
      }));

      const result = await apiFetch(`/student/quizzes/${selectedQuiz.id}/submit`, {
        method: "POST",
        token,
        body: JSON.stringify({ answers }),
      });

      setQuizResult(result);
      setStatus(`Quiz submitted. Score: ${result.correct_count}/${result.total_questions}`);
    } catch (err) {
      setError(err.message || "Could not submit quiz.");
    }
  }

  async function refreshAssignedWork() {
    setError("");
    setStatus("");
    try {
      await loadClassroomData();
      setSelectedAssignment(null);
      setSelectedQuiz(null);
      setQuizResult(null);
    } catch (err) {
      setError(err.message || "Could not refresh assigned work.");
    }
  }

  async function getProblem() {
    setStatus("");
    setError("");
    try {
      const data = await apiFetch("/game/problems", {
        method: "POST",
        token,
        body: JSON.stringify({ grade: 3, difficulty: 1, count: 1 }),
      });
      setProblems(data.problems || []);
      setAnswer("");
    } catch (err) {
      setError(err.message || "Could not generate problem.");
    }
  }

  async function submitAnswer() {
    const current = problems[0];
    if (!current || answer.trim() === "") return;

    setStatus("");
    setError("");
    try {
      const result = await apiFetch("/game/submit", {
        method: "POST",
        token,
        body: JSON.stringify({
          problem_id: current.problem_id,
          answer: Number(answer),
        }),
      });

      if (result.correct) {
        setStatus("Correct! XP updated.");
        await loadLearningData();
      } else {
        setStatus("Incorrect. Try another one.");
      }
    } catch (err) {
      setError(err.message || "Could not submit answer.");
    }
  }

  async function addTestItem() {
    setStatus("");
    setError("");
    try {
      await apiFetch("/student/inventory/add", {
        method: "POST",
        token,
        body: JSON.stringify({
          item_id: `item-${Date.now()}`,
          name: "Practice Hat",
          slot: "head",
        }),
      });
      await loadLearningData();
      setStatus("Item added.");
    } catch (err) {
      setError(err.message || "Could not add inventory item.");
    }
  }

  async function toggleEquip(item) {
    setStatus("");
    setError("");
    try {
      await apiFetch("/student/inventory/equip", {
        method: "POST",
        token,
        body: JSON.stringify({
          item_id: item.item_id,
          equipped: !item.equipped,
        }),
      });
      await loadLearningData();
    } catch (err) {
      setError(err.message || "Could not update item.");
    }
  }

  return (
    <div className="min-h-screen w-full bg-slate-50 p-3 md:p-6">
      <div className="flex min-h-[calc(100vh-1.5rem)] w-full flex-col gap-4 md:min-h-[calc(100vh-3rem)] md:flex-row">
        <aside className="w-full rounded-2xl border border-blue-200 bg-white p-4 md:w-72 md:shrink-0">
          <div className="mb-4 text-xl font-extrabold text-slate-900">Student Dashboard</div>
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Tabs</div>
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
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Assignments</h2>
                <button className="rounded-xl border border-blue-300 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={refreshAssignedWork}>Refresh</button>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                <div className="space-y-2">
                  {assignments.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">No assigned work yet. Join a classroom first.</div>}
                  {assignments.map((assignment) => (
                    <article key={assignment.id} className="rounded-xl border border-blue-100 p-3">
                      <div className="text-sm text-slate-600">{assignment.classroom_name} | Grade {assignment.grade} | {assignment.subject}</div>
                      <div className="font-semibold text-slate-900">{assignment.title}</div>
                      <div className="mt-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{assignment.completed ? "Completed" : "Pending"}</div>
                      <button className="mt-2 rounded-lg border border-blue-300 px-3 py-1 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={() => viewAssignment(assignment.id)}>View Assignment</button>
                    </article>
                  ))}
                </div>

                <div className="rounded-xl border border-blue-100 bg-slate-50 p-4">
                  <div className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Selected Assignment</div>
                  {!selectedAssignment && <div className="text-sm text-slate-500">Select "View Assignment" to open one.</div>}
                  {selectedAssignment && (
                    <div>
                      <div className="text-sm text-slate-600">{selectedAssignment.classroom_name} | Grade {selectedAssignment.grade} | {selectedAssignment.subject}</div>
                      <h3 className="mt-1 text-xl font-bold text-slate-900">{selectedAssignment.title}</h3>
                      <p className="mt-3 whitespace-pre-wrap text-sm text-slate-800">{selectedAssignment.content}</p>
                      <div className="mt-3 text-sm font-semibold text-slate-700">Status: {selectedAssignment.completed ? "Completed" : "Pending"}</div>
                      {!selectedAssignment.completed && <button className="mt-3 rounded-xl border border-blue-400 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-500 hover:text-white" onClick={() => markAssignmentComplete(selectedAssignment.id)}>Mark As Completed</button>}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {activeTab === "quizzes" && (
            <section>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Quizzes</h2>
                <button className="rounded-xl border border-blue-300 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={refreshAssignedWork}>Refresh</button>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                <div className="space-y-2">
                  {quizzes.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">No quizzes assigned yet.</div>}
                  {quizzes.map((quiz) => (
                    <article key={quiz.id} className="rounded-xl border border-blue-100 p-3">
                      <div className="text-sm text-slate-600">{quiz.classroom_name} | Grade {quiz.grade} | {quiz.subject}</div>
                      <div className="font-semibold text-slate-900">{quiz.title}</div>
                      <div className="text-sm text-slate-500">{quiz.question_count} questions</div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <button className="rounded-lg border border-blue-300 px-3 py-1 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={() => viewQuiz(quiz.id)}>View Quiz</button>
                        <button className="rounded-lg border border-blue-400 px-3 py-1 text-sm font-semibold text-slate-900 hover:bg-blue-500 hover:text-white" onClick={() => startQuizInGame(quiz.id)}>Start Quiz</button>
                      </div>
                    </article>
                  ))}
                </div>

                <div className="rounded-xl border border-blue-100 bg-slate-50 p-4">
                  <div className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Selected Quiz</div>
                  {!selectedQuiz && <div className="text-sm text-slate-500">Select "View Quiz" to open one.</div>}
                  {selectedQuiz && (
                    <div>
                      <div className="text-sm text-slate-600">{selectedQuiz.classroom_name} | Grade {selectedQuiz.grade} | {selectedQuiz.subject}</div>
                      <h3 className="mt-1 text-xl font-bold text-slate-900">{selectedQuiz.title}</h3>
                      <div className="mt-3 space-y-3">
                        {selectedQuiz.questions.map((question, idx) => {
                          const rowResult = quizResult?.results?.find((r) => r.question_id === question.id);
                          return (
                            <div key={question.id} className="rounded-xl border border-blue-100 bg-white p-3">
                              <div className="text-sm font-semibold text-slate-900">Q{idx + 1}. {question.prompt}</div>
                              <input
                                type="text"
                                value={quizAnswers[question.id] || ""}
                                onChange={(e) => setQuizAnswers((prev) => ({ ...prev, [question.id]: e.target.value }))}
                                placeholder="Your answer"
                                className="mt-2 w-full rounded-xl border border-blue-200 p-3"
                              />
                              {rowResult && (
                                <div className={`mt-2 text-sm font-semibold ${rowResult.correct ? "text-green-700" : "text-red-700"}`}>
                                  {rowResult.correct ? "Correct" : "Incorrect"}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <button className="mt-4 rounded-xl border border-blue-400 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-blue-500 hover:text-white" onClick={submitQuiz}>Submit Quiz</button>
                      {quizResult && <div className="mt-3 text-sm font-semibold text-slate-700">Score: {quizResult.correct_count}/{quizResult.total_questions}</div>}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {activeTab === "join" && (
            <section>
              <h2 className="mb-4 text-2xl font-bold text-slate-900">Join A Class</h2>
              <form onSubmit={joinClassroom} className="mb-6 grid gap-3 rounded-xl border border-blue-100 bg-slate-50 p-4">
                <input type="text" value={joinForm.class_code} onChange={(e) => setJoinForm((prev) => ({ ...prev, class_code: e.target.value }))} placeholder="Class code" required className="w-full rounded-xl border border-blue-200 p-3 uppercase" />
                <div className="grid gap-3 md:grid-cols-2">
                  <input type="text" value={joinForm.first_name} onChange={(e) => setJoinForm((prev) => ({ ...prev, first_name: e.target.value }))} placeholder="First name" required className="w-full rounded-xl border border-blue-200 p-3" />
                  <input type="text" value={joinForm.last_name} onChange={(e) => setJoinForm((prev) => ({ ...prev, last_name: e.target.value }))} placeholder="Last name" required className="w-full rounded-xl border border-blue-200 p-3" />
                </div>
                <input type="email" value={joinForm.email} onChange={(e) => setJoinForm((prev) => ({ ...prev, email: e.target.value }))} placeholder="Account email used for login" required className="w-full rounded-xl border border-blue-200 p-3" />
                <button type="submit" className="rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white">Join Classroom</button>
              </form>

              <h3 className="mb-3 text-lg font-bold text-slate-900">Your Classrooms</h3>
              <div className="space-y-2">
                {classrooms.length === 0 && <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">You are not in a classroom yet.</div>}
                {classrooms.map((classroom) => (
                  <article key={`${classroom.classroom_id}-${classroom.joined_at}`} className="rounded-xl border border-blue-100 p-3">
                    <div className="font-semibold text-slate-900">{classroom.name}</div>
                    <div className="text-sm text-slate-700">Grade {classroom.grade} | {classroom.subject}</div>
                    <div className="text-sm text-slate-700">Joined as: {classroom.first_name} {classroom.last_name} ({classroom.email})</div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === "learning" && (
            <section>
              <h2 className="mb-4 text-2xl font-bold text-slate-900">Learning</h2>
              <div className="mb-4 rounded-xl border border-blue-100 bg-slate-50 p-4">
                <div className="font-semibold text-slate-900">Progress</div>
                <div className="text-sm text-slate-700">XP: {progress?.xp ?? "-"}</div>
                <div className="text-sm text-slate-700">Level: {progress?.level ?? "-"}</div>
                <div className="text-sm text-slate-700">Problems Solved: {progress?.problems_solved ?? "-"}</div>
              </div>

              <button className="mb-3 w-full rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white" onClick={getProblem}>Generate Practice Problem</button>

              {problems[0] && (
                <div className="mb-4 rounded-xl border border-blue-100 p-4">
                  <div className="mb-2 text-sm">Problem: {problems[0].prompt}</div>
                  <input type="number" placeholder="Your answer" value={answer} onChange={(e) => setAnswer(e.target.value)} className="mb-2 w-full rounded-xl border border-blue-200 p-3" />
                  <button className="w-full rounded-xl border border-blue-400 px-4 py-2 font-semibold text-slate-900 hover:bg-blue-500 hover:text-white" onClick={submitAnswer}>Submit Answer</button>
                </div>
              )}

              <div className="rounded-xl border border-blue-100 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <div className="font-semibold text-slate-900">Inventory</div>
                  <button className="rounded-xl border border-blue-200 px-3 py-1 text-sm font-semibold text-slate-900 hover:bg-blue-50" onClick={addTestItem}>Add Test Item</button>
                </div>
                <div className="flex flex-col gap-2">
                  {inventory.length === 0 && <div className="text-sm text-slate-500">No items yet.</div>}
                  {inventory.map((item) => (
                    <button key={item.item_id} className="w-full rounded-xl border border-blue-200 px-3 py-2 text-left text-sm text-slate-800 hover:bg-blue-50" onClick={() => toggleEquip(item)}>
                      {item.name} ({item.slot}) - {item.equipped ? "Equipped" : "Unequipped"}
                    </button>
                  ))}
                </div>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
