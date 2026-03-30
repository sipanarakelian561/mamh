export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <section className="flex flex-col gap-4 items-center w-full max-w-md">
        <h1 className="text-4xl font-extrabold pb-2">Main Menu</h1>

        <div className="flex flex-col gap-4">
          <button
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-blue-500 hover:text-white transition"
          >
            Start Game
          </button>

          <button className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition">
            Settings
          </button>

          <button className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition">
            Extra
          </button>
        </div>
      </section>
    </div>
  );
}
