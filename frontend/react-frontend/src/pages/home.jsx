import { useNavigate } from "react-router-dom";
import FuzzyText from "@/ReactBits/FuzzyText/FuzzyText.jsx";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-white">
        <section className="flex flex-col gap-4 items-center w-full">
          <FuzzyText 
          baseIntensity={0.30}
          hoverIntensity={1.31}
          enableHover
        >
          MONSTER ATE MY HOMEWORK
        </FuzzyText>

          <div className="flex flex-col gap-4">
            <button
              onClick={() => navigate("/login", { state: { role: "student" } })}
              className="rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-white hover:bg-blue-500 hover:text-white transition"
            >
              Student login
            </button>

            <button
              onClick={() => navigate("/login", { state: { role: "teacher" } })}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-white hover:bg-blue-500 hover:text-white transition"
            >
              Teacher login
            </button>

            <button
              onClick={() => navigate("/register")}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 text-white hover:bg-blue-500 hover:text-white transition"
            >
              Create account
            </button>
          </div>
        </section>
    </div>
  );
}
