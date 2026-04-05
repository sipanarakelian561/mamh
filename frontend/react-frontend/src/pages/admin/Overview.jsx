import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

export default function AdminOverview() {
  const { token } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("teacher");
  const [password, setPassword] = useState("");
  const [lastPassword, setLastPassword] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [users, setUsers] = useState([]);
  const [listError, setListError] = useState("");
  const [listLoading, setListLoading] = useState(false);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const data = await apiFetch("/admin/users", {
        method: "POST",
        token,
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          role,
          password,
        }),
      });
      setResult(data);
      setLastPassword(password);
      await loadUsers();
      setFirstName("");
      setLastName("");
      setPassword("");
    } catch (err) {
      setError(err.message || "Failed to create user.");
    } finally {
      setLoading(false);
    }
  }

  async function loadUsers() {
    setListError("");
    setListLoading(true);
    try {
      const params = new URLSearchParams();
      if (search.trim()) params.set("q", search.trim());
      if (filterRole) params.set("role", filterRole);
      const data = await apiFetch(`/admin/users?${params.toString()}`, {
        method: "GET",
        token,
      });
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      setListError(err.message || "Failed to load users.");
    } finally {
      setListLoading(false);
    }
  }

  async function handleCopyCredentials() {
    if (!result?.email || !lastPassword) return;
    const text = `Email: ${result.email}\nPassword: ${lastPassword}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Ignore clipboard failures; user can manually copy.
    }
  }

  useEffect(() => {
    loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="max-w-3xl flex flex-col gap-8">
      <div>
        <h2 className="text-2xl font-bold">Create User</h2>
        <p className="text-sm text-gray-600">
          Admins generate emails automatically. Provide name, role, and password.
        </p>
      </div>

      <form onSubmit={handleCreate} className="flex flex-col gap-4">
        {error ? (
          <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        ) : null}

        {result ? (
          <div className="w-full p-3 rounded-xl border border-green-300 bg-green-50 text-green-800 text-sm">
            <div>
              Created: <span className="font-semibold">{result.email}</span> ({result.role})
            </div>
            <div className="mt-2 text-xs">
              Password set to: <span className="font-semibold">{lastPassword}</span>
            </div>
            <button
              type="button"
              onClick={handleCopyCredentials}
              className="mt-2 inline-flex rounded-lg px-3 py-2 text-sm font-semibold border border-green-300 hover:bg-green-200 transition"
            >
              Copy credentials
            </button>
          </div>
        ) : null}

        <div className="grid gap-3 sm:grid-cols-2">
          <input
            type="text"
            placeholder="First name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
          <option value="admin">Admin</option>
        </select>

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
        >
          {loading ? "Creating..." : "Generate Account"}
        </button>
      </form>

      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold">Existing Users</h3>
          <button
            type="button"
            onClick={loadUsers}
            className="rounded-lg px-3 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            {listLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <input
            type="text"
            placeholder="Search by email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">All roles</option>
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <button
          type="button"
          onClick={loadUsers}
          className="w-full sm:w-fit rounded-lg px-4 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
        >
          Search
        </button>

        {listError ? (
          <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
            {listError}
          </div>
        ) : null}

        <div className="rounded-2xl border overflow-hidden">
          <div className="grid grid-cols-4 bg-blue-50 text-blue-900 text-sm font-semibold px-4 py-3">
            <div>Email</div>
            <div>Role</div>
            <div>Admin</div>
            <div>Must Change Password</div>
          </div>
          <div className="divide-y">
            {users.length === 0 ? (
              <div className="px-4 py-4 text-sm text-gray-600">No users found.</div>
            ) : (
              users.map((u) => (
                <div key={u.id} className="grid grid-cols-4 px-4 py-3 text-sm">
                  <div className="truncate">{u.email}</div>
                  <div className="capitalize">{u.role}</div>
                  <div>{u.is_admin ? "Yes" : "No"}</div>
                  <div>{u.must_change_password ? "Yes" : "No"}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
