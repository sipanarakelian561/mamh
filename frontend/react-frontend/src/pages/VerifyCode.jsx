import { useState } from "react";
import { useLocation } from "react-router-dom";

export default function VerifyCode() {
  const [code, setCode] = useState("");
  const location = useLocation();
  const email = location.state?.email || "";

  function handleSubmit(e) {
    e.preventDefault();
    alert("Verification code submitted: " + code);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 items-center w-full max-w-md">
        <h1 className="text-4xl font-extrabold pb-2">Verify Code</h1>

        <p className="text-gray-600 text-sm text-center">
          Enter the code sent to {email}
        </p>

        <input
          type="text"
          placeholder="Verification Code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
          className="w-full p-3 border border-blue-300 rounded-xl"
        />

        <button
          type="submit"
          className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
        >
          Verify Code
        </button>
      </form>
    </div>
  );
}