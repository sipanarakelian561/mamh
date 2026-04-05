import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/UseAuth.jsx";
import Silk from "@/components/Silk.jsx";

export default function Register() {
  const registerDisabled = true;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { register } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (registerDisabled) {
      setError("Registration is disabled. Please contact an admin.");
      return;
    }
    setLoading(true);

    try {
      await register({ email, password, role });
      navigate(role === "teacher" ? "/teacher" : "/student");
    } catch (err) {
      setError(err.message || "Could not create account.");
    } finally {
      setLoading(false);
    }
  }

  return (

    <div className="relative min-h-screen">
    {/* Background */}
    <div className="absolute inset-0 z-0">
      <Silk
      speed={10}
      scale={2}
      color="#e346ff"
      noiseIntensity={1.5}
      rotation={5.5}
      />
    </div>
    
    <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
      <button
        className="text-white absolute top-4 left-4 px-4 py-2 rounded-xl border border-blue-300 hover:bg-blue-500 hover:text-white transition"
        onClick={() => navigate("/login")}
      >
        Back to Login
      </button>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 items-center w-full max-w-md"
      >
        <h1 className=" text-white text-4xl font-extrabold pb-2">Create Account</h1>
        <p className="w-full text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded-xl p-3">
          Registration is disabled. Please contact an admin to create an account.
        </p>

        {error && (
          <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={registerDisabled}
          className="placeholder-white text-white font-bold w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          disabled={registerDisabled}
          className="placeholder-white text-white font-bold w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          disabled={registerDisabled}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
        </select>

        <button
          type="submit"
          disabled={registerDisabled || loading}
          className="text-white w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
        >
          {loading ? "Creating..." : "Create Account"}
        </button>
      </form>
    </div>
    </div>
  );
}
