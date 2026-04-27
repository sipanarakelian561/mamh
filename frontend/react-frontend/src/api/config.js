function isLocalHost(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

export function getApiBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }

  if (typeof window !== "undefined" && isLocalHost(window.location.hostname)) {
    return "http://localhost:8000/api/v1";
  }

  throw new Error(
    "VITE_API_BASE_URL is not configured. Set it in Vercel for production builds."
  );
}
