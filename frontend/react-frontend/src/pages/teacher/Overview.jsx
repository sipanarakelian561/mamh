import { useNavigate } from "react-router-dom";

function Card({ title, children }) {
  return (
    <div className="rounded-2xl border border-blue-100 p-5">
      <div className="text-xl font-bold mb-3 text-slate-900">{title}</div>
      {children}
    </div>
  );
}

export default function TeacherOverview() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold text-slate-900">Teacher Dashboard</div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Quick Actions">
          <div className="flex flex-col gap-4">
            <button
              onClick={() => navigate("/teacher/question-bank")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Question Bank
            </button>
            <button
              onClick={() => navigate("/teacher/quizzes")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Quizzes
            </button>
            <button
              onClick={() => navigate("/teacher/classrooms")}
              className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              Manage Classrooms
            </button>
          </div>
        </Card>

        <Card title="At a Glance (mock for now)">
          <ul className="flex flex-col gap-3">
            <li className="rounded-xl border border-blue-100 p-3 text-lg text-slate-800">Active Classrooms: 2</li>
            <li className="rounded-xl border border-blue-100 p-3 text-lg text-slate-800">Question Bank Ready</li>
            <li className="rounded-xl border border-blue-100 p-3 text-lg text-slate-800">Problem Sets: 3</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
