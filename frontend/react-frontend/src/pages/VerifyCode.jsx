import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { verifyResetCode } from "../api/auth";
import homeBackground from "../assets/mamh_homescreen.jpeg";

export default function VerifyCode() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const email = sessionStorage.getItem("resetEmail");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      await verifyResetCode(email, code);

      sessionStorage.setItem("resetCode", code);

      navigate("/reset-password");
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
        }}
      />
      <div className="absolute inset-0 bg-black/35" />

      <div className="relative z-10 flex items-center justify-center min-h-screen">
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-4 w-full max-w-md p-8 bg-white/10 backdrop-blur-md rounded-2xl"
        >
          <h1 className="text-white text-3xl font-bold">Enter Code</h1>

          {error && <div className="text-red-400">{error}</div>}

          <input
            type="text"
            placeholder="6-digit code"
            className="p-3 rounded-xl bg-white/10 text-white"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
          />

          <button className="bg-blue-500 text-white p-3 rounded-xl">
            Verify Code
          </button>
        </form>
      </div>
    </div>
  );
}