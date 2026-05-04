const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function requestPasswordReset(email) {
    const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
    });

    if (!res.ok) throw new Error((await res.json()).detail || "Failed to send code");
    return res.json();
}

export async function verifyResetCode(email, code) {
    const res = await fetch(`${API_BASE_URL}/auth/verify-reset-code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, code }),
});
if (!res.ok) throw new Error((await res.json()).detail || "Invalid code");
return res.json();
}

export async function resetPassword(email, code, newPassword) {
    const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        email,
        code,
        new_password: newPassword,
    }),
    });

    if (!res.ok) throw new Error((await res.json()).detail || "Failed to reset password");
    return res.json();
}