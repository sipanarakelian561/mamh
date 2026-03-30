import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();

    if (!email) {
      alert("Please enter your email.");
      return;
    }

    navigate("/verify-code", { state: { email } });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 items-center w-full max-w-md">
        <h1 className="text-4xl font-extrabold pb-2">Forgot Password</h1>

        <input
          type="email"
          placeholder="Enter your account email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full p-3 border border-blue-300 rounded-xl"
        />

        <button
          type="submit"
          className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
        >
          Send Verification Code
        </button>

        <button
          type="button"
          onClick={() => navigate("/login")}
          className="text-blue-600 hover:underline"
        >
          Back to Login
        </button>
      </form>
    </div>
  );
}