import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { resetPassword } from "../api/auth";
import homeBackground from "../assets/mamh_homescreen.jpeg";

export default function ResetPassword() {
const [password, setPassword] = useState("");
const [confirm, setConfirm] = useState("");
const [success, setSuccess] = useState(false);
const [error, setError] = useState("");

const navigate = useNavigate();
const email = sessionStorage.getItem("resetEmail");
const code = sessionStorage.getItem("resetCode");

async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
    setError("Passwords do not match");
    return;
    }

    try {
    await resetPassword(email, code, password);
    setSuccess(true);
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
        <div className="flex flex-col gap-4 w-full max-w-md p-8 bg-white/10 backdrop-blur-md rounded-2xl">
        {!success ? (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <h1 className="text-white text-3xl font-bold">Reset Password</h1>

            {error && <div className="text-red-400">{error}</div>}

            <input
                type="password"
                placeholder="New password"
                className="p-3 rounded-xl bg-white/10 text-white"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />

            <input
                type="password"
                placeholder="Confirm password"
                className="p-3 rounded-xl bg-white/10 text-white"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
            />

            <button className="bg-blue-500 text-white p-3 rounded-xl">
                Update Password
            </button>
            </form>
        ) : (
            <>
            <h1 className="text-green-400 text-2xl font-bold">
                Password Changed Successfully
            </h1>

            <button
                onClick={() => navigate("/login")}
                className="bg-blue-500 text-white p-3 rounded-xl"
            >
                Return to Login
            </button>
            </>
        )}
        </div>
    </div>
    </div>
);
}