import { useNavigate } from "react-router-dom";
import Hyperspeed from "@/ReactBits/Hyperspeed/Hyperspeed.jsx";
import FuzzyText from "@/ReactBits/FuzzyText/FuzzyText.jsx";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen">
      {/* Background */}
      <div className="absolute inset-0 z-0 bg-black overflow-hidden">
        <Hyperspeed
          effectOptions={{
            distortion: "turbulentDistortion",
            length: 400,
            roadWidth: 10,
            islandWidth: 2,
            lanesPerRoad: 3,
            fov: 90,
            fovSpeedUp: 150,
            speedUp: 2,
            carLightsFade: 0.4,
            totalSideLightSticks: 20,
            lightPairsPerRoadWay: 40,
            shoulderLinesWidthPercentage: 0.05,
            brokenLinesWidthPercentage: 0.1,
            brokenLinesLengthPercentage: 0.5,
            lightStickWidth: [0.12, 0.5],
            lightStickHeight: [1.3, 1.7],
            movingAwaySpeed: [60, 80],
            movingCloserSpeed: [-120, -160],
            carLightsLength: [12, 80],
            carLightsRadius: [0.05, 0.14],
            carWidthPercentage: [0.3, 0.5],
            carShiftX: [-0.8, 0.8],
            carFloorSeparation: [0, 5],
            colors: {
              roadColor: 526344,
              islandColor: 657930,
              background: 0,
              shoulderLines: 1250072,
              brokenLines: 1250072,
              leftCars: [14177983, 6770850, 12732332],
              rightCars: [242627, 941733, 3294549],
              sticks: 242627,
            },
          }}
        />
      </div>

   

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
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
    </div>
  );
}