import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-white to-white px-4">
      <section className="text-center w-full max-w-md">
        <h1 className="mb-10 text-4xl sm:text-5xl font-extrabold text-black">
          Main Menu
        </h1>

        <div className="flex flex-col gap-4">
          <button
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-pink-300 text-pink-700 hover:bg-pink-300 hover:text-white transition"
          >
            Start Game
          </button>

          <button
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-blue-500 hover:text-white transition"
          >
            Settings
          </button>

          <button
            onClick={() => navigate("/login")}
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-blue-500 hover:text-white transition"
          >
            Login - Sign Up
          </button>
        </div>
      </section>
    </main>
  );
}
