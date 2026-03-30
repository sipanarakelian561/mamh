import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LogIn() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [signup, setSignup] = useState(false);
	const [gradelevel, setGradelevel] = useState("");
	const [id, setId] = useState("");

	const navigate = useNavigate();

	function HandleSubmit() {
		console.log("Email: " + email, "Password" + password);
		return;
	}

	if (signup === false) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<button className="absolute top-4 left-4 px-3 py-1 rounded border" onClick={() => navigate("/")}> Return </button>
				<form onSubmit={HandleSubmit} className="flex flex-col gap-4 items-center w-65">
					<h1 className="text-4xl pb-2"> Log in </h1>
					<input
						type="email"
						placeholder="Email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<input
						type="password"
						placeholder="Password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<button className="w-20 p-2 border rounded item-center"> Submit </button>
					<div className="flex ">
						<button className="flex-1" onClick={() => setSignup(true)}> Sign up </button>
						<h1 className="self-center">|</h1>
						<button className="flex-1"> Forgot password </button>
					</div>
				</form>
			</div>);
	} else {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<button className="absolute top-4 left-4 px-3 py-1 rounded border" onClick={() => navigate("/")}> Return </button>
				<form onSubmit={HandleSubmit} className="flex flex-col gap-4 items-center w-65">
					<h1 className="text-4xl pb-2"> Sign up </h1>
					<input
						type="email"
						placeholder="Email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<input
						type="password"
						placeholder="Password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<input
						type="number"
						placeholder="Grade Level"
						value={gradelevel}
						onChange={(e) => setGradelevel(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<input
						type="number"
						placeholder="Id"
						value={id}
						onChange={(e) => setId(e.target.value)}
						className="w-full p-2 border rounded focus:outline-none"
					/>
					<button className="w-20 p-2 border rounded item-center"> Submit </button>
					<button className="flex-1" onClick={() => setSignup(false)}> Log in </button>
				</form>
			</div>);
	};
};
