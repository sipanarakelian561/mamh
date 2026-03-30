export default function TeacherAssignments() {
  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Assignments</div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Create Assignment (placeholder)</div>
        <div className="text-lg">
          This page will let teachers:
          <ul className="list-disc ml-6 mt-2">
            <li>Select a classroom</li>
            <li>Select a problem set / quiz</li>
            <li>Set due date</li>
            <li>Assign to students</li>
          </ul>
        </div>
      </div>

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-2">Existing Assignments (mock)</div>
        <ul className="flex flex-col gap-3">
          <li className="rounded-xl border p-3 text-lg">Math Set 1 → Classroom A</li>
          <li className="rounded-xl border p-3 text-lg">Fractions Quiz → Classroom B</li>
        </ul>
      </div>
    </div>
  );
}