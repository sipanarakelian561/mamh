import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: "url('/home-screen-bg.png')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      />

      <div className="absolute inset-0 bg-black/35" />

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <section className="flex flex-col gap-6 items-center w-full max-w-md">
          <h1 className="text-4xl font-extrabold text-white text-center drop-shadow-lg">
            MONSTER ATE MY
            <br />
            HOMEWORK
          </h1>

          <div className="flex flex-col gap-4 w-full">
            <button
              onClick={() => navigate("/login", { state: { role: "student" } })}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-white text-white bg-white/10 backdrop-blur-md hover:bg-blue-500 hover:text-white transition"
            >
              Student login
            </button>

            <button
              onClick={() => navigate("/login", { state: { role: "teacher" } })}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-white text-white bg-white/10 backdrop-blur-md hover:bg-blue-500 hover:text-white transition"
            >
              Teacher login
            </button>

            <button
              onClick={() => navigate("/register")}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-white text-white bg-white/10 backdrop-blur-md hover:bg-blue-500 hover:text-white transition"
            >
              Create account
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}