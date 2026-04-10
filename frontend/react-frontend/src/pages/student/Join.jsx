import { useState } from "react";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/UseAuth";

export default function StudentJoin() {
  const { token, user } = useAuth();
  const [code, setCode] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState(user?.email || "");
  const [message, setMessage] = useState(null); // { type: 'success'|'error', text }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage(null);

    try {
      await apiFetch("/student/classrooms/join", {
        method: "POST",
        token,
        body: JSON.stringify({
          class_code: code.trim().toUpperCase(),
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          email: email.trim().toLowerCase(),
        }),
      });
      setMessage({
        type: "success",
        text: "You joined the classroom!",
      });
      setCode("");
      setFirstName("");
      setLastName("");
    } catch (err) {
      setMessage({
        type: "error",
        text: err.message || "Invalid or expired code. Get a new code from your teacher.",
      });
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-md">
      <div className="text-3xl font-extrabold">Join with code</div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="text-lg font-semibold">Class code</label>
        <input
          type="text"
          placeholder="e.g. ABCD1234"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-lg tracking-widest uppercase"
          maxLength={12}
          autoComplete="off"
          required
        />
        <input
          type="text"
          placeholder="First name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <input
          type="text"
          placeholder="Last name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <input
          type="email"
          placeholder="Account email used to log in"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <button
          type="submit"
          className="rounded-xl px-6 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
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
