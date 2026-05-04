import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { requestPasswordReset } from "../api/auth";
import homeBackground from "../assets/mamh_homescreen.jpeg";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");

    try {
      await requestPasswordReset(email);

      sessionStorage.setItem("resetEmail", email);

      navigate("/verify-code");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="relative min-h-screen">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `url(${homeBackground})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />

      <div className="absolute inset-0 bg-black/35" />

      <button
        type="button"
        onClick={() => navigate("/login")}
        className="absolute top-4 left-4 z-20 px-4 py-2 rounded-xl border border-white text-white bg-white/10 backdrop-blur-md hover:bg-blue-500 hover:text-white transition"
      >
        Return
      </button>

      <div className="relative z-10 flex items-center justify-center min-h-screen">
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-4 w-full max-w-md p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/30"
        >
          <h1 className="text-white text-3xl font-bold">Forgot Password</h1>

          {error && <div className="text-red-400">{error}</div>}
          {message && <div className="text-green-400">{message}</div>}

          <input
            type="email"
            placeholder="Enter your email"
            className="p-3 rounded-xl bg-white/10 text-white placeholder-white/70 border border-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <button className="bg-blue-500 text-white p-3 rounded-xl hover:bg-blue-600 transition">
            Send Code
          </button>
        </form>
      </div>
    </div>
  );
}