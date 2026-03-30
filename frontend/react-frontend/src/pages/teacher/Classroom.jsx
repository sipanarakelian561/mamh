import { useState } from "react";
import { generateJoinCode } from "../../utils/classroomCodes";

// Dummy data for skeleton — replace with API when backend is ready
const DUMMY_CLASSROOMS = [
  { id: "1", name: "Math" },
  { id: "2", name: "Science" },
  { id: "3", name: "Reading & Writing" },
];

const DUMMY_STUDENTS_BY_CLASS = {
  "1": [
    { id: "s1", name: "Lebron James", email: "lebron.james@school.edu" },
    { id: "s2", name: "Lebron James Jr.", email: "lebron.jamesJr@school.edu" },
    { id: "s3", name: "Lebron James III", email: "lebron.jamesIII@school.edu" },
  ],
  "2": [
    { id: "s4", name: "Lebron James IV", email: "lebron.jamesIV@school.edu" },
    { id: "s5", name: "Lebron James V", email: "lebron.jamesV@school.edu" },
  ],
  "3": [
    { id: "s6", name: "Lebron James VI", email: "lebron.jamesVI@school.edu" },
    { id: "s7", name: "Lebron James VII", email: "lebron.jamesVII@school.edu" },
    { id: "s8", name: "Lebron James VIII", email: "lebron.jamesVIII@school.edu" },
  ],
};

export default function TeacherClassrooms() {
  const [activeCode, setActiveCode] = useState(null); // { code, classroomName }

  function handleGenerateCode(classroom) {
    const code = generateJoinCode(classroom.id, classroom.name);
    setActiveCode({ code, classroomName: classroom.name });
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-3xl font-extrabold">Classrooms</div>

      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
        <strong>Demo (no backend):</strong> Codes are stored in this browser only. Students can join only from the same browser (e.g. open a student tab and use “Join with code”).
      </div>

      {activeCode && (
        <div className="rounded-2xl border-2 border-green-400 bg-green-50 p-5">
          <div className="text-lg font-bold text-green-900 mb-1">Share this code with students</div>
          <div className="text-3xl font-mono font-bold tracking-widest text-green-800">
            {activeCode.code}
          </div>
          <div className="text-sm text-green-700 mt-1">Class: {activeCode.classroomName}</div>
        </div>
      )}

      <div className="rounded-2xl border p-5">
        <div className="text-xl font-bold mb-4">My Classrooms</div>
        <ul className="flex flex-col gap-3">
          {DUMMY_CLASSROOMS.map((room) => (
            <li
              key={room.id}
              className="rounded-xl border p-4 flex flex-col gap-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-4">
                <span className="text-lg font-semibold">{room.name}</span>
                <button
                  type="button"
                  onClick={() => handleGenerateCode(room)}
                  className="rounded-xl px-5 py-2.5 text-base font-semibold border border-blue-300 bg-white hover:bg-blue-500 hover:text-white transition"
                >
                  Generate join code
                </button>
              </div>
              <div className="border-t pt-3">
                <div className="text-sm font-semibold text-gray-600 mb-2">
                  Students in class ({DUMMY_STUDENTS_BY_CLASS[room.id]?.length ?? 0})
                </div>
                <ul className="flex flex-col gap-1.5">
                  {(DUMMY_STUDENTS_BY_CLASS[room.id] ?? []).map((s) => (
                    <li key={s.id} className="text-sm text-gray-700 flex gap-2">
                      <span className="font-medium">{s.name}</span>
                      <span className="text-gray-500">{s.email}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
