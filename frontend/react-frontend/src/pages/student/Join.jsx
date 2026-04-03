import { useState } from "react";
import { validateJoinCode } from "../../utils/classroomCodes";

export default function StudentJoin() {
  const [code, setCode] = useState("");
  const [message, setMessage] = useState(null); // { type: 'success'|'error', text }

  function handleSubmit(e) {
    e.preventDefault();
    setMessage(null);

    const result = validateJoinCode(code);
    if (result) {
      setMessage({
        type: "success",
        text: `You joined ${result.classroomName}! (Demo: not saved until backend is connected.)`,
      });
      setCode("");
    } else {
      setMessage({
        type: "error",
        text: "Invalid or expired code. Get a new code from your teacher. (Same browser: generate a code as teacher first.)",
      });
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-md">
      <div className="text-white text-3xl font-extrabold">Join with code</div>

      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
        Enter the code your teacher shared. In this demo, the code must have been generated in this same browser (no backend yet).
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="text-white text-lg font-semibold">Class code</label>
        <input
          type="text"
          placeholder="e.g. ABC123"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="placeholder-white w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-lg tracking-widest uppercase"
          maxLength={6}
          autoComplete="off"
        />
        <button
          type="submit"
          className=" text-white rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
        >
          Join class
        </button>
      </form>

      {message && (
        <div
          className={`rounded-xl border p-4 ${
            message.type === "success"
              ? "border-green-400 bg-green-50 text-green-900"
              : "border-red-300 bg-red-50 text-red-800"
          }`}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}
