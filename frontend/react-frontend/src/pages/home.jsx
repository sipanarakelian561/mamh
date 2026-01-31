import { useNavigate } from "react-router-dom";

export default function Home() {
	const navigate = useNavigate();

	const goToLogin = () => {
		navigate("/login");
	};

	return (
		<main className="min-h-[100svh] flex items-center justify-center bg-gradient-to-b from-white to-white">
			<section className="text-center">
				<h1 className="mb-10 text-5xl font-extrabold text-black">
					Main Menu
				</h1>

				<div className="flex flex-col gap-4">
					<button
						className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-white hover:text-white transition"
					>
						Start Game
					</button>

					<button
						className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-white hover:text-white transition"
					>
						Settings
					</button>

					<button
						className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-white hover:text-white transition"
						onClick={goToLogin}
					>
						Login - Sign Up
					</button>
				</div>
			</section>
		</main>
	);
} 
