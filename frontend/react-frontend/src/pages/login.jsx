import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/UseAuth";

const DEV_MODE = true; // Match AuthContext dev mode

export default function LogIn() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");

	const navigate = useNavigate();
	const { login, user } = useAuth();

	// Navigate after successful login/register
	useEffect(() => {
		if (user) {
			if (user.role === "teacher") {
				navigate("/teacher");
			} else {
				navigate("/student");
			}
		}
	}, [user, navigate]);

	async function HandleSubmit(e) {
		e.preventDefault();
		setError("");

		try {
			await login(email, password);
		} catch (err) {
			setError(err.message || "Login failed. Please try again.");
		}
	}

	function fillTestCredentials(accountType) {
		if (accountType === "teacher") {
			setEmail("teacher@test.com");
			setPassword("password");
		} else {
			setEmail("student@test.com");
			setPassword("password");
		}
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-white px-4">
			<button 
				className="absolute top-4 left-4 px-4 py-2 rounded-xl border border-blue-300 hover:bg-blue-500 hover:text-white transition" 
				onClick={() => navigate("/")}
			> 
				Return 
			</button>
			<form onSubmit={HandleSubmit} className="flex flex-col gap-4 items-center w-full max-w-md">
				<h1 className="text-4xl font-extrabold pb-2"> Log in </h1>
				
				{/* Dev Mode Test Credentials */}
				{DEV_MODE && (
					<div className="w-full p-4 rounded-xl border border-blue-200 bg-blue-50">
						<div className="text-sm font-semibold text-blue-900 mb-3">Test Accounts (Dev Mode):</div>
						<div className="flex flex-col gap-2">
							<button
								type="button"
								onClick={() => fillTestCredentials("teacher")}
								className="w-full px-4 py-2 rounded-lg border border-blue-300 bg-white hover:bg-blue-100 text-sm text-left"
							>
								<strong>Teacher:</strong> teacher@test.com / password
							</button>
							<button
								type="button"
								onClick={() => fillTestCredentials("student")}
								className="w-full px-4 py-2 rounded-lg border border-blue-300 bg-white hover:bg-blue-100 text-sm text-left"
							>
								<strong>Student:</strong> student@test.com / password
							</button>
						</div>
					</div>
				)}

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
					className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
				<input
					type="password"
					placeholder="Password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
					className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
				<button 
					type="submit"
					className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
				> 
					Submit 
				</button>
				{!DEV_MODE && (
					<div className="flex gap-2 items-center">
						<button 
							type="button"
							className="text-blue-600 hover:underline"
						> 
							Forgot password 
						</button>
					</div>
				)}
			</form>
		</div>
	);
};
