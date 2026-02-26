export default function Home() {
    return (
        <main className="min-h-[100svh] flex items-center justify-center bg-gradient-to-b from-white to-pink-50">
      <section className="text-center">
        <h1 className="mb-10 text-5xl font-extrabold text-pink-900">
          Main Menu
        </h1>

        <div className="flex flex-col gap-4">
          <button
<<<<<<< Updated upstream
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-pink-300 text-pink-700 hover:bg-pink-300 hover:text-white transition"
=======
            onClick={() => navigate("/student/play")}
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-blue-500 hover:text-white transition"
>>>>>>> Stashed changes
          >
            Start Game
          </button>

          <button
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-pink-300 text-pink-700 hover:bg-pink-300 hover:text-white transition"
          >
            Settings
          </button>

          <button
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-pink-300 text-pink-700 hover:bg-pink-300 hover:text-white transition"
          >
            Extra
          </button>
        </div>
      </section>
    </main>
    );
   } 