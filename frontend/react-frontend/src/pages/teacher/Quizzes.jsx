export default function TeacherQuizzes() {
  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Quizzes / Problem Sets</div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Create Problem Set (placeholder)</div>
        <div className="text-lg">
          This page will let teachers:
          <ul className="list-disc ml-6 mt-2">
            <li>Name a topic</li>
            <li>Add questions + answers</li>
            <li>Set time limit</li>
            <li>Save the problem set</li>
          </ul>
        </div>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">My Problem Sets (mock)</div>
        <ul className="flex flex-col gap-3">
          <li className="rounded-xl border p-3 text-lg">Addition Basics (10 questions)</li>
          <li className="rounded-xl border p-3 text-lg">Subtraction Basics (8 questions)</li>
        </ul>
      </div>
    </div>
  );
}