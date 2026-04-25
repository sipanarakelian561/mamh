import { useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../../auth/UseAuth";

export default function StudentPlay() {
  const { token } = useAuth();
  const location = useLocation();
  const [started, setStarted] = useState(false);
  const [ready, setReady] = useState(false);
  const gameShellRef = useRef(null);

  const iframeSrc = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const mode = params.get("mode") || "";
    const quizId = params.get("quizId") || "";
    const qp = new URLSearchParams();
    const apiBaseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
    if (mode) qp.set("mode", mode);
    if (quizId) qp.set("quizId", quizId);
    if (token) qp.set("token", token);
    if (apiBaseUrl) qp.set("apiBaseUrl", apiBaseUrl);
    return `/official-game/OfficialGame.html?${qp.toString()}`;
  }, [location.search, token]);

  function enterFullscreen() {
    const el = gameShellRef.current;
    if (!el) return;
    if (el.requestFullscreen) {
      el.requestFullscreen();
    }
  }

  return (
    <div className="rounded-2xl border p-6 bg-white">
      <h2 className="text-2xl font-bold">Play Game</h2>
      <p className="mt-2 text-gray-600">Press space to jump.</p>

      {!started ? (
        <div className="mt-6">
          <button
            onClick={() => setStarted(true)}
            className="rounded-xl px-6 py-3 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Start Game
          </button>
        </div>
      ) : (
        <div
          ref={gameShellRef}
          className="game-shell mt-4 w-full rounded-2xl overflow-hidden border"
        >
          <div className="p-3 border-b flex items-center justify-between">
            <div className="text-sm text-gray-600">Official Game</div>
            <button
              onClick={enterFullscreen}
              disabled={!ready}
              className="rounded-lg px-3 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
            >
              {ready ? "Full Screen" : "Loading..."}
            </button>
          </div>
          <iframe
            src={iframeSrc}
            title="Official Game"
            allow="fullscreen"
            allowFullScreen
            onLoad={() => setReady(true)}
            className="game-frame w-full h-[500px]"
          />
        </div>
      )}
    </div>
  );
}
