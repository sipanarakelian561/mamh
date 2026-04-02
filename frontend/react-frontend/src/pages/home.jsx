import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <section className="flex flex-col gap-4 items-center w-full max-w-md">
        <h1 className="text-4xl font-extrabold pb-2">Main Menu</h1>

        <div className="flex flex-col gap-4">
          <button
            onClick={() => navigate("/login", { state: { role: "student" } })}
            className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-black hover:bg-blue-500 hover:text-white transition"
          >
            Student login
          </button>

          <button
            onClick={() => navigate("/login", { state: { role: "teacher" } })}
            className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Teacher login
          </button>

          <button
            onClick={() => navigate("/register")}
            className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Create account
          </button>
        </div>
      </section>
    </div>
  );
}
